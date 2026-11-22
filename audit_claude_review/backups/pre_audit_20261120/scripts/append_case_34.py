"""Save the evidence-backed Case 34 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '2f9d75d4b01cd18afcb4676d134142882f9e0034'
RECORD = {'case_id': '2f9d75d4b01cd18afcb4676d134142882f9e0034',
 'project': 'directory-scimple',
 'dependency_group': 'javax',
 'dependency_artifact': 'javaee-api',
 'old_version': '7.0',
 'new_version': '8.0.1',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '717',
 'breaking_tests': '686',
 'breaking_failures': '0',
 'breaking_errors': '10',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'JAVA_ERROR',
 'main_exception': 'java.lang.AbstractMethodError',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'javax:javaee-api:8.0.1',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'Java EE API 8.0.1 adds the abstract ResponseBuilder.status(int, String) '
                         'overload. The resolved RESTEasy 3.0.11.Final ResponseBuilderImpl lacks '
                         'that implementation, causing nine AbstractMethodErrors and one follow-on '
                         'Mockito setup error.',
 'pre_log': 'logs/batch_triage/2f9d75d4_pre.log',
 'breaking_log': 'logs/batch_triage/2f9d75d4_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Counts are reactor totals. scim-server-common '
          'fails and downstream modules are skipped. Disassembly confirms the API and '
          'implementation mismatch. The tee pipeline masks the failing Maven exit code. See '
          'results/case34_review.md and logs/case34_evidence/.'}


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
            raise ValueError('Case 34 differs from saved record; no changes made')
        print(f'Case 34 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case34.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case34.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 34 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
