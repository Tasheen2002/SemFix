"""Reconcile original PRE XML with a debug-only BREAKING classpath capture."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def main():
    base = ROOT / 'logs/case116_evidence'
    pre = json.loads((base / 'pre/archive_summary.json').read_text())
    report = next(r for r in pre['reports'] if r['module'] == 'maven-plugin')
    before = {'source': 'Original fresh PRE Surefire XML', 'report': report['path'], 'test_classpath': [p for p in report['classpath'].split(':') if p], 'provider_classpath': [], 'provider_classpath_not_available_in_original_xml': True}
    lines = (base / 'discovery_debug.log').read_text(errors='replace').splitlines()
    after = {'source': 'Separate original BREAKING image rerun with Maven debug logging only', 'module': 'maven-plugin'}
    for marker, key in [('test classpath:', 'test_classpath'), ('provider classpath:', 'provider_classpath')]:
        found = [(i+1, line.split(marker, 1)[1].split()) for i, line in enumerate(lines) if line.startswith('[DEBUG] ' + marker)]
        if len(found) != 1:
            raise ValueError('Expected one failed-module ' + marker)
        after[key + '_log_line'], after[key] = found[0]
    positions = [i for i, line in enumerate(lines) if re.fullmatch(r'\[DEBUG\]\s+junit:junit:jar:3\.8\.1:compile', line)]
    if len(positions) != 1:
        raise ValueError('Expected one selected JUnit compile dependency')
    i = positions[0]
    after['dependency_chain_excerpt'] = lines[max(0, i-8):i+2]
    for phase, value in [('pre', before), ('breaking', after)]:
        with (base / phase / 'discovery_classpaths.json').open('x', encoding='utf-8') as output:
            json.dump(value, output, indent=2)
    junit = '/root/.m2/repository/junit/junit/3.8.1/junit-3.8.1.jar'
    if junit in before['test_classpath'] or junit not in after['test_classpath']:
        raise ValueError('JUnit introduction differs from hypothesis')
    print('PRE test paths:', len(before['test_classpath']), 'BREAKING test/provider paths:', len(after['test_classpath']), len(after['provider_classpath']))

if __name__ == '__main__':
    main()
