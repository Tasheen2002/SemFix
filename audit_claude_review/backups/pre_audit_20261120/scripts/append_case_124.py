"""Save the evidence-backed Case 124 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = 'a9c9228182e2e46c98643332f65b0fe372f0a9e4'
RECORD = {'case_id': 'a9c9228182e2e46c98643332f65b0fe372f0a9e4',
 'project': 'camunda-platform-7-camel',
 'dependency_group': 'jakarta.xml.bind',
 'dependency_artifact': 'jakarta.xml.bind-api',
 'old_version': '2.3.2',
 'new_version': '3.0.1',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '42',
 'breaking_tests': '42',
 'breaking_failures': '0',
 'breaking_errors': '16',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'LINKAGE_ERROR',
 'main_exception': 'java.lang.IllegalStateException',
 'failure_origin': 'LIBRARY',
 'origin_library': 'jakarta.xml.bind:jakarta.xml.bind-api:3.0.1',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'JAXB API 3.0.1 supplies jakarta.xml.bind types while Camel requires '
                         'javax.xml.bind.JAXBException. The affected Spring module loses that '
                         'legacy type, causing 16 application-context setup errors.',
 'pre_log': 'logs/batch_triage/a9c92281_pre.log',
 'breaking_log': 'logs/batch_triage/a9c92281_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending independent human review; not a final semantic label. Both '
          'original Docker images were run. See results/case124_review.md and '
          'logs/case124_evidence/. No repair attempted.'}


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
            raise ValueError('Case 124 differs from saved record; no changes made')
        print(f'Case 124 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case124.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case124.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 124 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
