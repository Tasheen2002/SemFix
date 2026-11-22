"""Seal original-image and diagnostic evidence for Cases 161-188."""
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]

def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--through', type=int, choices=range(161, 189), default=188)
    end = parser.parse_args().through
    shared = ['scripts/archive_case_121_125.py', 'scripts/batch_triage_test_failures.py',
              'scripts/reconcile_cases_161_188_reports.py']
    helpers = {
        161: ['scripts/inspect_case_161_fixture_provenance.py'],
        168: ['scripts/diagnose_case_168_scheduler.py'],
        170: ['scripts/diagnose_case_170_class_origins.py'],
        171: ['scripts/probe_cases_171_186_logger.py'],
        177: ['scripts/inspect_case_177_surefire_runtime.py'],
        181: ['scripts/probe_case_181_jsoup_text.py'],
        184: ['scripts/probe_cases_171_186_logger.py'],
        185: ['scripts/probe_cases_171_186_logger.py'],
        186: ['scripts/probe_cases_171_186_logger.py'],
        188: ['scripts/probe_case_188_lexer_compatibility.py'],
    }
    resumed = ['scripts/resume_cases_168_188.py', 'scripts/inspect_resolved_cases_161_188_jars.py',
               'scripts/collect_cases_166_188_evidence.py', 'scripts/collect_cases_166_188_poms.py']

    for n in range(161, end + 1):
        base = ROOT / f'logs/case{n}_evidence'
        files = [p for p in base.rglob('*') if p.is_file() and p.name != 'sha256_manifest.json']
        record = runpy.run_path(str(ROOT / f'scripts/append_case_{n}.py'))['RECORD']
        files.extend(ROOT / p for p in shared + (resumed if n >= 168 else []) + helpers.get(n, []) + [f'scripts/append_case_{n}.py', f'results/case{n}_review.md', record['pre_log'], record['breaking_log']])
        manifest = {}
        for path in sorted(set(files)):
            with path.open('rb') as stream:
                manifest[path.relative_to(ROOT).as_posix()] = hashlib.file_digest(stream, 'sha256').hexdigest()
        path = base / 'sha256_manifest.json'
        if path.exists():
            if json.loads(path.read_text()) != manifest:
                raise ValueError(f'Sealed evidence changed for case {n}')
        else:
            with path.open('x', encoding='utf-8') as output:
                json.dump(manifest, output, indent=2)
        print(n, 'hashed files:', len(manifest))

if __name__ == '__main__':
    main()
