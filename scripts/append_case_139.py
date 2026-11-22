"""Save the evidence-backed Case 139 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = 'bbd396d040324e103e29fcfe0b51389bfade4d93'
RECORD = {'case_id': 'bbd396d040324e103e29fcfe0b51389bfade4d93',
 'project': 'wsdoc',
 'dependency_group': 'org.yaml',
 'dependency_artifact': 'snakeyaml',
 'old_version': '1.13',
 'new_version': '1.31',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '59',
 'breaking_tests': '59',
 'breaking_failures': '20',
 'breaking_errors': '0',
 'test_effect_type': 'TEST_FAILURE',
 'test_effect_subtype': 'LINKAGE_ERROR',
 'main_exception': 'java.lang.NoSuchMethodError',
 'failure_origin': 'LIBRARY',
 'origin_library': 'org.yaml:snakeyaml:1.31',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'Retained RAML Parser calls SequenceNode.getFlowStyle() with a Boolean '
                         'return descriptor. SnakeYAML 1.31 returns DumperOptions.FlowStyle '
                         'instead, so the JVM cannot resolve the old call.',
 'pre_log': 'logs/batch_triage/bbd396d0_pre.log',
 'breaking_log': 'logs/batch_triage/bbd396d0_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending independent human review; not a final semantic label. Both '
          'original Docker images were run. See results/case139_review.md and '
          'logs/case139_evidence/. No repair attempted.'}


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
            raise ValueError('Case 139 differs from saved record; no changes made')
        print(f'Case 139 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case139.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case139.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 139 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
