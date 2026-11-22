"""Inspect the actual JAXB artifacts resolved in the two original image pairs.

Run after archiving both phases. Outputs are exclusive; existing evidence is kept.
"""
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    candidates = list(csv.DictReader((ROOT / 'results/test_failure_candidates.csv').open(encoding='utf-8-sig', newline='')))
    probes = ('javax/xml/bind/JAXBException.class', 'jakarta/xml/bind/JAXBException.class',
              'javax/xml/bind/JAXBContext.class', 'jakarta/xml/bind/JAXBContext.class',
              'com/sun/xml/bind/v2/ContextFactory.class',
              'com/sun/xml/internal/bind/v2/ContextFactory.class',
              'org/glassfish/jaxb/runtime/v2/ContextFactory.class')
    for n in (101, 102):
        base = ROOT / f'logs/case{n}_evidence'
        results = []
        for phase in ('pre', 'breaking'):
            summary = json.loads((base / phase / 'archive_summary.json').read_text())
            classpath = set().union(*(set(r['classpath'].split(':')) for r in summary['reports']))
            paths = sorted(p for p in classpath if p.endswith('.jar') and ('/jaxb-' in p or '/jakarta.xml.bind-api/' in p))
            for path in paths:
                container = 'bump-' + candidates[n-1]['case_id'] + '-' + phase
                data = subprocess.check_output(['docker', 'cp', container + ':' + path, '-'])
                with tarfile.open(fileobj=io.BytesIO(data)) as archive:
                    members = [m for m in archive if m.isfile()]
                    if len(members) != 1:
                        raise ValueError('Expected one JAR')
                    data = archive.extractfile(members[0]).read()
                out = base / phase / 'jars' / Path(path).name
                out.parent.mkdir(exist_ok=True)
                with out.open('xb') as stream:
                    stream.write(data)
                with zipfile.ZipFile(io.BytesIO(data)) as jar:
                    names = set(jar.namelist())
                    services = {name: jar.read(name).decode('utf-8', errors='replace') for name in sorted(names) if name.startswith('META-INF/services/') and not name.endswith('/')}
                    results.append({'phase': phase, 'resolved_path': path, 'sha256': hashlib.sha256(data).hexdigest(), 'classes': {p: p in names for p in probes}, 'services': services})
        with (base / 'resolved_jar_inspection.json').open('x', encoding='utf-8') as output:
            json.dump(results, output, indent=2)
        print(n, json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
