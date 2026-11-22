"""Save the evidence-backed Case 22 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '1ca02168f00f994c625eeea6b5af4ab0a06f3a27'
RECORD = {'case_id': '1ca02168f00f994c625eeea6b5af4ab0a06f3a27',
 'project': 'sign-maven-plugin',
 'dependency_group': 'org.slf4j',
 'dependency_artifact': 'slf4j-api',
 'old_version': '1.7.36',
 'new_version': '2.0.0',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '38',
 'breaking_tests': '38',
 'breaking_failures': '0',
 'breaking_errors': '12',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'RUNTIME_EXCEPTION',
 'main_exception': 'java.lang.ClassCastException',
 'failure_origin': 'LIBRARY_USED_FOR_TESTING',
 'origin_library': 'org.simplify4u:slf4j-mock:2.2.0',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'PROVISIONAL_BEHAVIORAL',
 'behavior_change_type': 'OTHER_BEHAVIORAL_CHANGE',
 'behavior_description': 'SLF4J 2.0.0 ignores the legacy slf4j-mock 2.2.0 binding and returns '
                         'NOPLogger. The unchanged test library casts it to ProxyMock during '
                         'Mockito setup, causing 12 ClassCastException errors.',
 'pre_log': 'logs/batch_triage/1ca02168_pre.log',
 'breaking_log': 'logs/batch_triage/1ca02168_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. The call site is '
          'LoggerAnnotationEngine.findLoggersMocks. Maven and fresh Surefire totals agree. The tee '
          'pipeline masks the Maven exit code. See results/case22_review.md and '
          'logs/case22_evidence/.'}


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
            raise ValueError('Case 22 differs from saved record; no changes made')
        print(f'Case 22 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case22.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case22.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 22 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
