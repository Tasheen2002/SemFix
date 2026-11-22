"""Find the updated Jetty Server reference to the missing lifecycle type."""
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    base = ROOT / 'logs/case125_evidence'
    jar = base / 'breaking/jars/jetty-server-10.0.14.jar'
    needle = b'org/eclipse/jetty/util/component/AbstractLifeCycle$StopException'
    with zipfile.ZipFile(jar) as archive:
        classes = [name[:-6].replace('/', '.') for name in archive.namelist() if name.endswith('.class') and needle in archive.read(name)]
    records = []
    for clazz in classes:
        command = ['C:/Program Files/Java/jdk-21.0.11/bin/javap.exe', '-classpath', str(jar), '-p', '-s', '-c', clazz]
        run = subprocess.run(command, capture_output=True, text=True)
        if run.returncode:
            raise RuntimeError(run.stderr)
        filename = jar.stem + '_' + clazz.rsplit('.', 1)[-1] + '_StopException_javap.txt'
        path = base / 'breaking' / filename
        if path.exists():
            if path.read_text() != run.stdout:
                raise ValueError('Existing disassembly differs; preserve and inspect')
        else:
            with path.open('x', encoding='utf-8') as output:
                output.write(run.stdout)
        records.append({'class': clazz, 'file': filename, 'command': command, 'exit_code': run.returncode})
    result = {'referenced_binary_type': needle.decode(), 'artifact': jar.name, 'references': records}
    path = base / 'stop_exception_references.json'
    if path.exists():
        if json.loads(path.read_text()) != result:
            raise ValueError('Existing reference metadata differs')
    else:
        with path.open('x', encoding='utf-8') as output:
            json.dump(result, output, indent=2)
    print('Referencing classes:', classes)

if __name__ == '__main__':
    main()
