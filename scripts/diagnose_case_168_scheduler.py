"""Compare the scheduler's two existing regression tests in the original images."""
import csv
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]

def main():
    with (ROOT/'results/test_failure_candidates.csv').open(encoding='utf-8-sig',newline='') as stream:
        case_id=list(csv.DictReader(stream))[167]['case_id']
    base=ROOT/'logs/case168_evidence'
    results=[]
    for phase in ('pre','breaking'):
        original=f'bump-{case_id}-{phase}'
        image=subprocess.check_output(['docker','inspect','--format','{{.Image}}',original],text=True).strip()
        name=f'research-case168-regression-{phase}'
        command=['docker','run','--name',name,'--entrypoint','mvn',image,
                 'clean','test','-B','-pl','choco','-am',
                 '-Dtest=IssuesTest#testIssue100+testIssue101','-Dsurefire.failIfNoSpecifiedTests=false']
        log=base/f'regression_{phase}.log'
        with log.open('x',encoding='utf-8') as stream:
            run=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,timeout=300)
        text=log.read_text(encoding='utf-8',errors='replace')
        summaries=re.findall(r'^\[(?:INFO|ERROR)\] Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)[ \t]*$',text,re.M)
        results.append(dict(phase=phase,command=command,image_id=image,exit_code=run.returncode,
                            log=log.name,summaries=summaries,parser_exception='net.minidev.json.parser.ParseException' in text))
        print(phase,run.returncode,summaries,flush=True)
    with (base/'regression_comparison.json').open('x') as stream:
        json.dump(results,stream,indent=2)

if __name__=='__main__':
    main()
