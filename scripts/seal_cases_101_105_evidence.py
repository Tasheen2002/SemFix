"""Write exclusive SHA-256 manifests after completing Cases 101-105 evidence."""
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]

def main():
    shared = ['scripts/archive_bump_evidence.py', 'scripts/batch_triage_test_failures.py', 'scripts/collect_cases_101_105_poms.py', 'scripts/validate_cases_101_105.py', 'scripts/seal_cases_101_105_evidence.py']
    helpers = {101: ['scripts/inspect_cases_101_102_jars.py'], 102: ['scripts/inspect_cases_101_102_jars.py'], 103: ['scripts/collect_case_103_runner_evidence.py', 'scripts/inspect_cases_103_104_jars.py'], 104: ['scripts/inspect_cases_103_104_jars.py'], 105: ['scripts/reconcile_case_105_reports.py', 'scripts/inspect_case_105_jars.py']}
    for n in range(101, 106):
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
