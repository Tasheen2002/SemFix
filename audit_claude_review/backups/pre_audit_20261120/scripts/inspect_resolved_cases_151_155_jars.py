"""Inspect selected artifacts from original retained-container test classpaths.

This collects evidence only; it does not assign semantic classifications.
Existing JARs, inspection JSON and disassembly files are never overwritten.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
JAVAP = 'C:/Program Files/Java/jdk-21.0.11/bin/javap.exe'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case-number', type=int, required=True)
    parser.add_argument('--filter', required=True, help='Regex selecting resolved JAR paths')
    parser.add_argument('--probe-class', action='append', default=[])
    parser.add_argument('--javap-class', action='append', default=[])
    parser.add_argument('--module', help='Use test reports from this Maven module only')
    parser.add_argument('--output-name', default='jar_inspection.json', choices=['jar_inspection.json', 'mock_common_inspection.json'])
    args = parser.parse_args()
    if not 151 <= args.case_number <= 155:
        raise ValueError('This collection is scoped to Cases 151-155')
    base = ROOT / f'logs/case{args.case_number}_evidence'
    for phase in ('pre', 'breaking'):
        summary = json.loads((base / phase / 'archive_summary.json').read_text())
        container = 'bump-' + summary['case_id'] + '-' + phase
        info = json.loads(subprocess.check_output(['docker', 'inspect', container], text=True))[0]
        if info['State']['Status'] != 'exited' or info['Image'] != summary['image_id']:
            raise ValueError('Expected the original stopped container')
        reports = [r for r in summary['reports'] if args.module is None or r['module'] == args.module]
        paths = set().union(*(set(r['classpath'].split(':')) for r in reports))
        source = 'Fresh original test report classpaths'
        paths = sorted(p for p in paths if p.endswith('.jar') and re.search(args.filter, p))
        if not paths:
            raise ValueError(f'No matching artifacts for {phase}')
        records = []
        for path in paths:
            data = subprocess.check_output(['docker', 'cp', container + ':' + path, '-'])
            with tarfile.open(fileobj=io.BytesIO(data)) as archive:
                files = [m for m in archive if m.isfile()]
                if len(files) != 1:
                    raise ValueError('Expected exactly one JAR')
                data = archive.extractfile(files[0]).read()
            dest = base / phase / 'jars' / Path(path).name
            dest.parent.mkdir(exist_ok=True)
            if dest.exists():
                if dest.read_bytes() != data:
                    raise ValueError('Existing archived JAR differs: ' + str(dest))
            else:
                with dest.open('xb') as output:
                    output.write(data)
            record = {'resolved_path': path, 'sha256': hashlib.sha256(data).hexdigest(), 'classes': {}, 'services': {}, 'disassemblies': []}
            with zipfile.ZipFile(io.BytesIO(data)) as jar:
                names = set(jar.namelist())
                for clazz in args.probe_class:
                    name = clazz.replace('.', '/') + '.class'
                    content = jar.read(name) if name in names else None
                    record['classes'][clazz] = {'present': content is not None, 'major_version': int.from_bytes(content[6:8], 'big') if content else None}
                record['services'] = {name: jar.read(name).decode(errors='replace') for name in sorted(names) if name.startswith('META-INF/services/') and not name.endswith('/')}
                for clazz in args.javap_class:
                    if clazz.replace('.', '/') + '.class' not in names:
                        continue
                    command = [JAVAP, '-classpath', str(dest), '-p', '-s', '-c', clazz]
                    result = subprocess.run(command, capture_output=True, text=True)
                    if result.returncode:
                        raise RuntimeError(result.stderr)
                    name = dest.stem + '_' + clazz.rsplit('.', 1)[-1] + '_javap.txt'
                    disassembly = base / phase / name
                    if disassembly.exists():
                        if disassembly.read_text(encoding='utf-8') != result.stdout:
                            raise ValueError('Existing disassembly differs')
                    else:
                        with disassembly.open('x', encoding='utf-8') as output:
                            output.write(result.stdout)
                    record['disassemblies'].append({'class': clazz, 'file': name, 'command': command, 'exit_code': result.returncode})
            records.append(record)
            print(args.case_number, phase, dest.name, record['classes'], flush=True)
        result = {'case_id': summary['case_id'], 'phase': phase, 'path_filter': args.filter, 'path_source': source, 'artifacts': records}
        inspection_name = args.output_name
        with (base / phase / inspection_name).open('x', encoding='utf-8') as output:
            json.dump(result, output, indent=2)

if __name__ == '__main__':
    main()
