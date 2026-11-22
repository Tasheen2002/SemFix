"""Save the evidence-backed Case 56 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '4bbf6c2f38c57568196164323ded8ba8aff9953d'
RECORD = {'case_id': '4bbf6c2f38c57568196164323ded8ba8aff9953d',
 'project': 'jasmine-maven-plugin',
 'dependency_group': 'org.slf4j',
 'dependency_artifact': 'slf4j-api',
 'old_version': '1.7.32',
 'new_version': '2.0.1',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '72',
 'breaking_tests': '72',
 'breaking_failures': '2',
 'breaking_errors': '0',
 'test_effect_type': 'TEST_FAILURE',
 'test_effect_subtype': 'TEST_ASSERTION',
 'main_exception': 'java.lang.AssertionError',
 'failure_origin': 'LIBRARY_USED_FOR_TESTING',
 'origin_library': 'org.slf4j:slf4j-api:2.0.1',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'PROVISIONAL_BEHAVIORAL',
 'behavior_change_type': 'OTHER_BEHAVIORAL_CHANGE',
 'behavior_description': 'SLF4J 2.0.1 ignores the retained slf4j-test 1.2.0 legacy binding and '
                         'selects a no-operation logger. JasmineResultLoggerTest.shouldLogHeader '
                         'and shouldLogDetails see an empty message list and fail their header '
                         'assertions.',
 'pre_log': 'logs/batch_triage/4bbf6c2f_pre.log',
 'breaking_log': 'logs/batch_triage/4bbf6c2f_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Both original images ran 72 tests. PRE passed; '
          'BREAKING has two assertions, zero errors/skips. Fresh XML agrees with Maven. Only SLF4J '
          'API changes in archived source/POM and the affected classpath. The actual legacy binder '
          'is present but ignored, supporting provider-selection behavior rather than absent '
          'binary API. Agent assessment only, independent human review pending. No repair '
          'attempted. The tee pipeline masks Maven failure. See results/case56_review.md and '
          'logs/case56_evidence/.'}


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
            raise ValueError('Case 56 differs from saved record; no changes made')
        print(f'Case 56 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case56.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case56.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 56 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
