"""Save the evidence-backed Case 60 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '4ef12d5388d4d32000a9e598c2ae29a5842e80df'
RECORD = {'case_id': '4ef12d5388d4d32000a9e598c2ae29a5842e80df',
 'project': 'IDS-Messaging-Services',
 'dependency_group': 'org.junit.platform',
 'dependency_artifact': 'junit-platform-surefire-provider',
 'old_version': '1.0.3',
 'new_version': '1.3.2',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '32',
 'breaking_tests': '18',
 'breaking_failures': '0',
 'breaking_errors': '0',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'ERROR',
 'main_exception': 'java.lang.NoSuchMethodError',
 'failure_origin': 'LIBRARY_USED_FOR_TESTING',
 'origin_library': 'org.junit.platform:junit-platform-surefire-provider:1.3.2',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'The clearinghouse module upgrades the JUnit provider to 1.3.2 while '
                         'Surefire stays at 2.19.1. The mixed plugin classpath contains '
                         'common-java5 2.22.0, whose StringUtils lacks requireNonNull(Object). The '
                         'clearinghouse test runner fails before executing tests.',
 'pre_log': 'logs/batch_triage/4ef12d53_pre.log',
 'breaking_log': 'logs/batch_triage/4ef12d53_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Fresh XML and Maven give 32 PRE and 18 BREAKING '
          'tests across the reactor. Automated triage counts the last zero-test module only. The '
          'tee pipeline masks Maven failure. See results/case60_review.md and '
          'logs/case60_evidence/.'}


def main():
    path = Path(__file__).resolve().parents[1] / 'results' / 'behavioral_classification.csv'
    original = path.read_bytes()
    reader = csv.DictReader(io.StringIO(original.decode('utf-8-sig'), newline=''))
    fields = reader.fieldnames
    rows = list(reader)
    if not fields or len(fields) != len(RECORD) or set(fields) != set(RECORD):
        raise ValueError('Classification CSV schema differs; no changes made')
    ids = [row['case_id'] for row in rows]
    if len(ids) != len(set(ids)) or any(not value for value in ids):
        raise ValueError('Missing/duplicate case IDs; no changes made')
    existing = [row for row in rows if row['case_id'] == CASE_ID]
    if existing:
        if existing[0] != RECORD:
            raise ValueError('Case 60 differs from saved record; no changes made')
        print(f'Case 60 already recorded; no changes made. Total: {len(rows)}')
        return
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError('Malformed existing classification row; no changes made')
    extra = io.StringIO(newline='')
    csv.DictWriter(extra, fieldnames=fields).writerow(RECORD)
    separator = b'' if original.endswith((b'\n', b'\r')) else b'\r\n'
    updated = original + separator + extra.getvalue().encode('utf-8')
    # Preserve existing bytes and save a backup before the atomic replacement.
    backup_dir = path.parent / 'backups'
    backup_dir.mkdir(exist_ok=True)
    backup = backup_dir / (path.name + '.before_case60.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case60.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 60 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
