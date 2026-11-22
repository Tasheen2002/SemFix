"""Load identical generated-lexer bytecode in both original ANTLR environments."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
PROBE = '''import org.antlr.v4.runtime.atn.ATNDeserializer;
public class LexerCompatibilityProbe {
    public static void main(String[] args) throws Exception {
        System.out.println("runtime=" + ATNDeserializer.class.getProtectionDomain().getCodeSource().getLocation());
        System.out.println("method=" + ATNDeserializer.class.getMethod("deserialize", char[].class));
        System.out.println("initialized=" + Class.forName(args[0]));
    }
}
'''

def main():
    base = ROOT / 'logs/case112_evidence'
    originals = []
    for phase in ('pre', 'breaking'):
        with tarfile.open(base / phase / 'artifacts.tar') as archive:
            member = next(m for m in archive if m.name.endswith('/BotOperationsLexer.java'))
            originals.append((member.name, archive.extractfile(member).read()))
    if originals[0] != originals[1]:
        raise ValueError('Generated lexer changed between images')
    source_dir = base / 'lexer_probe_sources'
    source_dir.mkdir()
    lexer = source_dir / 'BotOperationsLexer.java'
    lexer.write_bytes(originals[0][1])
    probe = source_dir / 'LexerCompatibilityProbe.java'
    probe.write_text(PROBE, encoding='utf-8')
    package = re.search(rb'^package ([\w.]+);', originals[0][1], re.M)[1].decode()
    classes = base / 'lexer_probe_classes'
    classes.mkdir()
    old = next((base / 'pre/jars').glob('antlr4-runtime-*.jar'))
    command = ['C:/Program Files/Java/jdk-21.0.11/bin/javac.exe', '--release', '11', '-classpath', str(old), '-d', str(classes), str(lexer), str(probe)]
    compilation = subprocess.run(command, capture_output=True, text=True)
    if compilation.returncode:
        raise RuntimeError(compilation.stderr)
    hashes = {p.relative_to(classes).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in classes.rglob('*.class')}
    result = {'purpose': 'Same generated lexer and same compiled probe in both original images; no client source/dependency substitutions', 'original_source_path': originals[0][0], 'original_source_sha256': hashlib.sha256(originals[0][1]).hexdigest(), 'source_identical_between_images': True, 'compile_command': command, 'compile_exit_code': compilation.returncode, 'compile_stderr': compilation.stderr, 'class_sha256': hashes, 'runs': []}
    for phase in ('pre', 'breaking'):
        summary = json.loads((base / phase / 'archive_summary.json').read_text())
        jars = json.loads((base / phase / 'jar_inspection.json').read_text())['artifacts']
        if len(jars) != 1:
            raise ValueError('Expected one ANTLR runtime')
        command = ['docker', 'run', '--rm', '--name', 'research-case112-lexer-' + phase, '--mount', 'type=bind,source=' + str(classes) + ',target=/probe-classes,readonly', '--entrypoint', 'java', summary['image_id'], '-classpath', '/probe-classes:' + jars[0]['resolved_path'], 'LexerCompatibilityProbe', package + '.BotOperationsLexer']
        run = subprocess.run(command, capture_output=True, text=True, timeout=120)
        with (base / f'lexer_probe_{phase}.log').open('x', encoding='utf-8') as output:
            output.write(run.stdout + run.stderr)
        result['runs'].append({'phase': phase, 'image_id': summary['image_id'], 'command': command, 'exit_code': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr})
        print(phase, run.returncode, run.stdout, run.stderr, flush=True)
    with (base / 'lexer_probe_results.json').open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2)
    if [r['exit_code'] for r in result['runs']] != [0, 1] or 'version 3 (expected 4)' not in result['runs'][1]['stderr']:
        raise ValueError('Unexpected diagnostic outcome; inspect before assessment')

if __name__ == '__main__':
    main()
