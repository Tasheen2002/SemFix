"""Save the evidence-backed Case 28 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '22eec990412b563439a1dfae84134b43d85d9815'
RECORD = {'case_id': '22eec990412b563439a1dfae84134b43d85d9815',
 'project': 'pay-cardid',
 'dependency_group': 'org.dhatim',
 'dependency_artifact': 'dropwizard-sentry',
 'old_version': '2.0.22',
 'new_version': '2.0.28-8',
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
 'origin_library': 'org.dhatim:dropwizard-sentry:2.0.28-8',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'PROVISIONAL_BEHAVIORAL',
 'behavior_change_type': 'EXCEPTION_OR_CRASH_CHANGE',
 'behavior_description': 'The updated SentryAppenderFactory no longer accepts the '
                         'stacktraceAppPackages YAML property. The unchanged configuration is '
                         'rejected as an unrecognized field and the integration test fails during '
                         'Dropwizard setup.',
 'pre_log': 'logs/batch_triage/22eec990_pre.log',
 'breaking_log': 'logs/batch_triage/22eec990_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Disassembly of both resolved appender classes '
          'verifies the property change. Maven and fresh Surefire totals agree. The tee pipeline '
          "masks Maven's failing exit code. See results/case28_review.md and "
          'logs/case28_evidence/.'}


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
            raise ValueError('Case 28 differs from saved record; no changes made')
        print(f'Case 28 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case28.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case28.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 28 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
