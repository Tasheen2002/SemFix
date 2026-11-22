"""Save the evidence-backed Case 119 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = 'a18e08bb3fe120b33a5864ee94305a72290ef831'
RECORD = {'case_id': 'a18e08bb3fe120b33a5864ee94305a72290ef831',
 'project': 'html2pop3',
 'dependency_group': 'ch.qos.logback',
 'dependency_artifact': 'logback-classic',
 'old_version': '1.4.5',
 'new_version': '1.4.6',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '5',
 'breaking_tests': '5',
 'breaking_failures': '0',
 'breaking_errors': '2',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'LINKAGE_ERROR',
 'main_exception': 'java.lang.NoSuchMethodError',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'ch.qos.logback:logback-classic:1.4.6',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'Logback Classic 1.4.6 calls CachingDateFormatter(String, ZoneId, '
                         'Locale), absent from retained Logback Core 1.4.5. Logging '
                         'initialization fails, followed by a cascading FilterTest '
                         'initialization error.',
 'pre_log': 'logs/batch_triage/a18e08bb_pre.log',
 'breaking_log': 'logs/batch_triage/a18e08bb_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending independent human review; not a final semantic label. Both '
          'original Docker images were run. See results/case119_review.md and '
          'logs/case119_evidence/. No repair attempted.'}


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
            raise ValueError('Case 119 differs from saved record; no changes made')
        print(f'Case 119 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case119.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case119.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 119 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
