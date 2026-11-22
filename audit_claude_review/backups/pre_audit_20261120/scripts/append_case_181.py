"""Save the evidence-backed Case 181 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = 'fa6503da9fd5431abca41561a34d54e07fbbf7d0'
RECORD = {'case_id': 'fa6503da9fd5431abca41561a34d54e07fbbf7d0',
 'project': 'sparql.anything',
 'dependency_group': 'org.jsoup',
 'dependency_artifact': 'jsoup',
 'old_version': '1.14.2',
 'new_version': '1.15.3',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '240',
 'breaking_tests': '57',
 'breaking_failures': '2',
 'breaking_errors': '0',
 'test_effect_type': 'TEST_FAILURE',
 'test_effect_subtype': 'TEST_ASSERTION',
 'main_exception': 'java.lang.AssertionError',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'org.jsoup:jsoup:1.15.3',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'PROVISIONAL_BEHAVIORAL',
 'behavior_change_type': 'OTHER_BEHAVIORAL_CHANGE',
 'behavior_description': 'jsoup 1.15.3 trims whitespace in Element.html() for '
                         'the existing Microdata1 fixture. SPARQL Anything '
                         'stores that string as an innerHTML RDF literal, so '
                         'the output graph no longer matches the expected '
                         'graph. The isolated probe used identical compiled '
                         'code and fixture bytes in both images. Text '
                         'extraction produced identical output, and the HTML '
                         'serialization check reproduced the changed '
                         'whitespace.',
 'pre_log': 'logs/batch_triage/fa6503da_pre.log',
 'breaking_log': 'logs/batch_triage/fa6503da_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending independent human review. Both original '
          'Docker images were run. See results/case181_review.md and '
          'logs/case181_evidence/.'}


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
            raise ValueError('Case 181 differs from saved record; no changes made')
        print(f'Case 181 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case181.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case181.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 181 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
