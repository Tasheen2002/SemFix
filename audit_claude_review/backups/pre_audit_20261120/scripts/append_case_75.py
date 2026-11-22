"""Save the evidence-backed Case 75 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '5effea24fcd960f5659130912daf5e1d6319c9f4'
RECORD = {'case_id': '5effea24fcd960f5659130912daf5e1d6319c9f4',
 'project': 'dropwizard-pac4j',
 'dependency_group': 'org.eclipse.jetty',
 'dependency_artifact': 'jetty-server',
 'old_version': '9.4.35.v20201120',
 'new_version': '9.4.50.v20221201',
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
 'origin_library': 'org.eclipse.jetty:jetty-server:9.4.50.v20221201',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'The newer Jetty Server listener lacks lifeCycleFailure, which remains '
                         'abstract in Jetty Util 9.4.35. All ten errored tests encounter binary '
                         'dispatch failure during shutdown, with HTTP errors also recorded in six '
                         'end-to-end tests.',
 'pre_log': 'logs/batch_triage/5effea24_pre.log',
 'breaking_log': 'logs/batch_triage/5effea24_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Six tests have duplicate HTTP and teardown '
          "entries in raw Surefire XML. Counting each test once matches Maven's 16 tests and ten "
          'errors. Resolved JAR declarations confirm the linkage mismatch. The HTTP symptom was '
          'not isolated separately. The tee pipeline masks Maven failure. See '
          'results/case75_review.md and logs/case75_evidence/.'}


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
            raise ValueError('Case 75 differs from saved record; no changes made')
        print(f'Case 75 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case75.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case75.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 75 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
