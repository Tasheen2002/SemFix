"""Save the evidence-backed Case 53 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '46698497759b188a97830330dfebaf718beb5573'
RECORD = {'case_id': '46698497759b188a97830330dfebaf718beb5573',
 'project': 'plexus-archiver',
 'dependency_group': 'org.codehaus.plexus',
 'dependency_artifact': 'plexus-io',
 'old_version': '3.2.0',
 'new_version': '3.3.0',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '177',
 'breaking_tests': '177',
 'breaking_failures': '0',
 'breaking_errors': '22',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'RUNTIME_EXCEPTION',
 'main_exception': 'org.codehaus.plexus.archiver.ArchiverException',
 'failure_origin': 'CLIENT',
 'origin_library': 'org.codehaus.plexus:plexus-io:3.3.0',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'PROVISIONAL_BEHAVIORAL',
 'behavior_change_type': 'OTHER_BEHAVIORAL_CHANGE',
 'behavior_description': 'Plexus IO 3.3.0 reports directory symlinks as non-directories using '
                         'NOFOLLOW_LINKS FileAttributes, whereas 3.2.0 follows the link. The '
                         'unchanged archiver rejects these resources with Not a directory.',
 'pre_log': 'logs/batch_triage/46698497_pre.log',
 'breaking_log': 'logs/batch_triage/46698497_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. 177 reported tests in both images; PRE zero '
          'errors, BREAKING 22 ArchiverException errors; two skips in each. Source/POM and '
          'classpath differ only in Plexus IO. A same-environment standalone probe confirms '
          'resource.isDirectory true to false for the same kind of directory symlink. No repair '
          'attempted. The tee pipeline masks Maven failure. See results/case53_review.md and '
          'logs/case53_evidence/.'}


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
            raise ValueError('Case 53 differs from saved record; no changes made')
        print(f'Case 53 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case53.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case53.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 53 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
