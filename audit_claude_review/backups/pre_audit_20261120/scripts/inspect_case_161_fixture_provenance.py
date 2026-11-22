"""Verify the Case 161 fixture-only change and unchanged runtime classpaths."""
import hashlib
import json
from pathlib import Path
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = 'polyglot-kotlin/src/test/resources/example/pom.xml'
INPUT = 'polyglot-kotlin/src/test/resources/example/pom.kts'

def main():
    base = ROOT / 'logs/case161_evidence'
    summaries = [json.loads((base / phase / 'archive_summary.json').read_text()) for phase in ('pre', 'breaking')]
    before, after = [s['source_and_pom_sha256'] for s in summaries]
    assert before.keys() == after.keys()
    assert [p for p in before if before[p] != after[p]] == [FIXTURE]
    classpaths = [{(r['module'], r['test_class']): r['classpath'] for r in s['reports']} for s in summaries]
    assert classpaths[0] == classpaths[1]
    inputs, versions = [], []
    for phase, version in [('pre', '1.3.31'), ('breaking', '1.6.0')]:
        with tarfile.open(base / phase / 'artifacts.tar') as archive:
            inputs.append(archive.extractfile(INPUT).read())
            xml = ET.fromstring(archive.extractfile(FIXTURE).read())
        ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
        dependencies = xml.findall('m:dependencies/m:dependency', ns)
        stdlib = next(d for d in dependencies if d.findtext('m:artifactId', namespaces=ns) == 'kotlin-stdlib')
        assert stdlib.findtext('m:version', namespaces=ns) == version
        versions.append(version)
        metadata = json.loads((base / phase / 'jar_inspection.json').read_text())
        assert len(metadata['artifacts']) == 1
        jar = metadata['artifacts'][0]
        assert '/kotlin-stdlib/1.4.10/' in jar['resolved_path']
        assert hashlib.sha256((base / phase / 'jars/kotlin-stdlib-1.4.10.jar').read_bytes()).hexdigest() == jar['sha256']
    assert inputs[0] == inputs[1] and b'"kotlin.version" to "1.3.31"' in inputs[0]
    hashes = [hashlib.sha256((base / phase / 'jars/kotlin-stdlib-1.4.10.jar').read_bytes()).hexdigest() for phase in ('pre', 'breaking')]
    assert hashes[0] == hashes[1]
    result = {'only_changed_source_or_pom': FIXTURE, 'fixture_stdlib_versions': versions,
              'dsl_input_unchanged': INPUT, 'dsl_input_sha256': hashlib.sha256(inputs[0]).hexdigest(),
              'all_test_classpaths_identical': True, 'compared_test_classpaths': len(classpaths[0]),
              'actual_stdlib_version_both_images': '1.4.10', 'actual_stdlib_sha256_both_images': hashes[0]}
    with (base / 'fixture_provenance_check.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
