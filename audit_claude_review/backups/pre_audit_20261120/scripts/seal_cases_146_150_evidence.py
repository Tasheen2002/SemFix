"""Seal original-image and diagnostic evidence for Cases 146-150."""
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]

def main():
    shared = ['scripts/archive_case_121_125.py', 'scripts/batch_triage_test_failures.py', 'scripts/collect_cases_146_150_evidence.py', 'scripts/collect_cases_146_150_poms.py', 'scripts/inspect_resolved_cases_146_150_jars.py', 'scripts/validate_cases_146_150.py', 'scripts/seal_cases_146_150_evidence.py']
    reconcile = 'scripts/reconcile_cases_146_150_reports.py'
    helpers = {146: [], 147: ['scripts/probe_cases_147_150_logger.py'], 148: ['scripts/probe_cases_147_150_logger.py'], 149: ['scripts/reconcile_case_149_reports.py'], 150: ['scripts/probe_cases_147_150_logger.py']}
    for n in range(146, 151):
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
