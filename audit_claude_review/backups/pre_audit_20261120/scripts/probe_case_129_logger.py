"""Run the same Log4j initialization against the original test classpaths."""

import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SOURCE = '''import org.apache.logging.log4j.LogManager;

public class Case129LoggerProbe {
    public static void main(String[] args) {
        System.out.println(LogManager.getContext(false).getClass().getName());
    }
}
'''


def main():
    base = ROOT / 'logs/case129_evidence'
    source = base / 'Case129LoggerProbe.java'
    with source.open('x', encoding='utf-8') as output:
        output.write(SOURCE)
    with (base / 'pre/Case129LoggerProbe.class').open('xb') as output:
        output.close()
    subprocess.run([
        'C:/Program Files/Java/jdk-21.0.11/bin/javac.exe', '--release', '11',
        '-classpath', str(base / 'pre/jars/log4j-api-2.12.1.jar'),
        '-d', str(base / 'pre'), str(source),
    ], check=True)
    binary = base / 'pre/Case129LoggerProbe.class'
    runs = []
    for phase in ('pre', 'breaking'):
        summary = json.loads((base / phase / 'archive_summary.json').read_text())
        report = next(r for r in summary['reports'] if r['test_class'].endswith('.GeometryTest'))
        classpath = ':'.join(p for p in report['classpath'].split(':') if p.endswith('.jar'))
        command = [
            'docker', 'run', '--rm', '--name', f'research-case129-logger-{phase}',
            '--mount', f'type=bind,source={binary},target=/probe/Case129LoggerProbe.class,readonly',
            '--entrypoint', 'java', summary['image_id'], '-cp', '/probe:' + classpath,
            'Case129LoggerProbe',
        ]
        run = subprocess.run(command, capture_output=True, text=True, timeout=120)
        with (base / f'logger_probe_{phase}.log').open('x', encoding='utf-8') as output:
            output.write(run.stdout + run.stderr)
        runs.append({'phase': phase, 'image_id': summary['image_id'], 'command': command,
                     'exit_code': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr})
    result = {'class_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(), 'runs': runs}
    with (base / 'logger_probe_results.json').open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2)
    for run in runs:
        print(run['phase'], run['exit_code'], run['stdout'], run['stderr'])


if __name__ == '__main__':
    main()
