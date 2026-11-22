"""Save the evidence-backed Case 188 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = 'ff98f9e99811cd3186d3819d19b5b7f8143a0632'
RECORD = {'case_id': 'ff98f9e99811cd3186d3819d19b5b7f8143a0632',
 'project': 'Refactoring-Bot',
 'dependency_group': 'org.antlr',
 'dependency_artifact': 'antlr4-runtime',
 'old_version': '4.7.2',
 'new_version': '4.10',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '62',
 'breaking_tests': '62',
 'breaking_failures': '0',
 'breaking_errors': '1',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'RUNTIME_EXCEPTION',
 'main_exception': 'java.lang.ExceptionInInitializerError',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'org.antlr:antlr4-runtime:4.10',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'NON_BEHAVIORAL',  # [Label corrected 2026-11-20, approved by the researcher (Option A)] was PROVISIONAL_BEHAVIORAL
 'behavior_change_type': '',  # was OTHER_BEHAVIORAL_CHANGE
 'behavior_description': 'ANTLR 4.10 rejects version 3 of the serialized ATN '
                         'embedded in the unchanged generated lexer. The same '
                         'compiled lexer and probe initialize successfully '
                         'with runtime 4.7.2. Both expose deserialize(char[]), '
                         'and the updated method reaches format validation and '
                         'expects version 4.',
 'pre_log': 'logs/batch_triage/ff98f9e9_pre.log',
 'breaking_log': 'logs/batch_triage/ff98f9e9_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending independent human review. Both original '
          'Docker images were run. See results/case188_review.md and '
          'logs/case188_evidence/.'}


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
            raise ValueError('Case 188 differs from saved record; no changes made')
        print(f'Case 188 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case188.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case188.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 188 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
