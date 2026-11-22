"""Seal original-image and diagnostic evidence for Cases 116-120."""
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]

def main():
    shared = ['scripts/archive_case_116_120.py', 'scripts/batch_triage_test_failures.py', 'scripts/collect_cases_116_120_evidence.py', 'scripts/collect_cases_116_120_poms.py', 'scripts/inspect_resolved_cases_116_120_jars.py', 'scripts/validate_cases_116_120.py', 'scripts/seal_cases_116_120_evidence.py']
    helpers = {116: ['scripts/diagnose_case_116_test_discovery.py', 'scripts/collect_case_116_discovery_classpaths.py'], 117: ['scripts/probe_case_117_logger_selection.py'], 118: [], 119: [], 120: []}
    for n in range(116, 121):
        base = ROOT / f'logs/case{n}_evidence'
        files = [p for p in base.rglob('*') if p.is_file() and p.name != 'sha256_manifest.json']
        record = runpy.run_path(str(ROOT / f'scripts/append_case_{n}.py'))['RECORD']
        files.extend(ROOT / p for p in shared + helpers[n] + [f'scripts/append_case_{n}.py', f'results/case{n}_review.md', record['pre_log'], record['breaking_log']])
        manifest = {}
        for path in sorted(set(files)):
            with path.open('rb') as stream:
                manifest[path.relative_to(ROOT).as_posix()] = hashlib.file_digest(stream, 'sha256').hexdigest()
        with (base / 'sha256_manifest.json').open('x', encoding='utf-8') as output:
            json.dump(manifest, output, indent=2)
        print(n, 'hashed files:', len(manifest))

if __name__ == '__main__':
    main()
