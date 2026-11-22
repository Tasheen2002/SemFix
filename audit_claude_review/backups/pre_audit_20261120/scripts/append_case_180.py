"""Save the evidence-backed Case 180 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = 'f951ead97d14eb29e625d14c2ed5258949728ee4'
RECORD = {'case_id': 'f951ead97d14eb29e625d14c2ed5258949728ee4',
 'project': 'billy',
 'dependency_group': 'org.hibernate.validator',
 'dependency_artifact': 'hibernate-validator',
 'old_version': '6.1.7.Final',
 'new_version': '7.0.2.Final',
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
 'failure_origin': 'LIBRARY',
 'origin_library': 'org.hibernate.validator:hibernate-validator:7.0.2.Final',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'Hibernate Validator 7.0.2.Final advertises a Jakarta '
                         'Bean Validation provider. BillyValidator uses the '
                         'retained javax Validation API and cannot discover a '
                         'provider for that namespace. The initializer fails '
                         'and later tests report the failed initialization. '
                         'The reactor stops in billy-core.',
 'pre_log': 'logs/batch_triage/f951ead9_pre.log',
 'breaking_log': 'logs/batch_triage/f951ead9_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending independent human review. Both original '
          'Docker images were run. See results/case180_review.md and '
          'logs/case180_evidence/.'}


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
            raise ValueError('Case 180 differs from saved record; no changes made')
        print(f'Case 180 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case180.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case180.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 180 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
