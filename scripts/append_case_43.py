"""Save the evidence-backed Case 43 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '3b47c247b867ea50405402d650c08c8b5bbc2b8a'
RECORD = {'case_id': '3b47c247b867ea50405402d650c08c8b5bbc2b8a',
 'project': 'a',
 'dependency_group': 'org.graalvm.js',
 'dependency_artifact': 'js-scriptengine',
 'old_version': '22.3.2',
 'new_version': '23.0.0',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '80',
 'breaking_tests': '80',
 'breaking_failures': '0',
 'breaking_errors': '79',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'JAVA_ERROR',
 'main_exception': 'java.lang.UnsupportedClassVersionError',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'org.graalvm.js:js-scriptengine:23.0.0',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'ScriptEngine 23.0.0 supplies GraalJSEngineFactory compiled for Java 17. '
                         'Java 11 rejects it during test setup, causing 79 '
                         'UnsupportedClassVersionError reports.',
 'pre_log': 'logs/batch_triage/3b47c247_pre.log',
 'breaking_log': 'logs/batch_triage/3b47c247_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Maven and fresh reports agree. Both phases '
          'report one skip. Resolved class-file headers change from major 55 to 61. Human review '
          "pending. The tee pipeline masks Maven's failing exit code. See results/case43_review.md "
          'and logs/case43_evidence/.'}


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
            raise ValueError('Case 43 differs from saved record; no changes made')
        print(f'Case 43 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case43.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case43.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 43 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
