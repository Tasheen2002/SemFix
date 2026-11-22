"""Save the evidence-backed Case 90 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '80a534da02670221e857647dda3ce3546c76b75e'
RECORD = {'case_id': '80a534da02670221e857647dda3ce3546c76b75e',
 'project': 'recheck',
 'dependency_group': 'org.slf4j',
 'dependency_artifact': 'slf4j-api',
 'old_version': '1.7.36',
 'new_version': '2.0.5',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '737',
 'breaking_tests': '737',
 'breaking_failures': '0',
 'breaking_errors': '30',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'RUNTIME_EXCEPTION',
 'main_exception': 'java.lang.ClassCastException',
 'failure_origin': 'LIBRARY_USED_FOR_TESTING',
 'origin_library': 'org.slf4j:slf4j-api:2.0.5',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'PROVISIONAL_BEHAVIORAL',
 'behavior_change_type': 'OTHER_BEHAVIORAL_CHANGE',
 'behavior_description': 'SLF4J 2.0.5 ignores the retained Logback binding and selects a '
                         'no-operation logger. LogUnit casts it to a Logback Logger and reports 30 '
                         'errors.',
 'pre_log': 'logs/batch_triage/80a534da_pre.log',
 'breaking_log': 'logs/batch_triage/80a534da_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Resolved JAR inspection verifies the old binding '
          'remains present. Maven and fresh XML agree. The tee pipeline masks Maven failure. See '
          'results/case90_review.md and logs/case90_evidence/.'}


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
            raise ValueError('Case 90 differs from saved record; no changes made')
        print(f'Case 90 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case90.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case90.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 90 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
