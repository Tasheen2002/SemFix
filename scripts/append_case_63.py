"""Save the evidence-backed Case 63 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '5275fc9ef87a6d411b719d78c681b81ac914798b'
RECORD = {'case_id': '5275fc9ef87a6d411b719d78c681b81ac914798b',
 'project': 'JsonUnit',
 'dependency_group': 'org.apache.maven.surefire',
 'dependency_artifact': 'surefire-junit4',
 'old_version': '3.0.0-M5',
 'new_version': '3.0.0-M6',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '3566',
 'breaking_tests': '3564',
 'breaking_failures': '0',
 'breaking_errors': '0',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'ERROR',
 'main_exception': 'java.lang.NoSuchMethodError',
 'failure_origin': 'LIBRARY_USED_FOR_TESTING',
 'origin_library': 'org.apache.maven.surefire:surefire-junit4:3.0.0-M6',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'Surefire Plugin 3.0.0-M5 calls a DirectoryScannerParameters constructor '
                         'absent from the API 3.0.0-M6 brought in by the provider update. The '
                         'test-junit4 runner fails before executing tests.',
 'pre_log': 'logs/batch_triage/5275fc9e_pre.log',
 'breaking_log': 'logs/batch_triage/5275fc9e_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Fresh reports and Maven reactor totals agree. '
          'The affected nested test-junit4 POM is saved separately from the general archive. '
          'Resolved API and caller disassembly verify the constructor mismatch. The tee pipeline '
          'masks Maven failure. See results/case63_review.md and logs/case63_evidence/.'}


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
            raise ValueError('Case 63 differs from saved record; no changes made')
        print(f'Case 63 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case63.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case63.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 63 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
