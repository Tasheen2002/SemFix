"""Inspect the Log4j artifacts on Case 105's failing Spring Boot test classpath."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    base = ROOT / 'logs/case105_evidence'
    records = []
    probe = 'org/apache/logging/log4j/spi/LoggerContextShutdownAware.class'
    for phase in ('pre', 'breaking'):
        summary = json.loads((base / phase / 'archive_summary.json').read_text())
        reports = [r for r in summary['reports'] if r['module'] == 'spring/junit4-spring-boot-test']
        paths = sorted(set().union(*(set(r['classpath'].split(':')) for r in reports)))
        paths = [p for p in paths if '/org/apache/logging/log4j/' in p and p.endswith('.jar')]
        for path in paths:
            container = 'bump-' + summary['case_id'] + '-' + phase
            data = subprocess.check_output(['docker', 'cp', container + ':' + path, '-'])
            with tarfile.open(fileobj=io.BytesIO(data)) as archive:
                members = [m for m in archive if m.isfile()]
                if len(members) != 1:
                    raise ValueError('Expected one artifact')
                data = archive.extractfile(members[0]).read()
            destination = base / phase / Path(path).name
            with destination.open('xb') as output:
                output.write(data)
            with zipfile.ZipFile(io.BytesIO(data)) as jar:
                refs = [p for p in jar.namelist() if p.endswith('.class') and probe[:-6].encode() in jar.read(p)]
                record = {'phase': phase, 'resolved_path': path, 'sha256': hashlib.sha256(data).hexdigest(), 'contains_LoggerContextShutdownAware': probe in jar.namelist(), 'classes_referencing_type': refs}
            if '/log4j-core/' in path:
                command = ['C:/Program Files/Java/jdk-21.0.11/bin/javap.exe', '-classpath', str(destination), '-p', '-s', 'org.apache.logging.log4j.core.selector.ClassLoaderContextSelector']
                result = subprocess.run(command, capture_output=True, text=True)
                if result.returncode:
                    raise RuntimeError(result.stderr)
                with (base / f'{phase}_ClassLoaderContextSelector_javap.txt').open('x', encoding='utf-8') as output:
                    output.write(result.stdout)
                record['javap_command'] = command
            records.append(record)
    with (base / 'resolved_jar_inspection.json').open('x', encoding='utf-8') as output:
        json.dump(records, output, indent=2)
    print(json.dumps(records, indent=2))

if __name__ == '__main__':
    main()
