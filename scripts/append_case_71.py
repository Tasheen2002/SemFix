"""Save the evidence-backed Case 71 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '5743793a5d54e43d9acf27e46fdb3a257ee0196f'
RECORD = {'case_id': '5743793a5d54e43d9acf27e46fdb3a257ee0196f',
 'project': 'java-pubsublite',
 'dependency_group': 'com.google.flogger',
 'dependency_artifact': 'google-extensions',
 'old_version': '0.6',
 'new_version': '0.7.1',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '372',
 'breaking_tests': '331',
 'breaking_failures': '0',
 'breaking_errors': '123',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'LINKAGE_ERROR',
 'main_exception': 'java.lang.NoSuchMethodError',
 'failure_origin': 'LIBRARY',
 'origin_library': 'com.google.flogger:flogger:0.7.1',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': "Flogger's retained 0.6 system backend calls a StaticMethodCaller method "
                         'removed in resolved Flogger 0.7.1. Logging initialization fails and '
                         'causes test error cascades.',
 'pre_log': 'logs/batch_triage/5743793a_pre.log',
 'breaking_log': 'logs/batch_triage/5743793a_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Six tests have duplicate setup and teardown '
          'error entries in raw Surefire XML. Unique-test counts match Maven, with 331 tests and '
          '123 errors. The tee pipeline masks Maven failure. See results/case71_review.md and '
          'logs/case71_evidence/.'}


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
            raise ValueError('Case 71 differs from saved record; no changes made')
        print(f'Case 71 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case71.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case71.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 71 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
