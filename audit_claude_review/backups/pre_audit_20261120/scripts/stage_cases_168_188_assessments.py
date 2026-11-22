"""Materialize reviewed case notes and append scripts from original build evidence."""
import argparse
import csv
import json
from pathlib import Path
import pprint
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
KEYS = ('tests','failures','errors','skipped')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('findings', type=Path, help='Case-number keyed JSON with reviewed classification, primary exception and rationale')
    options = parser.parse_args()
    findings = json.loads(options.findings.read_text(encoding='utf-8'))
    with (RESULTS / 'test_failure_candidates.csv').open(encoding='utf-8-sig',newline='') as file:
        candidates = list(csv.DictReader(file))
    template = (ROOT / 'scripts/append_case_167.py').read_text(encoding='utf-8')
    reconcile = runpy.run_path(str(ROOT / 'scripts/reconcile_cases_161_188_reports.py'))['reconcile']
    for raw, data in sorted(findings.items(), key=lambda x:int(x[0])):
        n = int(raw)
        if not 168 <= n <= 188:
            raise ValueError(f'Case out of range: {n}')
        status, binary, exception, origin, rationale = data
        candidate = candidates[n-1]
        case_id = candidate['case_id']
        base = ROOT / f'logs/case{n}_evidence'
        logs = {phase:f'logs/batch_triage/{case_id[:8]}_{phase}.log' for phase in ('pre','breaking')}
        totals = {}
        for phase, log in logs.items():
            directory = base / phase
            meta = json.loads((directory / 'archive_summary.json').read_text())
            assert meta['case_id'] == case_id and meta['phase'] == phase and meta['container_state']['Status'] == 'exited' and not meta['container_state']['OOMKilled']
            text = (ROOT/log).read_text(encoding='utf-8',errors='replace')
            assert re.findall(r'^\[INFO\] BUILD (SUCCESS|FAILURE)\s*$',text,re.M) == ['SUCCESS' if phase=='pre' else 'FAILURE'], (n,phase)
            counts = meta['aggregate_counts']
            if any('/surefire-reports/junitreports/' in r['path'] for r in meta['reports']):
                evidence = reconcile(directory)
                counts = evidence['aggregate_counts']
                path = directory / 'reconciled_counts.json'
                if not path.exists():
                    path.write_text(json.dumps(evidence, indent=2))
                else:
                    assert json.loads(path.read_text()) == evidence
            matches = re.findall(r'^(?:\[[A-Z]+\] )?Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)[ \t]*$',text,re.M)
            measured = tuple(map(sum,zip(*(map(int,m) for m in matches)))) if matches else (0,0,0,0)
            assert tuple(counts[k] for k in KEYS) == measured, (n,phase,counts,measured)
            totals[phase] = counts
        pre, broken = (totals[p] for p in ('pre','breaking'))
        comparison = json.loads((base/'all_poms_comparison.json').read_text())
        label = {'B':'PROVISIONAL_BEHAVIORAL','N':'NON_BEHAVIORAL'}[status]
        effect = 'TEST_ERROR' if broken['errors'] or not broken['failures'] else 'TEST_FAILURE'
        subtype = 'LINKAGE_ERROR' if binary=='YES' else 'RUNTIME_EXCEPTION' if effect=='TEST_ERROR' else 'TEST_ASSERTION'
        record = dict(case_id=case_id,project=candidate['project'],dependency_group=candidate['dependency_group'],
            dependency_artifact=candidate['dependency_artifact'],old_version=candidate['previous_version'],
            new_version=candidate['new_version'],bump_category=candidate['failure_category'],
            pre_build_status='SUCCESS',breaking_build_status='FAILURE',pre_tests=str(pre['tests']),
            breaking_tests=str(broken['tests']),breaking_failures=str(broken['failures']),breaking_errors=str(broken['errors']),
            test_effect_type=effect,test_effect_subtype=subtype,main_exception=exception,failure_origin=origin,
            origin_library=':'.join([candidate['dependency_group'],candidate['dependency_artifact'],candidate['new_version']]),
            binary_linkage_incompatibility=binary,behavioral_status=label,
            behavior_change_type='OTHER_BEHAVIORAL_CHANGE' if status=='B' else '',behavior_description=rationale,
            pre_log=logs['pre'],breaking_log=logs['breaking'],review_status='PENDING_HUMAN_REVIEW',
            reviewer_1_label='',reviewer_2_label='',final_label='',
            notes=f'Agent assessment pending independent human review. Both original Docker images were run. See results/case{n}_review.md and logs/case{n}_evidence/.')
        code = template[:template.index('CASE_ID =')].replace('Case 167',f'Case {n}')+f'CASE_ID = {case_id!r}\nRECORD = '+pprint.pformat(record,sort_dicts=False)+'\n\n\n'+template[template.index('def main():'):].replace('Case 167',f'Case {n}').replace('case167',f'case{n}')
        review = f"# Case {n} review\n\n{candidate['project']} updates {candidate['dependency_artifact']} from {candidate['previous_version']} to {candidate['new_version']}.\n\n{rationale}\n\n| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |\n|---|---|---:|---:|---:|---:|\n"
        for phase,outcome in [('pre','SUCCESS'),('breaking','FAILURE')]:
            review += f'| {phase.upper()} | {outcome} | ' + ' | '.join(str(totals[phase][k]) for k in KEYS) + ' |\n'
        review += f"\nAssessment is `{label}`. Binary linkage flag is `{binary}`. Independent human review is pending.\n\nChanged POMs in the original archives are {', '.join(comparison['changed_poms'])}. Original logs and archived reports are indexed in the evidence manifest.\n"
        for path, content in [(ROOT/f'scripts/append_case_{n}.py',code),(RESULTS/f'case{n}_review.md',review)]:
            if path.exists():
                if path.read_text(encoding='utf-8') != content:
                    raise ValueError(f'Existing assessment differs at {path}')
            else:
                with path.open('x',encoding='utf-8') as file:
                    file.write(content)
        print(f'Staged Case {n}', flush=True)

if __name__=='__main__':
    main()
