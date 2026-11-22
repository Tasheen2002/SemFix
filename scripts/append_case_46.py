"""Save the evidence-backed Case 46 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '41164ec5392b2c853ae871f10a9541c055028b36'
RECORD = {'case_id': '41164ec5392b2c853ae871f10a9541c055028b36',
 'project': 'recheck.cli',
 'dependency_group': 'ch.qos.logback',
 'dependency_artifact': 'logback-classic',
 'old_version': '1.2.11',
 'new_version': '1.4.3',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '12',
 'breaking_tests': '12',
 'breaking_failures': '2',
 'breaking_errors': '0',
 'test_effect_type': 'TEST_FAILURE',
 'test_effect_subtype': 'TEST_ASSERTION',
 'main_exception': 'java.lang.AssertionError',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'ch.qos.logback:logback-classic:1.4.3',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'Logback 1.4.3 removes StaticLoggerBinder, directly required by retained '
                         'SLF4J API 1.7.36. SLF4J catches the linkage failure and selects a '
                         'no-operation logger. Two tests then fail because expected warning output '
                         'is empty.',
 'pre_log': 'logs/batch_triage/41164ec5_pre.log',
 'breaking_log': 'logs/batch_triage/41164ec5_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Provisional non-behavioural assessment based on '
          'a missing binary binding class. Human review should adjudicate the provider-transition '
          'boundary. Resolved JARs and SLF4J bytecode verify the missing class and fallback. Maven '
          "and fresh reports agree. The tee pipeline masks Maven's failing exit code. See "
          'results/case46_review.md and logs/case46_evidence/.'}


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
            raise ValueError('Case 46 differs from saved record; no changes made')
        print(f'Case 46 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case46.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case46.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 46 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
