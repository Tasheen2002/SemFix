"""Collect stopped original-image evidence while the Cases 151-155 batch runs.

This performs no triage or classification. Archives are written exclusively by
the existing collector; an existing archive summary is treated as completed.
"""
import csv
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]

def run(script, *arguments):
    subprocess.run([sys.executable, '-u', str(ROOT / 'scripts' / script), *arguments], cwd=ROOT, check=True)

def main():
    rows = list(csv.DictReader((ROOT / 'results/test_failure_candidates.csv').open(encoding='utf-8-sig', newline='')))
    remaining = {(n, phase) for n in range(151, 156) for phase in ('pre', 'breaking')}
    deadline = time.monotonic() + 3 * 60 * 60
    while remaining:
        if time.monotonic() > deadline:
            raise TimeoutError('Evidence collection timed out; preserve completed archives and inspect runs')
        for n, phase in sorted(remaining):
            destination = ROOT / f'logs/case{n}_evidence/{phase}/archive_summary.json'
            if destination.exists():
                remaining.remove((n, phase))
                continue
            cid = rows[n-1]['case_id']
            log = ROOT / f'logs/batch_triage/{cid[:8]}_{phase}.log'
            if not log.exists():
                continue
            content = log.read_text(encoding='utf-8', errors='replace')
            if 'BUILD SUCCESS' not in content and 'BUILD FAILURE' not in content:
                continue
            inspected = subprocess.run(['docker', 'inspect', 'bump-' + cid + '-' + phase], capture_output=True, text=True)
            if inspected.returncode or json.loads(inspected.stdout)[0]['State']['Status'] != 'exited':
                continue
            print('Archiving', n, phase, flush=True)
            run('archive_case_121_125.py', '--case-number', str(n), '--phase', phase)
            remaining.remove((n, phase))
        if remaining:
            time.sleep(3)
    run('collect_cases_151_155_poms.py')
    print('Original reports, runner evidence and all-depth POMs collected.', flush=True)

if __name__ == '__main__':
    main()
