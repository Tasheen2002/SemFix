"""Save the evidence-backed Case 88 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '78445745997d3ebe5d1e35d9762d95af875c85ec'
RECORD = {'case_id': '78445745997d3ebe5d1e35d9762d95af875c85ec',
 'project': 'missinglink',
 'dependency_group': 'org.codehaus.plexus',
 'dependency_artifact': 'plexus-utils',
 'old_version': '3.5.0',
 'new_version': '4.0.0',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '68',
 'breaking_tests': '68',
 'breaking_failures': '0',
 'breaking_errors': '14',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'LINKAGE_ERROR',
 'main_exception': 'java.lang.NoClassDefFoundError',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'org.codehaus.plexus:plexus-utils:4.0.0',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'Plexus Utils 4.0.0 lacks XmlStreamReader, which exists in 3.5.0. The '
                         'missing class causes 14 errors during Maven plugin test setup.',
 'pre_log': 'logs/batch_triage/78445745_pre.log',
 'breaking_log': 'logs/batch_triage/78445745_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Maven reactor totals match fresh XML. Automated '
          'triage records the last module only. Resolved JAR entries corroborate the missing '
          'class. See results/case88_review.md and logs/case88_evidence/.'}


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
            raise ValueError('Case 88 differs from saved record; no changes made')
        print(f'Case 88 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case88.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case88.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 88 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
