"""Save the evidence-backed Case 114 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '9c0f1348f89dffae4ad0d4f7e1906fc8c8ba8dca'
RECORD = {'case_id': '9c0f1348f89dffae4ad0d4f7e1906fc8c8ba8dca',
 'project': 'geostore',
 'dependency_group': 'com.h2database',
 'dependency_artifact': 'h2',
 'old_version': '1.3.175',
 'new_version': '2.1.210',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '190',
 'breaking_tests': '52',
 'breaking_failures': '0',
 'breaking_errors': '22',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'RUNTIME_EXCEPTION',
 'main_exception': 'javax.persistence.PersistenceException',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'com.h2database:h2:2.1.210',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'PROVISIONAL_BEHAVIORAL',
 'behavior_change_type': 'OTHER_BEHAVIORAL_CHANGE',
 'behavior_description': 'H2 2.1.210 rejects Hibernate-generated VARCHAR(10000000), which H2 '
                         '1.3.175 accepted. Schema creation fails at the new precision limit, '
                         'and 22 tests report downstream persistence errors for the missing '
                         'table.',
 'pre_log': 'logs/batch_triage/9c0f1348_pre.log',
 'breaking_log': 'logs/batch_triage/9c0f1348_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending independent human review; not a final semantic label. Both '
          'original Docker images were run. See results/case114_review.md and '
          'logs/case114_evidence/. No repair attempted.'}


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
            raise ValueError('Case 114 differs from saved record; no changes made')
        print(f'Case 114 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case114.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case114.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 114 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
