"""Save the evidence-backed Case 64 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '52ba94ad488d562bce56eee92fb46c63fba6541b'
RECORD = {'case_id': '52ba94ad488d562bce56eee92fb46c63fba6541b',
 'project': 'github-checks-plugin',
 'dependency_group': 'org.jenkins-ci.plugins',
 'dependency_artifact': 'github-api',
 'old_version': '1.117',
 'new_version': '1.303-400.v35c2d8258028',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '49',
 'breaking_tests': '49',
 'breaking_failures': '1',
 'breaking_errors': '0',
 'test_effect_type': 'TEST_FAILURE',
 'test_effect_subtype': 'TEST_ASSERTION',
 'main_exception': 'java.lang.AssertionError',
 'failure_origin': 'LIBRARY',
 'origin_library': 'io.jenkins.plugins:okhttp-api:4.9.2-20211102',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': "ArchUnit's package scan includes the updated transitive okhttp-api JAR. "
                         'JenkinsOkHttpClient calls Jenkins.get() twice, violating the static '
                         'architecture rule.',
 'pre_log': 'logs/batch_triage/52ba94ad_pre.log',
 'breaking_log': 'logs/batch_triage/52ba94ad_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Non-behavioural static architecture policy '
          'violation. The other 48 tests pass. Actual dependency JARs and disassembly establish '
          'the added class and offending calls. The automated behavioural cue reflects the '
          'assertion, while binary linkage is absent. The tee pipeline masks Maven failure. See '
          'results/case64_review.md and logs/case64_evidence/.'}


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
            raise ValueError('Case 64 differs from saved record; no changes made')
        print(f'Case 64 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case64.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case64.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 64 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
