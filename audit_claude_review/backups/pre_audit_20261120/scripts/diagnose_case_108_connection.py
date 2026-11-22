"""Rerun Case 108's connection test with SSHD trace logging only.

Original image, client source and dependency versions are retained. The diagnostic
container is retained until its fresh reports have been archived and validated.
"""
import io
import json
from pathlib import Path
import subprocess
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

def main():
    base = ROOT / 'logs/case108_evidence'
    summary = json.loads((base / 'breaking/archive_summary.json').read_text())
    with tarfile.open(base / 'breaking/artifacts.tar') as archive:
        config = archive.extractfile('src/test/resources/log4j.properties').read()
    configuration = base / 'connection_debug_log4j.properties'
    with configuration.open('xb') as output:
        output.write(config + b'\nlog4j.logger.org.apache.sshd=TRACE\n')
    name = 'research-case108-connection-debug'
    command = ['docker', 'run', '--name', name, '--mount', 'type=bind,source=' + str(configuration) + ',target=/tmp/connection-debug-log4j.properties,readonly', '--entrypoint', 'mvn', summary['image_id'], 'clean', 'test', '-B', '-Dtest=SshByPasswordTest', '-Dlog4j.configuration=file:/tmp/connection-debug-log4j.properties']
    with (base / 'connection_debug.log').open('x', encoding='utf-8') as output:
        run = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT, text=True, timeout=180)
    info = json.loads(subprocess.check_output(['docker', 'inspect', name], text=True))[0]
    if info['State']['Status'] != 'exited':
        raise ValueError('Diagnostic container unfinished')
    data = subprocess.check_output(['docker', 'cp', name + ':' + summary['working_directory'] + '/target/surefire-reports/.', '-'])
    with (base / 'connection_debug_reports.tar').open('xb') as output:
        output.write(data)
    counts = {'tests': 0, 'failures': 0, 'errors': 0, 'skipped': 0}
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        for member in archive:
            if member.isfile() and Path(member.name).name.startswith('TEST-') and member.name.endswith('.xml'):
                xml = ET.fromstring(archive.extractfile(member).read())
                for key in counts:
                    counts[key] += int(xml.get(key, '0'))
    result = {'purpose': 'Isolate the original connection-reset error with additional server-side logging', 'only_adjustment': 'SSHD trace logging via external Log4j configuration; no client source/dependency version changes', 'command': command, 'image_id': info['Image'], 'state': info['State'], 'counts': counts, 'exit_code': run.returncode}
    with (base / 'connection_debug_results.json').open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
