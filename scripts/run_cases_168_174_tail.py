"""Run reserved tail cases with the original triage code and per-case result files."""
import concurrent.futures
import csv
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/batch_triage_test_failures.py'
STAGING = ROOT / 'results/archive/cases168_174_triage'
FIRST, LAST = 168, 174

def worker(number, reserved_log):
    source = SCRIPT.read_text(encoding='utf-8')
    output = STAGING / f'case{number}.csv'
    marker = 'if log_file.exists():'
    assert source.count(marker) == 1
    source = source.replace(marker,
        'if log_file.exists() and not (log_file == RESERVED_LOG and log_file.stat().st_size == 0):')
    injection = "OUTPUT_FILE = Path(" + repr(str(output)) + ")\nRESERVED_LOG = Path(" + repr(str(reserved_log)) + ")\n"
    index = source.index('LOG_DIR =')
    source = source[:index] + injection + source[index:]
    log = STAGING / f'case{number}_runner.log'
    with log.open('x', encoding='utf-8') as stream:
        result = subprocess.run([sys.executable, '-u', '-c', source, '--start-case',
                                 str(number), '--end-case', str(number), '--retain-containers'],
                                stdout=stream, stderr=subprocess.STDOUT, cwd=ROOT, check=False)
    if result.returncode != 0 or not output.exists():
        raise RuntimeError(f'Case {number} did not save triage. See {log}')
    print(f'Case {number} saved', flush=True)

def main():
    STAGING.mkdir(parents=True)
    with (ROOT / 'results/test_failure_candidates.csv').open(encoding='utf-8-sig',newline='') as stream:
        candidates = list(csv.DictReader(stream))
    targets = [(n, ROOT / 'logs/batch_triage' / (candidates[n-1]['case_id'][:8] + '_pre.log'))
               for n in range(FIRST, LAST + 1)]
    if any(log.exists() for _, log in targets):
        raise FileExistsError('Tail runs already present')
    # The sequential runner refuses a case when its PRE log exists.
    for _, log in targets:
        log.touch(exist_ok=False)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        futures = {pool.submit(worker, n, log): n for n, log in targets}
        for job in concurrent.futures.as_completed(futures):
            try:
                job.result()
            except Exception as error:
                print(error, flush=True)

if __name__ == '__main__':
    main()
