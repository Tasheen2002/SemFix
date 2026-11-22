"""Save the evidence-backed Case 116 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = 'a047d2d3f9385a25ced0d2ad3c49f9401ea9c624'
RECORD = {'case_id': 'a047d2d3f9385a25ced0d2ad3c49f9401ea9c624',
 'project': 'incrementals-tools',
 'dependency_group': 'org.codehaus.mojo',
 'dependency_artifact': 'versions-maven-plugin',
 'old_version': '2.15.0',
 'new_version': '2.16.0',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '7',
 'breaking_tests': '0',
 'breaking_failures': '0',
 'breaking_errors': '0',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'RUNTIME_EXCEPTION',
 'main_exception': 'org.junit.platform.commons.JUnitException',
 'failure_origin': 'LIBRARY_USED_FOR_TESTING',
 'origin_library': 'org.codehaus.mojo:versions-maven-plugin:2.16.0',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'Versions Maven Plugin 2.16.0 introduces JUnit 3.8.1 through '
                         "reporting/Plexus dependencies. Surefire's Vintage 5.9.3 provider "
                         'refuses that unsupported JUnit version before discovering any tests.',
 'pre_log': 'logs/batch_triage/a047d2d3_pre.log',
 'breaking_log': 'logs/batch_triage/a047d2d3_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending independent human review; not a final semantic label. Both '
          'original Docker images were run. See results/case116_review.md and '
          'logs/case116_evidence/. No repair attempted.'}


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
            raise ValueError('Case 116 differs from saved record; no changes made')
        print(f'Case 116 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case116.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case116.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 116 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
