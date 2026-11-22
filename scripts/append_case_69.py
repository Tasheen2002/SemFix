"""Save the evidence-backed Case 69 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '56b1cde573f7b411a3a831bed30c624ddfdbdf3d'
RECORD = {'case_id': '56b1cde573f7b411a3a831bed30c624ddfdbdf3d',
 'project': 'a',
 'dependency_group': 'org.graalvm.js',
 'dependency_artifact': 'js-scriptengine',
 'old_version': '22.0.0',
 'new_version': '22.1.0',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '80',
 'breaking_tests': '80',
 'breaking_failures': '3',
 'breaking_errors': '9',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'RUNTIME_EXCEPTION',
 'main_exception': 'java.lang.IllegalArgumentException',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'org.graalvm.js:js-scriptengine:22.1.0',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'NON_BEHAVIORAL',  # [Label corrected 2026-11-20, approved by the researcher (Option A)] was PROVISIONAL_BEHAVIORAL
 'behavior_change_type': '',  # was OTHER_BEHAVIORAL_CHANGE
 'behavior_description': 'ScriptEngine 22.1.0 adds js.charset=UTF-8 to default context '
                         'configuration. The retained GraalJS 22.0.0 runtime rejects the new '
                         'option and message transformations abort.',
 'pre_log': 'logs/batch_triage/56b1cde5_pre.log',
 'breaking_log': 'logs/batch_triage/56b1cde5_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Three broker suites reproduce the same pattern. '
          'Same-environment probe changes only ScriptEngine and reproduces the option rejection '
          'without messaging. Maven and fresh XML agree. The tee pipeline masks Maven failure. See '
          'results/case69_review.md and logs/case69_evidence/.'}


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
            raise ValueError('Case 69 differs from saved record; no changes made')
        print(f'Case 69 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case69.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case69.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 69 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
