"""Save the evidence-backed Case 21 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '1c3529eaf282deb4868f4b13439170ef47db3e8c'
RECORD = {'case_id': '1c3529eaf282deb4868f4b13439170ef47db3e8c',
 'project': 'avans',
 'dependency_group': 'com.fasterxml.jackson.dataformat',
 'dependency_artifact': 'jackson-dataformat-cbor',
 'old_version': '2.4.0',
 'new_version': '2.13.3',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '69',
 'breaking_tests': '69',
 'breaking_failures': '1',
 'breaking_errors': '3',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'JAVA_ERROR',
 'main_exception': 'java.lang.NoClassDefFoundError',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'com.fasterxml.jackson.dataformat:jackson-dataformat-cbor:2.13.3',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'CBOR 2.13.3 requires TSFBuilder, absent from the resolved Jackson Core '
                         '2.4.2. SpyMemcachedSessionStore static initialization fails. Later '
                         'class-initialization errors and the HTTP 500 assertion are downstream '
                         'effects.',
 'pre_log': 'logs/batch_triage/1c3529ea_pre.log',
 'breaking_log': 'logs/batch_triage/1c3529ea_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Counts are whole reactor totals. Both runs skip '
          'two tests. The affected module reports four tests. Supplemental XML captures the avans '
          'module omitted by the archive helper. JAR inspection confirms TSFBuilder is referenced '
          'by the CBOR factory and absent from Core. The tee pipeline masks the Maven exit code. '
          'See results/case21_review.md and logs/case21_evidence/.'}


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
            raise ValueError('Case 21 differs from saved record; no changes made')
        print(f'Case 21 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case21.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case21.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 21 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
