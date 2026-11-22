"""Run identical logging bytecode on both original SLF4J dependency classpaths."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = '''import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.util.Collection;
public class LoggerSelectionProbe {
    public static void main(String[] args) throws Exception {
        Class<?> capture = Class.forName("uk.org.lidalia.slf4jtest.TestLoggerFactory");
        capture.getMethod("clearAll").invoke(null);
        Logger logger = LoggerFactory.getLogger("case117-probe");
        logger.info("case117 diagnostic message");
        System.out.println("factory=" + LoggerFactory.getILoggerFactory().getClass().getName());
        System.out.println("logger=" + logger.getClass().getName());
        System.out.println("captured=" + ((Collection<?>) capture.getMethod("getAllLoggingEvents").invoke(null)).size());
    }
}
'''

def main():
    base = ROOT / 'logs/case117_evidence'
    source = base / 'LoggerSelectionProbe.java'
    with source.open('x', encoding='utf-8') as output:
        output.write(SOURCE)
    classes = base / 'logger_probe_classes'
    classes.mkdir()
    api = base / 'pre/jars/slf4j-api-1.7.32.jar'
    command = ['C:/Program Files/Java/jdk-21.0.11/bin/javac.exe', '--release', '11', '-classpath', str(api), '-d', str(classes), str(source)]
    compilation = subprocess.run(command, capture_output=True, text=True)
    if compilation.returncode:
        raise RuntimeError(compilation.stderr)
    result = {'purpose': 'Same compiled logging call and capture library; original dependencies retained', 'compile_command': command, 'compile_exit_code': compilation.returncode, 'class_sha256': hashlib.sha256((classes / 'LoggerSelectionProbe.class').read_bytes()).hexdigest(), 'runs': []}
    for phase in ('pre', 'breaking'):
        summary = json.loads((base / phase / 'archive_summary.json').read_text())
        report = next(r for r in summary['reports'] if r['test_class'].endswith('JasmineResultLoggerTest'))
        classpath = ':'.join(p for p in report['classpath'].split(':') if p.endswith('.jar'))
        command = ['docker', 'run', '--rm', '--name', 'research-case117-logger-' + phase, '--mount', 'type=bind,source=' + str(classes) + ',target=/probe-classes,readonly', '--entrypoint', 'java', summary['image_id'], '-classpath', '/probe-classes:' + classpath, 'LoggerSelectionProbe']
        run = subprocess.run(command, capture_output=True, text=True, timeout=120)
        with (base / f'logger_probe_{phase}.log').open('x', encoding='utf-8') as output:
            output.write(run.stdout + run.stderr)
        result['runs'].append({'phase': phase, 'image_id': summary['image_id'], 'command': command, 'exit_code': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr})
        print(phase, run.returncode, run.stdout, run.stderr, flush=True)
    with (base / 'logger_probe_results.json').open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2)
    if [r['exit_code'] for r in result['runs']] != [0, 0] or 'captured=1' not in result['runs'][0]['stdout'] or 'captured=0' not in result['runs'][1]['stdout'] or 'NOPLoggerFactory' not in result['runs'][1]['stdout']:
        raise ValueError('Unexpected diagnostic behavior; inspect before assessment')

if __name__ == '__main__':
    main()
