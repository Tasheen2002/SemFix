"""Save the evidence-backed Case 52 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '4631885da3cfd6601de5d24133fa3828a590ca9e'
RECORD = {'case_id': '4631885da3cfd6601de5d24133fa3828a590ca9e',
 'project': 'junit-quickcheck',
 'dependency_group': 'org.mockito',
 'dependency_artifact': 'mockito-core',
 'old_version': '4.11.0',
 'new_version': '5.4.0',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '1114',
 'breaking_tests': '510',
 'breaking_failures': '1',
 'breaking_errors': '0',
 'test_effect_type': 'TEST_FAILURE',
 'test_effect_subtype': 'TEST_ASSERTION',
 'main_exception': 'java.lang.AssertionError',
 'failure_origin': 'LIBRARY_USED_FOR_TESTING',
 'origin_library': 'org.mockito:mockito-core:5.4.0',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'PROVISIONAL_BEHAVIORAL',
 'behavior_change_type': 'OTHER_BEHAVIORAL_CHANGE',
 'behavior_description': 'Mockito 5.4.0 defaults to inline mocking, intercepting final '
                         'Generator.shrink and returning an unstubbed empty list. Mockito 4.11.0 '
                         'uses subclass mocking, allowing the real final method to reach the '
                         'doShrink stub.',
 'pre_log': 'logs/batch_triage/4631885d_pre.log',
 'breaking_log': 'logs/batch_triage/4631885d_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Reactor totals match Maven and fresh reports. A '
          'disposable BREAKING-image control forces mock-maker-subclass and the exact failing test '
          'passes with Mockito 5.4.0 retained. Default plugin disassembly and final source method '
          'support the diagnosis. Full upgraded suite under the override was not run. Human review '
          "pending. The tee pipeline masks Maven's failing exit code. See results/case52_review.md "
          'and logs/case52_evidence/.'}


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
            raise ValueError('Case 52 differs from saved record; no changes made')
        print(f'Case 52 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case52.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case52.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 52 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
