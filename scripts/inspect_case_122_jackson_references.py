"""Distinguish JacksonFeature descriptors from related type-name prefix matches."""
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    base = ROOT / 'logs/case122_evidence'
    jar = base / 'breaking/jars/jackson-databind-2.12.6.1.jar'
    needle = b'com/fasterxml/jackson/core/util/JacksonFeature'
    with zipfile.ZipFile(jar) as archive:
        classes = [name[:-6].replace('/', '.') for name in archive.namelist() if name.endswith('.class') and needle in archive.read(name)]
    records = []
    for clazz in classes:
        command = ['C:/Program Files/Java/jdk-21.0.11/bin/javap.exe', '-classpath', str(jar), '-p', '-s', '-c', clazz]
        run = subprocess.run(command, capture_output=True, text=True)
        if run.returncode:
            raise RuntimeError(run.stderr)
        filename = jar.stem + '_' + clazz.rsplit('.', 1)[-1] + '_JacksonFeature_javap.txt'
        path = base / 'breaking' / filename
        if path.exists():
            if path.read_text() != run.stdout:
                raise ValueError('Existing disassembly differs; preserve and inspect')
        else:
            with path.open('x', encoding='utf-8') as output:
                output.write(run.stdout)
        direct = 'Lcom/fasterxml/jackson/core/util/JacksonFeature;' in run.stdout
        records.append({'class': clazz, 'file': filename, 'command': command, 'exit_code': run.returncode, 'direct_JacksonFeature_descriptor': direct})
    result = {'searched_type_name_prefix': needle.decode(), 'match_note': 'The prefix also matches JacksonFeatureSet; the direct descriptor flag distinguishes exact JacksonFeature parameters/types.', 'artifact': jar.name, 'references': records}
    path = base / 'jackson_feature_references.json'
    if path.exists() and json.loads(path.read_text()) != result:
        backup = path.with_name('jackson_feature_references.before_match_rule_clarification.json')
        if backup.exists():
            raise FileExistsError(backup)
        shutil.copy2(path, backup)
        path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    elif not path.exists():
        with path.open('x', encoding='utf-8') as output:
            json.dump(result, output, indent=2)
    print('Exact JacksonFeature descriptors:', [r['class'] for r in records if r['direct_JacksonFeature_descriptor']])

if __name__ == '__main__':
    main()
