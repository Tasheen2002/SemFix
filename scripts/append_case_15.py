"""Save the evidence-backed Case 15 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '14e2c8d47384137d1fff33d9a1441af3d1ef29a3'
RECORD = {
    'case_id': CASE_ID,
    'project': 'pay-adminusers',
    'dependency_group': 'org.slf4j',
    'dependency_artifact': 'slf4j-api',
    'old_version': '1.7.36',
    'new_version': '2.0.5',
    'bump_category': 'TEST_FAILURE',
    'pre_build_status': 'SUCCESS',
    'breaking_build_status': 'FAILURE',
    'pre_tests': '747',
    'breaking_tests': '715',
    'breaking_failures': '0',
    'breaking_errors': '12',
    'test_effect_type': 'TEST_ERROR',
    'test_effect_subtype': 'RUNTIME_EXCEPTION',
    'main_exception': 'java.lang.ClassCastException',
    'failure_origin': 'CLIENT',
    'origin_library': 'org.slf4j:slf4j-api:2.0.5',
    'binary_linkage_incompatibility': 'NO',
    'behavioral_status': 'PROVISIONAL_BEHAVIORAL',
    'behavior_change_type': 'OTHER_BEHAVIORAL_CHANGE',
    'behavior_description': (
        'SLF4J 2.0.5 ignores the existing Logback 1.2.11 binding and returns '
        'NOPLogger. Unchanged client test code casts it to Logback Logger, '
        'causing ClassCastException; Dropwizard resource tests also fail '
        'during logging initialization.'
    ),
    'pre_log': 'logs/batch_triage/14e2c8d4_pre.log',
    'breaking_log': 'logs/batch_triage/14e2c8d4_breaking.log',
    'review_status': 'PENDING_HUMAN_REVIEW',
    'reviewer_1_label': '',
    'reviewer_2_label': '',
    'final_label': '',
    'notes': (
        'Assessment author: CODEX_AGENT; evidence-backed provisional analysis, '
        'not a human-reviewed or final semantic label. PRE: 747 tests, 0 failures, '
        '0 errors, 0 skipped, BUILD SUCCESS. BREAKING: 715 reported tests, '
        '0 failures, 12 errors, 0 skipped, BUILD FAILURE. Eight logger-cast '
        'errors and four class-initialization errors. Four resource classes '
        'exercise 36 PRE tests but produce four BREAKING error entries; the '
        'net reduction of 32 is not skipped/passing tests. Later Could not '
        'initialize class errors are secondary to Unable to acquire the logger '
        'context; no primary binary-linkage failure identified. All 440 source '
        'files match; the only POM change and affected test classpath path '
        'difference is SLF4J 1.7.36 to 2.0.5. See results/case15_review.md, '
        'results/case15_assessment.json, and logs/case15_evidence/. '
        'No repair attempted; independent human review remains pending.'
    ),
}


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
            raise ValueError('Case 15 differs from saved record; no changes made')
        print(f'Case 15 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case15.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case15.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 15 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
