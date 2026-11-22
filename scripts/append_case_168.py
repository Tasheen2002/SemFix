"""Save the evidence-backed Case 168 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = 'de20387b7a373cf20daa590247a1b65876ebca38'
RECORD = {'case_id': 'de20387b7a373cf20daa590247a1b65876ebca38',
 'project': 'scheduler',
 'dependency_group': 'net.minidev',
 'dependency_artifact': 'json-smart',
 'old_version': '2.4.8',
 'new_version': '2.4.9',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '966',
 'breaking_tests': '617',
 'breaking_failures': '2',
 'breaking_errors': '0',
 'test_effect_type': 'TEST_FAILURE',
 'test_effect_subtype': 'TEST_ASSERTION',
 'main_exception': 'net.minidev.json.parser.ParseException',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'net.minidev:json-smart:2.4.9',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'PROVISIONAL_BEHAVIORAL',
 'behavior_change_type': 'OTHER_BEHAVIORAL_CHANGE',
 'behavior_description': 'JSON Smart 2.4.9 rejects the existing scheduler '
                         'fixtures under its parser nesting restriction. '
                         'IssuesTest.testIssue100 and testIssue101 fail during '
                         'parsing after the same fixtures passed in PRE. '
                         'Counts reconcile duplicate TestNG report formats.',
 'pre_log': 'logs/batch_triage/de20387b_pre.log',
 'breaking_log': 'logs/batch_triage/de20387b_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending independent human review. Both original '
          'Docker images were run. See results/case168_review.md and '
          'logs/case168_evidence/.'}


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
            raise ValueError('Case 168 differs from saved record; no changes made')
        print(f'Case 168 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case168.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case168.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 168 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
