"""Capture Maven's effective test classpath for the original discovery failure.

Only debug logging is added. No source, dependency or test-engine setting changes.
"""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def main():
    base = ROOT / 'logs/case116_evidence'
    original = json.loads((base / 'breaking/archive_summary.json').read_text())
    name = 'research-case116-discovery-debug'
    command = ['docker', 'run', '--name', name, '--entrypoint', 'mvn', original['image_id'], '-X', 'clean', 'test', '-B']
    with (base / 'discovery_debug.log').open('x', encoding='utf-8') as output:
        run = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT, timeout=240)
    info = json.loads(subprocess.check_output(['docker', 'inspect', name], text=True))[0]
    result = {'purpose': 'Obtain the test classpath behind the original engine-discovery failure', 'only_adjustment': 'Maven debug logging; original source and dependency versions retained', 'command': command, 'image_id': info['Image'], 'state': info['State'], 'exit_code': run.returncode}
    with (base / 'discovery_debug_results.json').open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2)
    print('Diagnostic exit:', run.returncode)
    if run.returncode != 1 or info['State']['Status'] != 'exited':
        raise ValueError('Unexpected diagnostic result; inspect before assessment')

if __name__ == '__main__':
    main()
