"""Resume original BUMP runs and preserve interrupted evidence."""
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime
import json
from pathlib import Path
import re
import subprocess
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
LOGS = ROOT / 'logs/batch_triage'
TRIAGE = ROOT / 'scripts/batch_triage_test_failures.py'

def inspect(name):
    result = subprocess.run(['docker','container','inspect',name],capture_output=True,text=True)
    if result.returncode:
        if 'No such' in result.stderr:
            return None
        raise RuntimeError(result.stderr)
    return json.loads(result.stdout)[0]

def work(item):
    n, row = item
    stage = RESULTS / f"archive/cases{'168_174' if n <= 174 else '175_188'}_triage"
    output = stage / f'case{n}.csv'
    if output.exists():
        return n, 'saved triage reused'
    source = TRIAGE.read_text(encoding='utf-8').split('parser = argparse.ArgumentParser(', 1)[0]
    ns = {'__name__': 'triage_resume'}
    exec(compile(source, str(TRIAGE), 'exec'), ns)
    ns.update(args=SimpleNamespace(retain_containers=True, force=False), OUTPUT_FILE=output)
    original = ns['run_docker_image']

    def phase_run(command, case_id, phase):
        log = LOGS / f'{case_id[:8]}_{phase}.log'
        name = f'bump-{case_id}-{phase}'
        info = inspect(name)
        if info and info['State']['Running']:
            subprocess.run(['docker','wait',name],check=True,timeout=2700,capture_output=True)
            info = inspect(name)
        content = log.read_text(encoding='utf-8',errors='replace') if log.exists() else ''
        matches = re.findall(r'^\[INFO\] BUILD (SUCCESS|FAILURE)\s*$', content, re.M)
        if len(matches) == 1 and info and info['State']['Status'] == 'exited' and not info['State']['OOMKilled']:
            state = info['State']
            elapsed = 0.0
            try:
                elapsed = (datetime.fromisoformat(state['FinishedAt']) - datetime.fromisoformat(state['StartedAt'])).total_seconds()
            except ValueError:
                pass
            print(n, phase, 'reusing completed run', flush=True)
            return dict(exit_code=state['ExitCode'], timeout=False, duration_seconds=round(elapsed,2), log_file=str(log), runner_error='')
        if matches:
            raise RuntimeError(f'{n} {phase} has a finished log without matching retained container')
        suffix = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        if info:
            if info['State']['Status'] not in ('exited','created'):
                raise RuntimeError(f'{n} {phase} container in unexpected state')
            subprocess.run(['docker','rename',name,name+'-interrupted-'+suffix],check=True)
        if log.exists():
            log.rename(log.with_name(log.name+'.interrupted-'+suffix))
        print(n, phase, 'running original image', flush=True)
        return original(command,case_id,phase)

    ns['run_docker_image'] = phase_run
    ns['process_candidate'](n,row)
    if not output.exists():
        raise RuntimeError(f'Case {n} did not save triage')
    return n, 'triage saved'

def main():
    subprocess.run(['docker','info','--format','{{.ServerVersion}}'],check=True,timeout=45)
    with (RESULTS/'test_failure_candidates.csv').open(encoding='utf-8-sig',newline='') as file:
        candidates=list(csv.DictReader(file))
    targets=[(n,candidates[n-1]) for n in (168,169,170,180,183,184,171,172,173,174,185,186,187,188,175,176,177,178,179,181,182)]
    with ThreadPoolExecutor(max_workers=3) as pool:
        pending={pool.submit(work,item): item[0] for item in targets}
        errors=[]
        from concurrent.futures import as_completed
        for future in as_completed(pending):
            try:
                print(*future.result(),flush=True)
            except Exception as exc:
                errors.append(pending[future])
                print(f'Case {pending[future]} failed: {exc}',flush=True)
    if errors:
        raise SystemExit(f'Unfinished cases: {errors}')

if __name__=='__main__':
    main()
