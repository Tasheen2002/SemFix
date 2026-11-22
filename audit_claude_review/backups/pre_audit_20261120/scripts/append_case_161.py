"""Save the evidence-backed Case 161 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = 'd9a0df6feee60bb6d7d301f251cab386168eecd1'
RECORD = {'case_id': 'd9a0df6feee60bb6d7d301f251cab386168eecd1',
 'project': 'polyglot-maven',
 'dependency_group': 'org.jetbrains.kotlin',
 'dependency_artifact': 'kotlin-stdlib',
 'old_version': '1.3.31',
 'new_version': '1.6.0',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '302',
 'breaking_tests': '302',
 'breaking_failures': '1',
 'breaking_errors': '0',
 'test_effect_type': 'TEST_FAILURE',
 'test_effect_subtype': 'TEST_ASSERTION',
 'main_exception': 'org.junit.ComparisonFailure',
 'failure_origin': 'CLIENT',
 'origin_library': 'org.jetbrains.kotlin:kotlin-stdlib:1.6.0',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'The expected XML fixture changed its Kotlin stdlib '
                         'version to 1.6.0. The unchanged Kotlin input still '
                         'generates 1.3.31. All 34 test classpaths match, and '
                         'the Kotlin stdlib 1.4.10 JAR has the same hash in '
                         'both images.',
 'pre_log': 'logs/batch_triage/d9a0df6f_pre.log',
 'breaking_log': 'logs/batch_triage/d9a0df6f_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending independent human review. Both original '
          'Docker images were run. See results/case161_review.md and '
          'logs/case161_evidence/.'}


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
            raise ValueError('Case 161 differs from saved record; no changes made')
        print(f'Case 161 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case161.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case161.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 161 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
