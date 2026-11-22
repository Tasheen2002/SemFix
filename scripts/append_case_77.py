"""Save the evidence-backed Case 77 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '60c05d7f413430e47f624cc3c7b13c97466c6bb3'
RECORD = {'case_id': '60c05d7f413430e47f624cc3c7b13c97466c6bb3',
 'project': 'http',
 'dependency_group': 'org.junit.jupiter',
 'dependency_artifact': 'junit-jupiter-engine',
 'old_version': '5.8.1',
 'new_version': '5.10.0',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '906',
 'breaking_tests': '0',
 'breaking_failures': '0',
 'breaking_errors': '0',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'ERROR',
 'main_exception': 'java.lang.NoSuchMethodError',
 'failure_origin': 'LIBRARY_USED_FOR_TESTING',
 'origin_library': 'org.junit.platform:junit-platform-launcher:1.10.0',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': "The Surefire plugin's Jupiter Engine update resolves Platform Launcher "
                         '1.10.0, which invokes TestDescriptor.getAncestors() while the project '
                         'test classpath retains Platform Engine 1.8.2. The fork fails before '
                         'tests run.',
 'pre_log': 'logs/batch_triage/60c05d7f_pre.log',
 'breaking_log': 'logs/batch_triage/60c05d7f_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. PRE runs the same 453 tests in two Surefire '
          'executions, giving 906 executions and one final set of 453 XML cases. The original fork '
          'dump and a Maven debug run identify NoSuchMethodError and the mixed classpath. The main '
          'log omits the exception class. The tee pipeline masks Maven failure. See '
          'results/case77_review.md and logs/case77_evidence/.'}


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
            raise ValueError('Case 77 differs from saved record; no changes made')
        print(f'Case 77 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case77.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case77.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 77 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
