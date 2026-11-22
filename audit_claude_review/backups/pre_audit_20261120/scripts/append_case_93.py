"""Save the evidence-backed Case 93 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '875358af2da44c7f35c3ee17bf2113cd6ec43491'
RECORD = {'case_id': '875358af2da44c7f35c3ee17bf2113cd6ec43491',
 'project': 'billy',
 'dependency_group': 'org.hibernate.validator',
 'dependency_artifact': 'hibernate-validator',
 'old_version': '6.1.7.Final',
 'new_version': '7.0.4.Final',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '279',
 'breaking_tests': '20',
 'breaking_failures': '0',
 'breaking_errors': '19',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'RUNTIME_EXCEPTION',
 'main_exception': 'javax.validation.NoProviderFoundException',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'org.hibernate.validator:hibernate-validator:7.0.4.Final',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'Hibernate Validator 7.0.4.Final registers a Jakarta provider that the '
                         'retained javax API cannot discover. BillyValidator initialization fails '
                         'and 19 tests error.',
 'pre_log': 'logs/batch_triage/875358af_pre.log',
 'breaking_log': 'logs/batch_triage/875358af_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Service lookup is the initiating failure. '
          'Resolved JAR descriptors verify the provider mismatch. Maven reactor totals and fresh '
          'XML agree. See results/case93_review.md and logs/case93_evidence/.'}


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
            raise ValueError('Case 93 differs from saved record; no changes made')
        print(f'Case 93 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case93.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case93.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 93 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
