"""Identify JAXB origins in each original image's Spring test classloader.

A separate diagnostic container adds one isolated probe test. Production source
and dependency versions stay unchanged; this is not a repair or original count.
"""
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = '''import java.net.URL;
import java.util.Enumeration;
import org.junit.Test;
public class Case124ClassOriginsTest {
    @Test public void origins() throws Exception {
        ClassLoader loader = Case124ClassOriginsTest.class.getClassLoader();
        String[] resources = {
            "javax/xml/bind/JAXBException.class",
            "jakarta/xml/bind/JAXBException.class"
        };
        for (String path : resources) {
            Enumeration<URL> urls = loader.getResources(path);
            boolean found = false;
            while (urls.hasMoreElements()) {
                found = true;
                System.out.println("CASE124_RESOURCE " + path + "=" + urls.nextElement());
            }
            if (!found) System.out.println("CASE124_RESOURCE " + path + "=ABSENT");
        }
    }
}
'''

def main():
    base = ROOT / 'logs/case124_evidence'
    source = base / 'Case124ClassOriginsTest.java'
    if source.exists():
        if source.read_text() != SOURCE:
            raise ValueError('Existing diagnostic source differs; do not overwrite')
    else:
        with source.open('x', encoding='utf-8') as output:
            output.write(SOURCE)
    result = {'purpose': 'Class-origin diagnostic because original XML exposes only Maven launcher classpath', 'only_adjustment': 'Add and select one standalone diagnostic test in separate containers; original production source and dependency versions retained', 'runs': []}
    for phase in ('pre', 'breaking'):
        summary = json.loads((base / phase / 'archive_summary.json').read_text())
        name = 'research-case124-origins-' + phase
        command = ['docker', 'run', '--name', name, '--mount', 'type=bind,source=' + str(source) + ',target=' + summary['working_directory'] + '/camunda-bpm-camel-spring/src/test/java/Case124ClassOriginsTest.java,readonly', '--entrypoint', 'mvn', summary['image_id'], 'clean', 'test', '-B', '-pl', 'camunda-bpm-camel-spring', '-am', '-Dtest=Case124ClassOriginsTest', '-Dsurefire.failIfNoSpecifiedTests=false']
        log = base / f'class_origins_{phase}.log'
        if not log.exists():
            with log.open('x', encoding='utf-8') as output:
                subprocess.run(command, stdout=output, stderr=subprocess.STDOUT, timeout=240)
        info = json.loads(subprocess.check_output(['docker', 'inspect', name], text=True))[0]
        if info['State']['Status'] != 'exited' or info['Image'] != summary['image_id']:
            raise ValueError('Diagnostic container unfinished or wrong image')
        report_archive = base / f'class_origins_{phase}_reports.tar'
        if report_archive.exists():
            data = report_archive.read_bytes()
        else:
            data = subprocess.check_output(['docker', 'cp', name + ':' + summary['working_directory'] + '/camunda-bpm-camel-spring/target/surefire-reports/.', '-'])
            with report_archive.open('xb') as output:
                output.write(data)
        counts = dict.fromkeys(('tests', 'failures', 'errors', 'skipped'), 0)
        captured_output = []
        with tarfile.open(fileobj=io.BytesIO(data)) as archive:
            for member in archive:
                if member.isfile() and Path(member.name).name.startswith('TEST-') and member.name.endswith('.xml'):
                    xml = ET.fromstring(archive.extractfile(member).read())
                    for key in counts:
                        counts[key] += int(xml.get(key, '0'))
                elif member.isfile() and member.name.endswith('.txt'):
                    captured_output.append(archive.extractfile(member).read().decode(errors='replace'))
        text = log.read_text(errors='replace') + '\n' + '\n'.join(captured_output)
        origins = sorted(set(re.findall(r'^CASE124_RESOURCE (\S+)=(.+)$', text, re.M)))
        paths = sorted(set(re.findall(r'^jar:file:(.+\.jar)!/', value)[0] for _, value in origins if value.startswith('jar:file:')))
        exit_code = info['State']['ExitCode']
        entry = {'phase': phase, 'image_id': info['Image'], 'command': command, 'state': info['State'], 'exit_code': exit_code, 'counts': counts, 'output_source': 'Maven log plus fresh Surefire captured-output report files', 'resources': [{'resource': key, 'origin': value} for key, value in origins], 'resolved_bind_api_paths': paths}
        metadata = base / phase / 'class_origin_paths.json'
        if metadata.exists():
            previous = json.loads(metadata.read_text())
            if previous != entry:
                backup = metadata.with_name('class_origin_paths.before_report_output_parse.json')
                if backup.exists():
                    raise FileExistsError(backup)
                shutil.copy2(metadata, backup)
                metadata.write_text(json.dumps(entry, indent=2), encoding='utf-8')
        else:
            with metadata.open('x', encoding='utf-8') as output:
                json.dump(entry, output, indent=2)
        result['runs'].append(entry)
        print(phase, exit_code, counts, paths, flush=True)
        if exit_code != 0 or counts != {'tests': 1, 'failures': 0, 'errors': 0, 'skipped': 0} or len(paths) != 1:
            raise ValueError('Unexpected class-origin diagnostic; inspect before assessment')
    with (base / 'class_origins_results.json').open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2)

if __name__ == '__main__':
    main()
