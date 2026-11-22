"""Save the evidence-backed Case 109 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '94380c9eb5be989b7e60e0353a03b03ff4687674'
RECORD = {'case_id': '94380c9eb5be989b7e60e0353a03b03ff4687674',
 'project': 'dependency-track-maven-plugin',
 'dependency_group': 'com.google.inject',
 'dependency_artifact': 'guice',
 'old_version': '5.1.0',
 'new_version': '7.0.0',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '223',
 'breaking_tests': '223',
 'breaking_failures': '0',
 'breaking_errors': '54',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'JAVA_ERROR',
 'main_exception': 'java.lang.ExceptionInInitializerError',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'com.google.inject:guice:7.0.0',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'PROVISIONAL_BEHAVIORAL',
 'behavior_change_type': 'OTHER_BEHAVIORAL_CHANGE',
 'behavior_description': 'Guice 7.0.0 no longer recognizes javax.inject.Qualifier as a '
                         'binding-annotation marker. Sisu Parameters remains present but Key.get '
                         'rejects it with IllegalArgumentException; ParameterKeys initialization '
                         'fails and 53 further errors cascade.',
 'pre_log': 'logs/batch_triage/94380c9e_pre.log',
 'breaking_log': 'logs/batch_triage/94380c9e_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending independent human review; not a final semantic label. Both '
          'original Docker images were run. See results/case109_review.md and '
          'logs/case109_evidence/. No repair attempted.'}


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
            raise ValueError('Case 109 differs from saved record; no changes made')
        print(f'Case 109 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case109.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case109.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 109 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
