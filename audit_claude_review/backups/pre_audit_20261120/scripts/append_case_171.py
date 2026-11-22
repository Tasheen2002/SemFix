"""Save the evidence-backed Case 171 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = 'e0f2562e849012538cd30e2730c82991983f4eba'
RECORD = {'case_id': 'e0f2562e849012538cd30e2730c82991983f4eba',
 'project': 'dropwizard-pac4j',
 'dependency_group': 'org.slf4j',
 'dependency_artifact': 'slf4j-api',
 'old_version': '1.7.30',
 'new_version': '2.0.0',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '16',
 'breaking_tests': '16',
 'breaking_failures': '0',
 'breaking_errors': '10',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'RUNTIME_EXCEPTION',
 'main_exception': 'java.lang.IllegalStateException',
 'failure_origin': 'LIBRARY',
 'origin_library': 'org.slf4j:slf4j-api:2.0.0',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'PROVISIONAL_BEHAVIORAL',
 'behavior_change_type': 'OTHER_BEHAVIORAL_CHANGE',
 'behavior_description': 'SLF4J 2.0.0 ignores the present legacy Logback 1.2.3 '
                         'binding and selects NOP logging. Dropwizard cannot '
                         'obtain the expected logger context during test '
                         'server startup, leading to ten setup errors. The '
                         'original runtime pair and logger probe show the '
                         'provider selection change.',
 'pre_log': 'logs/batch_triage/e0f2562e_pre.log',
 'breaking_log': 'logs/batch_triage/e0f2562e_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending independent human review. Both original '
          'Docker images were run. See results/case171_review.md and '
          'logs/case171_evidence/.'}


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
            raise ValueError('Case 171 differs from saved record; no changes made')
        print(f'Case 171 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case171.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case171.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 171 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
