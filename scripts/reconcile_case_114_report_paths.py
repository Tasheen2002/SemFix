"""Normalize a legacy PAX './' path alias without changing original archives."""
import json
from pathlib import Path, PurePosixPath
import shutil
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

def main():
    base = ROOT / 'logs/case114_evidence'
    phases = {}
    for phase in ('pre', 'breaking'):
        directory = base / phase
        summary = json.loads((directory / 'archive_summary.json').read_text())
        expected = {r['path'] for r in summary['reports']}
        collected, aliases = [], []
        with tarfile.open(directory / 'artifacts.tar') as archive:
            for member in archive:
                normalized = PurePosixPath(member.name).as_posix()
                if normalized not in expected:
                    continue
                xml = ET.fromstring(archive.extractfile(member).read())
                props = {p.get('name'): p.get('value') for p in xml.findall('properties/property')}
                key = 'surefire.test.class.path' if props.get('surefire.test.class.path') else 'java.class.path'
                collected.append({'report': normalized, 'property': key, 'classpath': props.get(key, '')})
                if member.name != normalized:
                    aliases.append({'archive_path': member.name, 'normalized_path': normalized})
        if len(collected) != summary['report_count'] or {r['report'] for r in collected} != expected:
            raise ValueError('Not all fresh reports were reconciled')
        path = directory / 'resolved_test_classpaths.json'
        previous = json.loads(path.read_text())
        if previous != collected:
            backup = directory / 'resolved_test_classpaths.before_path_normalization.json'
            if backup.exists():
                raise FileExistsError(backup)
            shutil.copy2(path, backup)
            path.write_text(json.dumps(collected, indent=2), encoding='utf-8')
        phases[phase] = {'report_count': len(collected), 'normalized_aliases': aliases, 'original_archive_unchanged': True, 'previous_extraction_preserved_if_changed': True}
        print(phase, len(collected), 'reports; normalized aliases:', len(aliases))
    with (base / 'report_path_normalization.json').open('x', encoding='utf-8') as output:
        json.dump(phases, output, indent=2)

if __name__ == '__main__':
    main()
