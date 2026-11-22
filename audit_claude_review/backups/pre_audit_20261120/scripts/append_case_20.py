"""Save the evidence-backed Case 20 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '19e20b0d69cb6dadbc54313cb6c6e5f70670ac93'
RECORD = {'case_id': '19e20b0d69cb6dadbc54313cb6c6e5f70670ac93',
 'project': 'logging-chainsaw',
 'dependency_group': 'com.thoughtworks.xstream',
 'dependency_artifact': 'xstream',
 'old_version': '1.4.17',
 'new_version': '1.4.19',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '5',
 'breaking_tests': '5',
 'breaking_failures': '0',
 'breaking_errors': '1',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'RUNTIME_EXCEPTION',
 'main_exception': 'com.thoughtworks.xstream.security.ForbiddenClassException',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'com.thoughtworks.xstream:xstream:1.4.19',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'PROVISIONAL_BEHAVIORAL',
 'behavior_change_type': 'EXCEPTION_OR_CRASH_CHANGE',
 'behavior_description': 'XStream 1.4.19 rejects LogPanelPreferenceModel when the unchanged test '
                         'deserializes its XML with fromXML using default type permissions. PRE '
                         'accepts the same round trip.',
 'pre_log': 'logs/batch_triage/19e20b0d_pre.log',
 'breaking_log': 'logs/batch_triage/19e20b0d_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. One BREAKING error at '
          'LogPanelPreferenceModelTest.testLogPanelPreferenceModelSerialization. The stack reaches '
          'SecurityMapper.realClass and NoTypePermission. Maven and fresh Surefire totals agree. '
          'See results/case20_review.md and logs/case20_evidence/.'}


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
            raise ValueError('Case 20 differs from saved record; no changes made')
        print(f'Case 20 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case20.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case20.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 20 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
