"""Reconcile duplicate TestNG report formats against fresh top-level Surefire XML."""
import argparse
from collections import Counter
import json
from pathlib import Path
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=('pre', 'breaking'), required=True)
    phase = parser.parse_args().phase
    base = ROOT / 'logs/case105_evidence' / phase
    summary = json.loads((base / 'archive_summary.json').read_text())
    selected = [r for r in summary['reports'] if '/surefire-reports/junitreports/' not in r['path']]
    excluded = [r for r in summary['reports'] if '/surefire-reports/junitreports/' in r['path']]
    selected_paths = {r['path'] for r in selected}
    excluded_paths = {r['path'] for r in excluded}
    top = Counter()
    nested = Counter()
    with tarfile.open(base / 'artifacts.tar') as archive:
        for member in archive:
            if member.name not in selected_paths | excluded_paths:
                continue
            xml = ET.fromstring(archive.extractfile(member).read())
            module = member.name.split('/target/')[0]
            target = nested if member.name in excluded_paths else top
            for test in xml.iter('testcase'):
                status = next((k for k in ('failure', 'error', 'skipped') if test.find(k) is not None), 'passed')
                target[(module, test.get('classname'), test.get('name'), status)] += 1
    if nested - top:
        raise ValueError('Excluded TestNG reports contain nonduplicate test identities/statuses')
    totals = {k: sum(r['counts'][k] for r in selected) for k in ('tests', 'failures', 'errors', 'skipped')}
    duplicates = {k: sum(r['counts'][k] for r in excluded) for k in totals}
    if sum(nested.values()) != duplicates['tests']:
        raise ValueError('Excluded report testcase count differs from headers')
    if sum(top.values()) != totals['tests']:
        raise ValueError('Included report testcase count differs from headers')
    result = {'phase': phase, 'rule': 'Include top-level Surefire XML; exclude nested TestNG junitreports only after matching test identities and statuses to included reports.', 'raw_xml_counts': summary['aggregate_counts'], 'aggregate_counts': totals, 'duplicate_format_counts': duplicates, 'included_reports': sorted(selected_paths), 'excluded_reports': sorted(excluded_paths), 'duplicate_test_identities_and_statuses_verified': True}
    with (base / 'reconciled_counts.json').open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
