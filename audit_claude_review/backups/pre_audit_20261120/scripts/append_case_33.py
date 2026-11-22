"""Save the evidence-backed Case 33 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '2cc9522c8f62871d12243b174b98bd7d5b121362'
RECORD = {'case_id': '2cc9522c8f62871d12243b174b98bd7d5b121362',
 'project': 'avans',
 'dependency_group': 'com.fasterxml.jackson.core',
 'dependency_artifact': 'jackson-core',
 'old_version': '2.4.2',
 'new_version': '2.13.3',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '69',
 'breaking_tests': '69',
 'breaking_failures': '1',
 'breaking_errors': '2',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'JAVA_ERROR',
 'main_exception': 'java.lang.NoSuchMethodError',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'com.fasterxml.jackson.core:jackson-core:2.13.3',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'CBOR 2.4.0 calls getOutputContext with the JsonWriteContext return '
                         'descriptor, which Jackson Core 2.13.3 no longer supplies. The resulting '
                         'NoSuchMethodError breaks session serialization and causes the HTTP '
                         'integration assertion to receive 500.',
 'pre_log': 'logs/batch_triage/2cc9522c_pre.log',
 'breaking_log': 'logs/batch_triage/2cc9522c_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Whole reactor totals include directly copied '
          'avans module reports omitted by the default archive. Both runs skip two tests. Copied '
          'module POM and JAR disassembly verify the Core-only update and missing binary '
          "signature. The tee pipeline masks Maven's failing exit code. See "
          'results/case33_review.md and logs/case33_evidence/.'}


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
            raise ValueError('Case 33 differs from saved record; no changes made')
        print(f'Case 33 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case33.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case33.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 33 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
