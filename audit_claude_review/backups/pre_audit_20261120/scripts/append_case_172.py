"""Save the evidence-backed Case 172 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = 'e35a97cf177d8cd7d022c4adca7da24f1a17a2eb'
RECORD = {'case_id': 'e35a97cf177d8cd7d022c4adca7da24f1a17a2eb',
 'project': 'recheck.cli',
 'dependency_group': 'ch.qos.logback',
 'dependency_artifact': 'logback-classic',
 'old_version': '1.2.11',
 'new_version': '1.4.5',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '12',
 'breaking_tests': '12',
 'breaking_failures': '2',
 'breaking_errors': '0',
 'test_effect_type': 'TEST_FAILURE',
 'test_effect_subtype': 'LINKAGE_ERROR',
 'main_exception': 'java.lang.AssertionError',
 'failure_origin': 'LIBRARY',
 'origin_library': 'ch.qos.logback:logback-classic:1.4.5',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'Logback Classic 1.4.5 no longer includes '
                         'StaticLoggerBinder, which retained SLF4J 1.7.36 '
                         'directly calls. Its missing-class fallback '
                         'suppresses warnings and prompts, leading to two '
                         'assertions against empty output.',
 'pre_log': 'logs/batch_triage/e35a97cf_pre.log',
 'breaking_log': 'logs/batch_triage/e35a97cf_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending independent human review. Both original '
          'Docker images were run. See results/case172_review.md and '
          'logs/case172_evidence/.'}


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
            raise ValueError('Case 172 differs from saved record; no changes made')
        print(f'Case 172 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case172.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case172.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 172 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
