"""Seal original-image and diagnostic evidence for Cases 131-135."""
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]

def main():
    shared = ['scripts/archive_case_121_125.py', 'scripts/batch_triage_test_failures.py', 'scripts/collect_cases_131_135_evidence.py', 'scripts/collect_cases_131_135_poms.py', 'scripts/inspect_resolved_cases_131_135_jars.py', 'scripts/validate_cases_131_135.py', 'scripts/seal_cases_131_135_evidence.py']
    helpers = {
        131: ['scripts/collect_case_131_runner_evidence.py'],
        132: ['scripts/probe_cases_132_134_logger.py'],
        133: [],
        134: ['scripts/probe_cases_132_134_logger.py'],
        135: ['scripts/diagnose_case_135_class_origins.py'],
    }
    for n in range(131, 136):
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
