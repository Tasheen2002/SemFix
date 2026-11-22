"""Save the evidence-backed Case 84 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '700fd2428406fdaa4aacf00feab0cbbe634d70c2'
RECORD = {'case_id': '700fd2428406fdaa4aacf00feab0cbbe634d70c2',
 'project': 'dropwizard-pac4j',
 'dependency_group': 'org.eclipse.jetty',
 'dependency_artifact': 'jetty-server',
 'old_version': '9.4.35.v20201120',
 'new_version': '9.4.47.v20220610',
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
 'origin_library': 'org.eclipse.jetty:jetty-server:9.4.47.v20220610',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'The newer Jetty Server listener lacks lifeCycleFailure, required by the '
                         'retained Jetty Util interface. Ten tests encounter shutdown linkage '
                         'errors. Six also record HTTP connection errors.',
 'pre_log': 'logs/batch_triage/700fd242_pre.log',
 'breaking_log': 'logs/batch_triage/700fd242_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Six duplicate HTTP and teardown records in raw '
          'XML are counted once each to reconcile with Maven. Actual JAR declarations confirm the '
          'listener mismatch. The HTTP symptom was not isolated separately. See '
          'results/case84_review.md and logs/case84_evidence/.'}


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
            raise ValueError('Case 84 differs from saved record; no changes made')
        print(f'Case 84 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case84.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case84.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 84 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
