"""Identify Jackson origins in each original image's messaging test classloader.

A separate diagnostic container adds one isolated probe test. Production source
and dependency versions stay unchanged; this is not a repair or original count.
"""
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = '''import java.net.URL;
import java.util.Enumeration;
import org.junit.jupiter.api.Test;
public class Case135ClassOriginsTest {
    @Test public void origins() throws Exception {
        ClassLoader loader = Case135ClassOriginsTest.class.getClassLoader();
        String[] resources = {
            "com/fasterxml/jackson/databind/ObjectMapper.class",
            "com/fasterxml/jackson/core/JsonFactory.class",
            "com/fasterxml/jackson/annotation/JsonProperty.class",
            "com/fasterxml/jackson/annotation/JsonKey.class"
        };
        for (String path : resources) {
            Enumeration<URL> urls = loader.getResources(path);
            boolean found = false;
            while (urls.hasMoreElements()) {
                found = true;
                System.out.println("CASE135_RESOURCE " + path + "=" + urls.nextElement());
            }
            if (!found) System.out.println("CASE135_RESOURCE " + path + "=ABSENT");
        }
    }
}
'''

def main():
    base = ROOT / 'logs/case135_evidence'
    source = base / 'Case135ClassOriginsTest.java'
    with source.open('x', encoding='utf-8') as output:
        output.write(SOURCE)
    result = {'purpose': 'Class-origin diagnostic because original XML exposes only Maven launcher classpath', 'only_adjustment': 'Add and select one standalone diagnostic test in separate containers; original production source and dependency versions retained', 'runs': []}
    for phase in ('pre', 'breaking'):
        summary = json.loads((base / phase / 'archive_summary.json').read_text())
        name = 'research-case135-origins-' + phase
        command = ['docker', 'run', '--name', name, '--mount', 'type=bind,source=' + str(source) + ',target=' + summary['working_directory'] + '/messaging/src/test/java/Case135ClassOriginsTest.java,readonly', '--entrypoint', 'mvn', summary['image_id'], 'clean', 'test', '-B', '-pl', 'messaging', '-am', '-Dtest=Case135ClassOriginsTest', '-Dsurefire.failIfNoSpecifiedTests=false']
        log = base / f'class_origins_{phase}.log'
        with log.open('x', encoding='utf-8') as output:
            run = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT, timeout=240)
        info = json.loads(subprocess.check_output(['docker', 'inspect', name], text=True))[0]
        data = subprocess.check_output(['docker', 'cp', name + ':' + summary['working_directory'] + '/messaging/target/surefire-reports/.', '-'])
        with (base / f'class_origins_{phase}_reports.tar').open('xb') as output:
            output.write(data)
        counts = dict.fromkeys(('tests', 'failures', 'errors', 'skipped'), 0)
        with tarfile.open(fileobj=io.BytesIO(data)) as archive:
            for member in archive:
                if member.isfile() and Path(member.name).name.startswith('TEST-') and member.name.endswith('.xml'):
                    xml = ET.fromstring(archive.extractfile(member).read())
                    for key in counts:
                        counts[key] += int(xml.get(key, '0'))
        text = log.read_text(errors='replace')
        origins = re.findall(r'^CASE135_RESOURCE (\S+)=(.+)$', text, re.M)
        paths = sorted(set(re.findall(r'^jar:file:(.+\.jar)!/', value)[0] for _, value in origins if value.startswith('jar:file:')))
        entry = {'phase': phase, 'image_id': info['Image'], 'command': command, 'state': info['State'], 'exit_code': run.returncode, 'counts': counts, 'resources': [{'resource': key, 'origin': value} for key, value in origins], 'resolved_jackson_paths': paths}
        with (base / phase / 'class_origin_paths.json').open('x', encoding='utf-8') as output:
            json.dump(entry, output, indent=2)
        result['runs'].append(entry)
        print(phase, run.returncode, counts, paths, flush=True)
        if run.returncode != 0 or counts != {'tests': 1, 'failures': 0, 'errors': 0, 'skipped': 0} or len(paths) != 3:
            raise ValueError('Unexpected class-origin diagnostic; inspect before assessment')
    with (base / 'class_origins_results.json').open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2)

if __name__ == '__main__':
    main()
