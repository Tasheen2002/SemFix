"""Compare logger selection using one compiled probe and the original test JARs."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SOURCE = '''import org.slf4j.LoggerFactory;

public class LoggerSelectionProbe {
    public static void main(String[] args) {
        System.out.println("factory=" + LoggerFactory.getILoggerFactory().getClass().getName());
        System.out.println("logger=" + LoggerFactory.getLogger("bump-diagnostic").getClass().getName());
    }
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case_number', type=int, choices=(156, 159))
    args = parser.parse_args()
    base = ROOT / f'logs/case{args.case_number}_evidence'
    source = base / 'LoggerSelectionProbe.java'
    with source.open('x', encoding='utf-8') as output:
        output.write(SOURCE)
    classes = base / 'logger_probe_classes'
    classes.mkdir()
    javac = 'C:/Program Files/Java/jdk-21.0.11/bin/javac.exe'
    subprocess.run([javac, '--release', '11', '-cp', str(next((base / 'pre/jars').glob('slf4j-api-*.jar'))), '-d', str(classes), str(source)], check=True)
    snapshots = {phase: json.loads((base / phase / 'archive_summary.json').read_text()) for phase in ('pre', 'breaking')}
    affected = next(r['test_class'] for r in snapshots['breaking']['reports'] if r['errors'] or r['failures'])
    runs = []
    for phase, summary in snapshots.items():
        report = next(r for r in summary['reports'] if r['test_class'] == affected)
        classpath = ':'.join(p for p in report['classpath'].split(':') if p.endswith('.jar'))
        command = ['docker', 'run', '--rm', '--name', f'research-case{args.case_number}-logger-{phase}',
                   '--mount', f'type=bind,source={classes},target=/probe,readonly', '--entrypoint', 'java',
                   summary['image_id'], '-cp', '/probe:' + classpath, 'LoggerSelectionProbe']
        run = subprocess.run(command, capture_output=True, text=True, timeout=120)
        with (base / f'logger_probe_{phase}.log').open('x', encoding='utf-8') as output:
            output.write(run.stdout + run.stderr)
        runs.append({'phase': phase, 'image_id': summary['image_id'], 'command': command, 'exit_code': run.returncode,
                     'stdout': run.stdout, 'stderr': run.stderr})
        print(phase, run.returncode, run.stdout, run.stderr, flush=True)
    result = {'test_classpath_source': affected, 'class_sha256': hashlib.sha256((classes / 'LoggerSelectionProbe.class').read_bytes()).hexdigest(), 'runs': runs}
    with (base / 'logger_probe_results.json').open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2)
    if any(r['exit_code'] for r in runs) or 'logger=org.slf4j.helpers.NOPLogger' not in runs[1]['stdout']:
        raise ValueError('Unexpected logger probe outcome')


if __name__ == '__main__':
    main()
