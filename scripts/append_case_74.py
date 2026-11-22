"""Save the evidence-backed Case 74 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '5e6846a50737c240be6fedb6626f0d32906d10ad'
RECORD = {'case_id': '5e6846a50737c240be6fedb6626f0d32906d10ad',
 'project': 'IDS-Messaging-Services',
 'dependency_group': 'org.springframework',
 'dependency_artifact': 'spring-tx',
 'old_version': '5.3.24',
 'new_version': '6.0.3',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '32',
 'breaking_tests': '18',
 'breaking_failures': '0',
 'breaking_errors': '5',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'LINKAGE_ERROR',
 'main_exception': 'org.springframework.beans.BeanInstantiationException',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'org.springframework:spring-tx:6.0.3',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'Spring TX 6.0.3 uses Java 17 bytecode. Java 11 rejects '
                         'TransactionDefinition during Spring test listener setup, producing five '
                         'errors wrapping UnsupportedClassVersionError.',
 'pre_log': 'logs/batch_triage/5e6846a5_pre.log',
 'breaking_log': 'logs/batch_triage/5e6846a5_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Maven and fresh reports agree on reactor totals. '
          'The automated screen reports only the last module. Resolved class headers corroborate '
          'the 61 versus 55 incompatibility. The tee pipeline masks Maven failure. See '
          'results/case74_review.md and logs/case74_evidence/.'}


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
            raise ValueError('Case 74 differs from saved record; no changes made')
        print(f'Case 74 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case74.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case74.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 74 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
