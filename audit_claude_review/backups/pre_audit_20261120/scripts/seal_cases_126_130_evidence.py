"""Seal original-image and diagnostic evidence for Cases 126-130."""
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]

def main():
    shared = ['scripts/archive_case_121_125.py', 'scripts/batch_triage_test_failures.py', 'scripts/collect_cases_126_130_evidence.py', 'scripts/collect_cases_126_130_poms.py', 'scripts/inspect_resolved_cases_126_130_jars.py', 'scripts/validate_cases_126_130.py', 'scripts/seal_cases_126_130_evidence.py']
    helpers = {126: [], 127: ['scripts/probe_case_127_lexer_compatibility.py'], 128: ['scripts/diagnose_case_128_class_origins.py'], 129: ['scripts/probe_case_129_logger.py'], 130: []}
    for n in range(126, 131):
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
