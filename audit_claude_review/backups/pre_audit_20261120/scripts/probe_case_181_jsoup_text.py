"""Replay the unchanged client text call against both archived jsoup JARs."""
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'logs/case181_evidence'
JAVA = Path('C:/Program Files/Java/jdk-21.0.11/bin')
FIXTURE = 'sparql-anything-html/src/test/resources/Microdata1.html'
SOURCE = """import java.io.File;
import org.jsoup.Jsoup;
public class JsoupTextProbe {
    public static void main(String[] arguments) throws Exception {
        var document = Jsoup.parse(new File(arguments[0]), "UTF-8");
        for (String name : new String[]{"html", "body", "div", "h1", "span"}) {
            System.out.println(name + ".text=" + document.selectFirst(name).select("*").text());
            System.out.println(name + ".html=" + document.selectFirst(name).html().replace("\\n", "|"));
        }
    }
}
"""

def main():
    directory = BASE / 'html_probe_by_element'
    directory.mkdir()
    source = directory / 'JsoupTextProbe.java'
    source.write_text(SOURCE)
    samples = []
    for phase in ('pre', 'breaking'):
        with tarfile.open(BASE / phase / 'artifacts.tar') as archive:
            samples.append(archive.extractfile(FIXTURE).read())
    assert samples[0] == samples[1]
    fixture = directory / 'Microdata1.html'
    fixture.write_bytes(samples[0])
    jars = [next((BASE / phase / 'jars').glob('jsoup-*.jar')) for phase in ('pre','breaking')]
    subprocess.run([str(JAVA/'javac.exe'), '--release', '11', '-cp', str(jars[0]), str(source)], check=True)
    classfile = directory / 'JsoupTextProbe.class'
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()
    runs = []
    for phase, jar in zip(('pre','breaking'), jars):
        image = json.loads((BASE / phase / 'archive_summary.json').read_text())['image_id']
        command = ['docker', 'run', '--rm', '--network', 'none',
                   '--mount', f'type=bind,source={directory},target=/probe,readonly',
                   '--mount', f'type=bind,source={jar},target=/jsoup.jar,readonly',
                   '--entrypoint', 'java', image, '-cp', '/probe:/jsoup.jar', 'JsoupTextProbe', '/probe/Microdata1.html']
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=90)
        runs.append({'phase': phase, 'image_id': image, 'jar_sha256': digest(jar), 'command': command, 'output': result.stdout.strip()})
    output = {'fixture_sha256': digest(fixture), 'class_sha256': digest(classfile), 'runs': runs}
    (directory / 'results.json').write_text(json.dumps(output, indent=2))
    print([r['output'] for r in runs])

if __name__ == '__main__':
    main()
