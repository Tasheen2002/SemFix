"""Execute identical JDBC/SQL bytecode against both original H2 versions."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SQL = 'CREATE TABLE precision_probe (stored_data VARCHAR(10000000) NOT NULL)'
SOURCE = '''import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;
public class H2PrecisionProbe {
    public static void main(String[] args) throws Exception {
        Class.forName("org.h2.Driver");
        try (Connection connection = DriverManager.getConnection("jdbc:h2:mem:case114_precision");
             Statement statement = connection.createStatement()) {
            System.out.println("database=" + connection.getMetaData().getDatabaseProductVersion());
            System.out.println("sql=" + args[0]);
            statement.execute(args[0]);
            System.out.println("CREATE TABLE accepted");
        }
    }
}
'''

def main():
    base = ROOT / 'logs/case114_evidence'
    source = base / 'H2PrecisionProbe.java'
    with source.open('x', encoding='utf-8') as output:
        output.write(SOURCE)
    classes = base / 'precision_probe_classes'
    classes.mkdir()
    command = ['C:/Program Files/Java/jdk-21.0.11/bin/javac.exe', '--release', '11', '-d', str(classes), str(source)]
    compilation = subprocess.run(command, capture_output=True, text=True)
    if compilation.returncode:
        raise RuntimeError(compilation.stderr)
    bytecode = (classes / 'H2PrecisionProbe.class').read_bytes()
    result = {'purpose': 'Isolate changed acceptance of the column precision through unchanged JDBC calls; not a repair', 'sql': SQL, 'compile_command': command, 'compile_exit_code': compilation.returncode, 'class_sha256': hashlib.sha256(bytecode).hexdigest(), 'runs': []}
    classpaths = []
    for phase in ('pre', 'breaking'):
        summary = json.loads((base / phase / 'archive_summary.json').read_text())
        inspection = json.loads((base / phase / 'jar_inspection.json').read_text())
        if len(inspection['artifacts']) != 1:
            raise ValueError('Expected exactly one resolved H2 artifact')
        jar = inspection['artifacts'][0]['resolved_path']
        cps = json.loads((base / phase / 'resolved_test_classpaths.json').read_text())
        cp = next(r for r in cps if '/persistence/target/' in r['report'])
        classpaths.append(set(cp['classpath'].split(':')))
        command = ['docker', 'run', '--rm', '--name', 'research-case114-precision-' + phase, '--mount', 'type=bind,source=' + str(classes) + ',target=/probe-classes,readonly', '--entrypoint', 'java', summary['image_id'], '-classpath', '/probe-classes:' + jar, 'H2PrecisionProbe', SQL]
        run = subprocess.run(command, capture_output=True, text=True, timeout=120)
        with (base / f'precision_probe_{phase}.log').open('x', encoding='utf-8') as output:
            output.write(run.stdout + run.stderr)
        result['runs'].append({'phase': phase, 'image_id': summary['image_id'], 'resolved_h2_path': jar, 'command': command, 'exit_code': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr})
        print(phase, run.returncode, run.stdout, run.stderr, flush=True)
    result['persistence_test_classpath_difference'] = {'property': 'surefire.test.class.path', 'removed': sorted(classpaths[0] - classpaths[1]), 'added': sorted(classpaths[1] - classpaths[0])}
    with (base / 'precision_probe_results.json').open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2)
    if [r['exit_code'] for r in result['runs']] != [0, 1] or 'Precision' not in result['runs'][1]['stderr'] or '1048576' not in result['runs'][1]['stderr']:
        raise ValueError('Unexpected diagnostic outcome; inspect before assessment')

if __name__ == '__main__':
    main()
