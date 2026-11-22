"""Save the evidence-backed Case 35 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '30149ce4bdde6418aad7f02c35bd9dc8101b58ac'
RECORD = {'case_id': '30149ce4bdde6418aad7f02c35bd9dc8101b58ac',
 'project': 'pay-cardid',
 'dependency_group': 'org.dhatim',
 'dependency_artifact': 'dropwizard-sentry',
 'old_version': '2.0.22',
 'new_version': '2.0.28-3',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '44',
 'breaking_tests': '34',
 'breaking_failures': '0',
 'breaking_errors': '1',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'RUNTIME_EXCEPTION',
 'main_exception': 'io.dropwizard.configuration.ConfigurationParsingException',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'org.dhatim:dropwizard-sentry:2.0.28-3',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'PROVISIONAL_BEHAVIORAL',
 'behavior_change_type': 'EXCEPTION_OR_CRASH_CHANGE',
 'behavior_description': 'Dropwizard Sentry 2.0.28-3 rejects the existing stacktraceAppPackages '
                         'YAML property as unrecognized. The changed configuration contract '
                         'prevents integration test startup.',
 'pre_log': 'logs/batch_triage/30149ce4_pre.log',
 'breaking_log': 'logs/batch_triage/30149ce4_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Disassembly of both resolved appender classes '
          'verifies the configuration property change. Maven and fresh Surefire totals agree. The '
          "tee pipeline masks Maven's failing exit code. See results/case35_review.md and "
          'logs/case35_evidence/.'}


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
            raise ValueError('Case 35 differs from saved record; no changes made')
        print(f'Case 35 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case35.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case35.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 35 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
