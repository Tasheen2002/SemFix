"""Save the evidence-backed Case 99 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '8b372dfe79625ff585c5b0392913b6b152cc7c22'
RECORD = {'case_id': '8b372dfe79625ff585c5b0392913b6b152cc7c22',
 'project': 'dropwizard-pac4j',
 'dependency_group': 'org.eclipse.jetty',
 'dependency_artifact': 'jetty-server',
 'old_version': '9.4.35.v20201120',
 'new_version': '9.4.48.v20220622',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '16',
 'breaking_tests': '16',
 'breaking_failures': '0',
 'breaking_errors': '10',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'LINKAGE_ERROR',
 'main_exception': 'java.lang.AbstractMethodError',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'org.eclipse.jetty:jetty-server:9.4.48.v20220622',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'The updated Jetty listener lacks lifeCycleFailure, required by the '
                         'retained Jetty Util interface. Ten tests record shutdown linkage errors. '
                         'Six also record HTTP connection errors.',
 'pre_log': 'logs/batch_triage/8b372dfe_pre.log',
 'breaking_log': 'logs/batch_triage/8b372dfe_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Six duplicate HTTP and teardown XML entries are '
          'reconciled against Maven. Actual JAR declarations corroborate the listener mismatch. '
          'The HTTP errors were not isolated separately. See results/case99_review.md and '
          'logs/case99_evidence/.'}


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
            raise ValueError('Case 99 differs from saved record; no changes made')
        print(f'Case 99 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case99.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case99.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 99 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
