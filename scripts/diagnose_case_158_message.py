"""Run one isolated message/origin probe in each original image; not a repair."""
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
from urllib.parse import unquote, urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = '''import org.junit.Test;
import org.apache.http.client.HttpResponseException;
import org.apache.http.HttpResponse;
import com.github.sardine.impl.SardineException;
public class Case158MessageProbeTest {
    @Test public void messageAndOrigins() {
        System.out.println("CASE158_ORIGIN httpclient=" + HttpResponseException.class.getProtectionDomain().getCodeSource().getLocation());
        System.out.println("CASE158_ORIGIN httpcore=" + HttpResponse.class.getProtectionDomain().getCodeSource().getLocation());
        System.out.println("CASE158_PARENT " + new HttpResponseException(400, "m").getMessage());
        System.out.println("CASE158_CLIENT " + new SardineException("m", 400, "response phrase").getMessage());
    }
}
'''

def main():
    base = ROOT / 'logs/case158_evidence'
    source = base / 'Case158MessageProbeTest.java'
    with source.open('x') as stream:
        stream.write(SOURCE)
    runs = []
    for phase in ('pre', 'breaking'):
        summary = json.loads((base / phase / 'archive_summary.json').read_text())
        name = 'research-case158-message-' + phase
        command = ['docker', 'run', '--name', name, '--mount',
                   f'type=bind,source={source},target={summary["working_directory"]}/src/test/java/Case158MessageProbeTest.java,readonly',
                   '--entrypoint', 'mvn', summary['image_id'], 'clean', 'test', '-B', '-Dtest=Case158MessageProbeTest']
        log = base / f'message_probe_{phase}.log'
        with log.open('x', encoding='utf-8') as stream:
            run = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, timeout=300)
        info = json.loads(subprocess.check_output(['docker', 'inspect', name], text=True))[0]
        data = subprocess.check_output(['docker', 'cp', name + ':' + summary['working_directory'] + '/target/surefire-reports/.', '-'])
        with (base / f'message_probe_{phase}_reports.tar').open('xb') as stream:
            stream.write(data)
        text = log.read_text(encoding='utf-8', errors='replace')
        counts = dict.fromkeys(('tests', 'failures', 'errors', 'skipped'), 0)
        with tarfile.open(fileobj=io.BytesIO(data)) as archive:
            for member in archive:
                if not member.isfile():
                    continue
                content = archive.extractfile(member).read().decode(errors='replace')
                if member.name.endswith('.txt'):
                    text += '\n' + content
                if Path(member.name).name.startswith('TEST-') and member.name.endswith('.xml'):
                    xml = ET.fromstring(content)
                    for key in counts:
                        counts[key] += int(xml.get(key, '0'))
                    for output in xml.findall('.//system-out'):
                        text += '\n' + (output.text or '')
        origins = dict(re.findall(r'^CASE158_ORIGIN (\w+)=(\S+)', text, re.M))
        paths = sorted(unquote(urlparse(url).path) for url in origins.values())
        messages = {key: sorted(set(re.findall(r'^CASE158_' + key.upper() + r' (.+)$', text, re.M))) for key in ('parent', 'client')}
        entry = {'phase': phase, 'image_id': info['Image'], 'container_name': name, 'state': info['State'],
                 'command': command, 'exit_code': run.returncode, 'counts': counts, 'origins': origins,
                 'resolved_http_paths': paths, 'messages': messages}
        with (base / phase / 'message_origin_paths.json').open('x') as stream:
            json.dump(entry, stream, indent=2)
        assert run.returncode == 0 and info['Image'] == summary['image_id']
        assert counts == {'tests': 1, 'failures': 0, 'errors': 0, 'skipped': 0} and len(paths) == 2
        prefix = '' if phase == 'pre' else 'status code: 400, reason phrase: '
        assert messages == {'parent': [prefix + 'm'], 'client': [prefix + 'm (400 response phrase)']}
        runs.append(entry)
        print(phase, counts, origins, messages, flush=True)
    with (base / 'message_probe_results.json').open('x') as stream:
        json.dump({'purpose': 'Separate diagnostic: add and select one test; original production source and dependency versions retained', 'runs': runs}, stream, indent=2)

if __name__ == '__main__':
    main()
