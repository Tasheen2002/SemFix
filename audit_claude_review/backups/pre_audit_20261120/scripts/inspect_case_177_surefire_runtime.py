"""Inspect the plugin realm printed by the original Case 177 failure.

The failed provider starts no messaging-module tests, so no BREAKING report from that module exists.
These paths come directly from Maven's original error report, not project XML.
"""
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
    base = ROOT / 'logs/case177_evidence'
    summary = json.loads((base / 'breaking/archive_summary.json').read_text())
    log = ROOT / f"logs/batch_triage/{summary['case_id'][:8]}_breaking.log"
    urls = []
    for n, line in enumerate(log.read_text(errors='replace').splitlines(), 1):
        match = re.fullmatch(r'\[ERROR\] urls\[(\d+)\] = file:(.+\.jar)', line)
        if match:
            urls.append({'index': int(match[1]), 'path': match[2], 'log_line': n})
    if [u['index'] for u in urls] != list(range(len(urls))) or not urls:
        raise ValueError('Original plugin realm URLs missing or noncontiguous')
    name = 'bump-' + summary['case_id'] + '-breaking'
    info = json.loads(subprocess.check_output(['docker', 'inspect', name], text=True))[0]
    if info['State']['Status'] != 'exited' or info['Image'] != summary['image_id']:
        raise ValueError('Expected original stopped BREAKING container')
    records = []
    for item in urls:
        path = item['path']
        if not re.search(r'/(common-java5|maven-surefire-common|maven-surefire-plugin|surefire-booter|junit-platform-surefire-provider)/', path):
            continue
        raw = subprocess.check_output(['docker', 'cp', name + ':' + path, '-'])
        with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
            files = [m for m in archive if m.isfile()]
            if len(files) != 1:
                raise ValueError('Expected one runtime artifact')
            data = archive.extractfile(files[0]).read()
        dest = base / 'breaking/jars' / Path(path).name
        dest.parent.mkdir(exist_ok=True)
        with dest.open('xb') as output:
            output.write(data)
        record = {'resolved_path': path, 'sha256': hashlib.sha256(data).hexdigest(), 'disassemblies': [], 'confirmed_requireNonNull_callers': []}
        with zipfile.ZipFile(io.BytesIO(data)) as jar:
            candidates = [entry[:-6].replace('/', '.') for entry in jar.namelist() if entry.endswith('.class') and b'org/apache/maven/surefire/util/internal/StringUtils' in jar.read(entry) and b'requireNonNull' in jar.read(entry)]
        if '/common-java5/' in path:
            candidates.append('org.apache.maven.surefire.util.internal.StringUtils')
        for clazz in sorted(set(candidates)):
            command = [JAVAP, '-classpath', str(dest), '-p', '-s', '-c', clazz]
            run = subprocess.run(command, capture_output=True, text=True)
            if run.returncode:
                raise RuntimeError(run.stderr)
            caller = 'org/apache/maven/surefire/util/internal/StringUtils.requireNonNull:' in run.stdout
            if clazz.endswith('.StringUtils') or caller:
                filename = dest.stem + '_' + clazz.rsplit('.', 1)[-1] + '_javap.txt'
                with (base / 'breaking' / filename).open('x', encoding='utf-8') as output:
                    output.write(run.stdout)
                record['disassemblies'].append({'class': clazz, 'file': filename, 'command': command, 'exit_code': run.returncode})
            if caller:
                record['confirmed_requireNonNull_callers'].append(clazz)
        records.append(record)
        print(dest.name, 'confirmed callers:', record['confirmed_requireNonNull_callers'], flush=True)
    result = {'case_id': summary['case_id'], 'phase': 'breaking', 'image_id': summary['image_id'], 'path_source': 'Original Maven failure plugin realm URLs; successful PRE project XML does not expose this plugin realm', 'plugin_urls': urls, 'artifacts': records}
    with (base / 'plugin_runtime_inspection.json').open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2)

if __name__ == '__main__':
    main()
