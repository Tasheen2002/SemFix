"""Save the evidence-backed Case 94 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '8776fe7cd60bd309daf843bc70608ebf963c6761'
RECORD = {'case_id': '8776fe7cd60bd309daf843bc70608ebf963c6761',
 'project': 'wsdoc',
 'dependency_group': 'com.fasterxml.jackson.core',
 'dependency_artifact': 'jackson-databind',
 'old_version': '2.4.2',
 'new_version': '2.12.6.1',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '59',
 'breaking_tests': '59',
 'breaking_failures': '33',
 'breaking_errors': '0',
 'test_effect_type': 'TEST_FAILURE',
 'test_effect_subtype': 'LINKAGE_ERROR',
 'main_exception': 'java.lang.NoClassDefFoundError',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'com.fasterxml.jackson.core:jackson-databind:2.12.6.1',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'Updated Jackson Databind references JsonMerge, absent from retained '
                         'Jackson Annotations 2.4.1. The missing type prevents ObjectMapper '
                         'initialization and results in 33 reported failures.',
 'pre_log': 'logs/batch_triage/8776fe7c_pre.log',
 'breaking_log': 'logs/batch_triage/8776fe7c_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Use Maven and suite-level XML counts. Nested '
          'TestNG per-class reports duplicate the executions. Resolved JAR inspection corroborates '
          'the missing type. See results/case94_review.md and logs/case94_evidence/.'}


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
            raise ValueError('Case 94 differs from saved record; no changes made')
        print(f'Case 94 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case94.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case94.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 94 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
