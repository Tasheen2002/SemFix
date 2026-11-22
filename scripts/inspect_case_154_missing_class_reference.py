"""Locate the missing Jackson class reference in the archived resolved JARs."""
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    base = ROOT / 'logs/case154_evidence'
    result = {}
    for phase, version in [('pre', '2.10.5.1'), ('breaking', '2.12.7.1')]:
        jar = base / phase / 'jars' / f'jackson-databind-{version}.jar'
        with zipfile.ZipFile(jar) as archive:
            found = [n for n in archive.namelist() if n.endswith('.class') and
                     b'com/fasterxml/jackson/core/util/JacksonFeature' in archive.read(n)]
        result[phase] = {'jar_sha256': hashlib.sha256(jar.read_bytes()).hexdigest(), 'referring_classes': found}
        for name in found:
            clazz = name[:-6].replace('/', '.')
            run = subprocess.run(['C:/Program Files/Java/jdk-21.0.11/bin/javap.exe', '-classpath', str(jar),
                                  '-p', '-s', '-c', clazz], capture_output=True, text=True, check=True)
            output = base / phase / f'{jar.stem}_{clazz.rsplit(".", 1)[-1]}_javap.txt'
            if output.exists():
                assert output.read_text() == run.stdout
            else:
                with output.open('x') as stream:
                    stream.write(run.stdout)
    assert result['pre']['referring_classes'] == []
    assert result['breaking']['referring_classes'] == ['com/fasterxml/jackson/databind/DeserializationContext.class', 'com/fasterxml/jackson/databind/node/TreeTraversingParser.class', 'com/fasterxml/jackson/databind/util/TokenBuffer$Parser.class', 'com/fasterxml/jackson/databind/util/TokenBuffer.class']
    with (base / 'missing_class_references.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
