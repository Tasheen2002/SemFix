"""Reconcile duplicate request/teardown entries without changing raw reports."""
from collections import defaultdict
import json
from pathlib import Path
import re
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

def reconcile(base):
    summary = json.loads((base / 'archive_summary.json').read_text())
    reports = {r['path']: r for r in summary['reports']}
    grouped = defaultdict(list)
    with tarfile.open(base / 'artifacts.tar') as archive:
        for member in archive:
            if member.name not in reports:
                continue
            xml = ET.fromstring(archive.extractfile(member).read())
            tests = xml.findall('testcase')
            assert len(tests) == int(xml.get('tests'))
            for test in tests:
                identity = (test.get('classname') or xml.get('name'), test.get('name'))
                issues = [e for e in test if e.tag in ('failure', 'error', 'skipped')]
                assert len(issues) <= 1
                grouped[identity].append({'status': issues[0].tag if issues else 'passed',
                                          'type': issues[0].get('type') if issues else None,
                                          'stacktrace': issues[0].text or '' if issues else ''})
    totals = dict.fromkeys(('tests', 'failures', 'errors', 'skipped'), 0)
    duplicates = []
    for identity, entries in sorted(grouped.items()):
        totals['tests'] += 1
        if len(entries) > 1:
            assert summary['phase'] == 'breaking' and len(entries) == 2
            assert identity[0] in ('org.pac4j.dropwizard.e2e.EndToEndTest',
                                   'org.pac4j.dropwizard.e2e.EndToEndServletTest')
            assert all(e['status'] == 'error' for e in entries)
            assert {e['type'] for e in entries} == {'javax.ws.rs.ProcessingException', 'java.lang.RuntimeException'}
            teardown = next(e for e in entries if e['type'] == 'java.lang.RuntimeException')
            assert 'AbstractApplicationTest.tearDown' in teardown['stacktrace']
            assert 'java.lang.AbstractMethodError' in teardown['stacktrace']
            duplicates.append({'test_class': identity[0], 'test_name': identity[1],
                               'reported_entries': 2, 'types': [e['type'] for e in entries]})
        status = entries[0]['status']
        assert all(e['status'] == status for e in entries)
        if status != 'passed':
            totals[{'failure': 'failures', 'error': 'errors', 'skipped': 'skipped'}[status]] += 1
    assert len(duplicates) == (6 if summary['phase'] == 'breaking' else 0)
    return {'case_id': summary['case_id'], 'phase': summary['phase'],
            'rule': 'Count each class/method once; retain both request and teardown error entries in raw XML.',
            'raw_xml_counts': summary['aggregate_counts'], 'aggregate_counts': totals,
            'test_identities': [list(k) for k in sorted(grouped)], 'duplicate_test_entries': duplicates}

def main():
    base = ROOT / 'logs/case149_evidence'
    results = [reconcile(base / phase) for phase in ('pre', 'breaking')]
    assert results[0]['test_identities'] == results[1]['test_identities']
    for result, phase in zip(results, ('pre', 'breaking')):
        log = ROOT / f"logs/batch_triage/{result['case_id'][:8]}_{phase}.log"
        matches = re.findall(r'^(?:\[[A-Z]+\] )?Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)[ \t]*$', log.read_text(errors='replace'), re.M)
        assert len(matches) == 1
        assert tuple(map(int, matches[0])) == tuple(result['aggregate_counts'].values())
        with (base / phase / 'reconciled_counts.json').open('x') as stream:
            json.dump(result, stream, indent=2)
        print(phase, result['aggregate_counts'], 'duplicated methods', len(result['duplicate_test_entries']))

if __name__ == '__main__':
    main()
