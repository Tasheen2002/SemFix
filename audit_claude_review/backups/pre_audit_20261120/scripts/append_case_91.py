"""Save the evidence-backed Case 91 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '851e6b1628f8ecb86db912dc5431a496ddf02148'
RECORD = {'case_id': '851e6b1628f8ecb86db912dc5431a496ddf02148',
 'project': 'semantic-metrics',
 'dependency_group': 'com.squareup.okhttp3',
 'dependency_artifact': 'okhttp',
 'old_version': '3.3.1',
 'new_version': '3.14.9',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '111',
 'breaking_tests': '111',
 'breaking_failures': '0',
 'breaking_errors': '2',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'LINKAGE_ERROR',
 'main_exception': 'java.lang.VerifyError',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'com.squareup.okhttp3:okhttp:3.14.9',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'Retained MockWebServer$5 extends RealWebSocket, which becomes final at '
                         'that binary name in OkHttp 3.14.9. JVM verification fails during test '
                         'setup.',
 'pre_log': 'logs/batch_triage/851e6b16_pre.log',
 'breaking_log': 'logs/batch_triage/851e6b16_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. The exact nested class loads with the PRE '
          'classpath and fails with the BREAKING classpath in a focused probe. Maven and fresh XML '
          'agree on reactor counts. See results/case91_review.md and logs/case91_evidence/.'}


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
            raise ValueError('Case 91 differs from saved record; no changes made')
        print(f'Case 91 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case91.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case91.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 91 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
