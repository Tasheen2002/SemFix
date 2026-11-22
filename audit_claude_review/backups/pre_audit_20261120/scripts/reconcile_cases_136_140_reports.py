"""Separate duplicated TestNG exports from Maven Surefire totals."""

import argparse
from collections import Counter
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
COUNT_KEYS = ('tests', 'failures', 'errors', 'skipped')


def reconcile(base):
    summary = json.loads((base / 'archive_summary.json').read_text(encoding='utf-8'))
    selected = [row for row in summary['reports'] if '/surefire-reports/junitreports/' not in row['path']]
    excluded = [row for row in summary['reports'] if '/surefire-reports/junitreports/' in row['path']]
    groups = [{row['path']: row for row in reports} for reports in (selected, excluded)]
    identities = [Counter(), Counter()]
    statuses = [Counter(), Counter()]
    normalized_names = [0, 0]
    found = set()
    disabled_identity = ('choco', 'org.btrplace.scheduler.choco.constraint.CSplitTest', 'testContinuous')
    disabled_source = 'choco/src/test/java/org/btrplace/scheduler/choco/constraint/CSplitTest.java'
    disabled_in_source = False
    with tarfile.open(base / 'artifacts.tar') as archive:
        for member in archive:
            path = PurePosixPath(member.name).as_posix()
            if path == disabled_source:
                source = archive.extractfile(member).read().decode('utf-8')
                disabled_in_source = bool(re.search(r'@Test\(enabled\s*=\s*false\)\s+public void testContinuous\(', source))
            for index, group in enumerate(groups):
                if path not in group:
                    continue
                if path in found:
                    raise ValueError(f'Duplicate archived path: {path}')
                found.add(path)
                xml = ET.fromstring(archive.extractfile(member).read())
                for test in xml.iter('testcase'):
                    name = test.get('name')
                    if excluded:
                        # Surefire appends TestNG invocation arguments and an ordinal.
                        # The second export records only the method name. Match multiplicities.
                        normalized = re.sub(r'(?:\[.*\])?\(\d+\)$', '', name)
                        normalized_names[index] += normalized != name
                        name = normalized
                    identity = (group[path]['module'], test.get('classname'), name)
                    status = next((tag for tag in ('failure', 'error', 'skipped') if test.find(tag) is not None), 'passed')
                    identities[index][identity] += 1
                    statuses[index][(*identity, status)] += 1
    nested_only = identities[1] - identities[0]
    disabled_exported = nested_only == Counter({disabled_identity: 1}) and disabled_in_source and statuses[1][(*disabled_identity, 'skipped')] == 1
    if found != groups[0].keys() | groups[1].keys() or (nested_only and not disabled_exported):
        raise ValueError('Nested TestNG identities do not match the selected reports')
    selected_totals = {key: sum(row['counts'][key] for row in selected) for key in COUNT_KEYS}
    excluded_totals = {key: sum(row['counts'][key] for row in excluded) for key in COUNT_KEYS}
    if [sum(group.values()) for group in identities] != [selected_totals['tests'], excluded_totals['tests']]:
        raise ValueError('Test identities and declared counts disagree')
    unmatched_statuses = [{'module': m, 'class': c, 'test': t, 'nested_status': s, 'count': count}
                          for (m, c, t, s), count in (statuses[1] - statuses[0]).items()]
    for item in unmatched_statuses:
        identity = (item['module'], item['class'], item['test'])
        if disabled_exported and identity == disabled_identity:
            continue
        counterpart = {'error': 'failure', 'failure': 'error'}.get(item['nested_status'])
        if counterpart is None or statuses[0][(*identity, counterpart)] < item['count']:
            raise ValueError(f'Unexplained TestNG status difference: {item}')
    result = {'phase': summary['phase'], 'case_id': summary['case_id'], 'raw_xml_counts': summary['aggregate_counts'],
              'aggregate_counts': selected_totals, 'duplicate_format_counts': excluded_totals,
              'included_reports': sorted(groups[0]), 'excluded_reports': sorted(groups[1]),
              'nested_failure_error_label_differences': [item for item in unmatched_statuses
                  if not disabled_exported or (item['module'], item['class'], item['test']) != disabled_identity]}
    if any(normalized_names):
        result['normalized_parameterized_names'] = {'suite': normalized_names[0], 'nested': normalized_names[1]}
    if disabled_exported:
        result['nested_only_disabled_test'] = {'identity': list(disabled_identity), 'source_path': disabled_source}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case_number', type=int, choices=range(136, 141))
    args = parser.parse_args()
    for phase in ('pre', 'breaking'):
        base = ROOT / f'logs/case{args.case_number}_evidence' / phase
        result = reconcile(base)
        with (base / 'reconciled_counts.json').open('x', encoding='utf-8') as output:
            json.dump(result, output, indent=2)
        print(phase, result['aggregate_counts'], 'duplicated entries', result['duplicate_format_counts'], flush=True)


if __name__ == '__main__':
    main()
