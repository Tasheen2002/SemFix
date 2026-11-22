"""Seal original-image and diagnostic evidence for Cases 106-110."""
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]

def main():
    shared = ['scripts/archive_bump_evidence.py', 'scripts/batch_triage_test_failures.py', 'scripts/collect_cases_106_110_evidence.py', 'scripts/collect_cases_106_110_poms.py', 'scripts/inspect_resolved_case_jars.py', 'scripts/validate_cases_106_110.py', 'scripts/seal_cases_106_110_evidence.py']
    helpers = {106: ['scripts/collect_case_106_runner_evidence.py'], 107: [], 108: ['scripts/diagnose_case_108_connection.py'], 109: ['scripts/probe_case_109_annotation_compatibility.py'], 110: []}
    for n in range(106, 111):
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
