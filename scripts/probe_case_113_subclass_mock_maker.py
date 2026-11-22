"""Rerun the two failing tracing tests with Mockito 5.1.0 and subclass mocking.

This diagnostic changes only a test-resource MockMaker selection in a separate
container. It is not a verified client repair or a full-reactor validation.
"""
import io
import json
from pathlib import Path
import subprocess
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

def main():
    base = ROOT / 'logs/case113_evidence'
    summary = json.loads((base / 'breaking/archive_summary.json').read_text())
    if any(p.endswith('mockito-extensions/org.mockito.plugins.MockMaker') for p in summary['source_and_pom_sha256']):
        raise ValueError('Original project already selects a MockMaker; inspect before proceeding')
    shell = "set -eu; mkdir -p gax/src/test/resources/mockito-extensions; printf '%s\\n' mock-maker-subclass > gax/src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker; cat gax/src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker; exec mvn clean test -B -pl gax -am -Dtest=OpencensusTracerFactoryTest#testImplicitParentSpan,OpencensusTracerTest#testLongRunningExample -Dsurefire.failIfNoSpecifiedTests=false"
    name = 'research-case113-subclass-control'
    command = ['docker', 'run', '--name', name, '--entrypoint', 'sh', summary['image_id'], '-c', shell]
    with (base / 'subclass_control.log').open('x', encoding='utf-8') as output:
        run = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT, text=True, timeout=240)
    info = json.loads(subprocess.check_output(['docker', 'inspect', name], text=True))[0]
    if info['State']['Status'] != 'exited':
        raise ValueError('Diagnostic container unfinished')
    data = subprocess.check_output(['docker', 'cp', name + ':' + summary['working_directory'] + '/gax/target/surefire-reports/.', '-'])
    with (base / 'subclass_control_reports.tar').open('xb') as output:
        output.write(data)
    counts = {'tests': 0, 'failures': 0, 'errors': 0, 'skipped': 0}
    reports = []
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        for member in archive:
            if not member.isfile() or not Path(member.name).name.startswith('TEST-') or not member.name.endswith('.xml'):
                continue
            xml = ET.fromstring(archive.extractfile(member).read())
            props = {p.get('name'): p.get('value') for p in xml.findall('properties/property')}
            reports.append({'path': member.name, 'class': xml.get('name'), 'classpath': props.get('java.class.path', '')})
            for key in counts:
                counts[key] += int(xml.get(key, '0'))
    result = {'purpose': 'Isolate the changed mock-maker default; not a full repair', 'only_adjustment': 'Add mock-maker-subclass test-resource selection; upgraded Mockito and transitive Byte Buddy are retained', 'command': command, 'image_id': info['Image'], 'state': info['State'], 'counts': counts, 'reports': reports, 'exit_code': run.returncode}
    with (base / 'subclass_control_results.json').open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2)
    print('Control exit:', run.returncode, 'counts:', counts)
    if run.returncode != 0 or counts != {'tests': 2, 'failures': 0, 'errors': 0, 'skipped': 0} or not all('/mockito-core/5.1.0/' in r['classpath'] for r in reports):
        raise ValueError('Unexpected diagnostic result; inspect before assessment')

if __name__ == '__main__':
    main()
