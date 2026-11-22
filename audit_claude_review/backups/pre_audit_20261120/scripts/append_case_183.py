"""Save the evidence-backed Case 183 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = 'fb40f5e5fc20ca31cf9fdadd5ace53f7de5ea093'
RECORD = {'case_id': 'fb40f5e5fc20ca31cf9fdadd5ace53f7de5ea093',
 'project': 'quarkus-micrometer-registry',
 'dependency_group': 'io.quarkiverse.googlecloudservices',
 'dependency_artifact': 'quarkus-google-cloud-common-grpc',
 'old_version': '1.4.0',
 'new_version': '2.2.0',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '19',
 'breaking_tests': '19',
 'breaking_failures': '0',
 'breaking_errors': '1',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'LINKAGE_ERROR',
 'main_exception': 'java.lang.IllegalAccessError',
 'failure_origin': 'LIBRARY',
 'origin_library': 'io.quarkiverse.googlecloudservices:quarkus-google-cloud-common-grpc:2.2.0',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'The gRPC update changes proto-google-common-protos '
                         'from 2.14.0 to 2.22.1. Its MetricDescriptor calls '
                         'LazyStringArrayList.emptyList(), which is '
                         'inaccessible in retained protobuf-java 3.14.0. '
                         'Quarkus integration test startup fails with '
                         'IllegalAccessError.',
 'pre_log': 'logs/batch_triage/fb40f5e5_pre.log',
 'breaking_log': 'logs/batch_triage/fb40f5e5_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending independent human review. Both original '
          'Docker images were run. See results/case183_review.md and '
          'logs/case183_evidence/.'}


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
            raise ValueError('Case 183 differs from saved record; no changes made')
        print(f'Case 183 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case183.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case183.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 183 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
