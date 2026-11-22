"""Save the evidence-backed Case 55 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '474422dcefb61cf1460c9f218a11b7ba693725c2'
RECORD = {'case_id': '474422dcefb61cf1460c9f218a11b7ba693725c2',
 'project': 'dropwizard-pac4j',
 'dependency_group': 'org.glassfish.jersey.core',
 'dependency_artifact': 'jersey-server',
 'old_version': '2.32',
 'new_version': '2.39',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '16',
 'breaking_tests': '16',
 'breaking_failures': '0',
 'breaking_errors': '10',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'LINKAGE_ERROR',
 'main_exception': 'java.lang.NoClassDefFoundError',
 'failure_origin': 'LIBRARY',
 'origin_library': 'org.glassfish.jersey.core:jersey-common:2.32',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'Jersey Server 2.39 startup requires DynamicFeatureConfigurator, absent '
                         'from retained Jersey Common 2.32. All ten test errors are missing-class '
                         'failures.',
 'pre_log': 'logs/batch_triage/474422dc_pre.log',
 'breaking_log': 'logs/batch_triage/474422dc_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Both images report 16 tests. BREAKING has ten '
          'NoClassDefFoundError errors. Only Server changes in the project POM; classpaths also '
          'lose transitive jersey-media-jaxb 2.32. Actual Server JAR references and Common JAR '
          'absence corroborate the missing-class diagnosis. No isolated substitution control or '
          'repair attempted. The tee pipeline masks Maven failure. See results/case55_review.md '
          'and logs/case55_evidence/.'}


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
            raise ValueError('Case 55 differs from saved record; no changes made')
        print(f'Case 55 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case55.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case55.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 55 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
