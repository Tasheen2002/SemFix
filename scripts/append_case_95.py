"""Save the evidence-backed Case 95 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '87fbea62fa6867b8288295b80718c51981ae340a'
RECORD = {'case_id': '87fbea62fa6867b8288295b80718c51981ae340a',
 'project': 'dropwizard-pac4j',
 'dependency_group': 'com.fasterxml.jackson.core',
 'dependency_artifact': 'jackson-databind',
 'old_version': '2.10.5.1',
 'new_version': '2.13.4.2',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '16',
 'breaking_tests': '16',
 'breaking_failures': '0',
 'breaking_errors': '16',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'LINKAGE_ERROR',
 'main_exception': 'java.lang.NoClassDefFoundError',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'com.fasterxml.jackson.core:jackson-databind:2.13.4.2',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'Jackson Databind 2.13.4.2 references JacksonFeature, absent from '
                         'retained Jackson Core 2.10.5. All 16 tests report the missing type.',
 'pre_log': 'logs/batch_triage/87fbea62_pre.log',
 'breaking_log': 'logs/batch_triage/87fbea62_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Resolved JAR inspection corroborates the missing '
          'class. Maven and fresh XML agree on totals. See results/case95_review.md and '
          'logs/case95_evidence/.'}


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
            raise ValueError('Case 95 differs from saved record; no changes made')
        print(f'Case 95 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case95.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case95.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 95 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
