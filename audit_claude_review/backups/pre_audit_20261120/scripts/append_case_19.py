"""Save the evidence-backed Case 19 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '19249139eb66616953c389242c22edde60c4ac2f'
RECORD = {'case_id': '19249139eb66616953c389242c22edde60c4ac2f',
 'project': 'pgpverify-maven-plugin',
 'dependency_group': 'org.junit.jupiter',
 'dependency_artifact': 'junit-jupiter-params',
 'old_version': '5.9.3',
 'new_version': '5.10.0',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '300',
 'breaking_tests': '161',
 'breaking_failures': '0',
 'breaking_errors': '15',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'JAVA_ERROR',
 'main_exception': 'java.lang.NoSuchMethodError',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'org.junit.jupiter:junit-jupiter-params:5.10.0',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'JUnit Params 5.10.0 calls ClassLoaderUtils.getClassLoader(Class) during '
                         'argument-source resolution. Resolved JUnit Platform Commons 1.9.3 lacks '
                         'that method, causing NoSuchMethodError across 15 test reports.',
 'pre_log': 'logs/batch_triage/19249139_pre.log',
 'breaking_log': 'logs/batch_triage/19249139_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. AUTO_NON_BEHAVIORAL_CANDIDATE. PRE 300 tests '
          'with no failures, errors, or skips. BREAKING 161 reported tests with 15 linkage errors '
          'across nine classes and no assertion failures or skips. Maven summaries match fresh '
          'Surefire reports. Both images pipe Maven through tee and exited zero. The only archived '
          'source/POM content difference is the Params version. All affected classpath path '
          'comparisons and javap on the resolved JARs confirm the missing method. See '
          'results/case19_review.md and logs/case19_evidence/.'}


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
            raise ValueError('Case 19 differs from saved record; no changes made')
        print(f'Case 19 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case19.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case19.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 19 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
