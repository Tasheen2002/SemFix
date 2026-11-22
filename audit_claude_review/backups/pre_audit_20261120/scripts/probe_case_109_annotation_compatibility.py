"""Run one identical Java 11 class file against both original Guice environments.

The probe changes no dependency or client source. This is diagnostic evidence,
not a repair and not an independently reviewed semantic label.
"""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = '''import com.google.inject.Key;
import org.eclipse.sisu.Parameters;
import java.util.Arrays;

public class AnnotationCompatibilityProbe {
    public static void main(String[] args) {
        System.out.println("java=" + System.getProperty("java.version"));
        System.out.println("Guice=" + Key.class.getProtectionDomain().getCodeSource().getLocation());
        System.out.println("Parameters annotations=" + Arrays.toString(Parameters.class.getAnnotations()));
        System.out.println("binding=" + Key.get(String.class, Parameters.class));
    }
}
'''

def main():
    base = ROOT / 'logs/case109_evidence'
    source = base / 'AnnotationCompatibilityProbe.java'
    with source.open('x', encoding='utf-8') as output:
        output.write(SOURCE)
    classes = base / 'annotation_probe_classes'
    classes.mkdir()
    jars = sorted((base / 'pre/jars').glob('*.jar'))
    command = ['C:/Program Files/Java/jdk-21.0.11/bin/javac.exe', '--release', '11', '-classpath', ';'.join(map(str, jars)), '-d', str(classes), str(source)]
    compilation = subprocess.run(command, capture_output=True, text=True)
    if compilation.returncode:
        raise RuntimeError(compilation.stderr)
    bytecode = (classes / 'AnnotationCompatibilityProbe.class').read_bytes()
    result = {'purpose': 'Same compiled public API call in original PRE/BREAKING images; no source or dependency substitutions', 'compile_command': command, 'compile_exit_code': compilation.returncode, 'compile_stdout': compilation.stdout, 'compile_stderr': compilation.stderr, 'class_sha256': hashlib.sha256(bytecode).hexdigest(), 'class_major_version': int.from_bytes(bytecode[6:8], 'big'), 'runs': []}
    for phase in ('pre', 'breaking'):
        summary = json.loads((base / phase / 'archive_summary.json').read_text())
        report = next(r for r in summary['reports'] if r['test_class'].endswith('UploadBomMojoIntegrationTest'))
        classpath = ':'.join(p for p in report['classpath'].split(':') if p.endswith('.jar'))
        command = ['docker', 'run', '--rm', '--name', 'research-case109-annotation-' + phase, '--mount', 'type=bind,source=' + str(classes) + ',target=/probe-classes,readonly', '--entrypoint', 'java', summary['image_id'], '-classpath', '/probe-classes:' + classpath, 'AnnotationCompatibilityProbe']
        run = subprocess.run(command, capture_output=True, text=True, timeout=120)
        with (base / f'annotation_probe_{phase}.log').open('x', encoding='utf-8') as output:
            output.write(run.stdout + run.stderr)
        result['runs'].append({'phase': phase, 'image_id': summary['image_id'], 'command': command, 'exit_code': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr})
        print(phase, 'exit', run.returncode, run.stdout, run.stderr, flush=True)
    with (base / 'annotation_probe_results.json').open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2)
    if result['runs'][0]['exit_code'] != 0 or result['runs'][1]['exit_code'] != 1 or 'is not a binding annotation' not in result['runs'][1]['stderr']:
        raise ValueError('Unexpected diagnostic result; inspect before assessment')

if __name__ == '__main__':
    main()
