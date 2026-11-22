"""Save the evidence-backed Case 70 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '57062474434f91f25595516ae8b759a53073a40f'
RECORD = {'case_id': '57062474434f91f25595516ae8b759a53073a40f',
 'project': 'geoserver-shell',
 'dependency_group': 'org.json',
 'dependency_artifact': 'json',
 'old_version': '20090211',
 'new_version': '20230227',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '205',
 'breaking_tests': '205',
 'breaking_failures': '0',
 'breaking_errors': '2',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'RUNTIME_EXCEPTION',
 'main_exception': 'org.json.JSONException',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'org.json:json:20230227',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'PROVISIONAL_BEHAVIORAL',
 'behavior_change_type': 'OTHER_BEHAVIORAL_CHANGE',
 'behavior_description': 'JSONObject.getString used to convert numeric session IDs to strings. '
                         'Version 20230227 throws JSONException for the same Integer values, '
                         'breaking both session commands.',
 'pre_log': 'logs/batch_triage/57062474_pre.log',
 'breaking_log': 'logs/batch_triage/57062474_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Maven and fresh XML agree. A same-environment '
          'probe varying only the JSON JAR confirms both parsed values are Integer and only the '
          'new getString rejects the value. Independent human review is pending. The tee pipeline '
          'masks Maven failure. See results/case70_review.md and logs/case70_evidence/.'}


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
            raise ValueError('Case 70 differs from saved record; no changes made')
        print(f'Case 70 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case70.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case70.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 70 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
