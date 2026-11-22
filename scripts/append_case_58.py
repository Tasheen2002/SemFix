"""Save the evidence-backed Case 58 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '4d4a773e3498e14932bfaf82f957c2a3f5c2cfe3'
RECORD = {'case_id': '4d4a773e3498e14932bfaf82f957c2a3f5c2cfe3',
 'project': 'dependency-track-maven-plugin',
 'dependency_group': 'com.sun.xml.bind',
 'dependency_artifact': 'jaxb-impl',
 'old_version': '2.3.3',
 'new_version': '4.0.0',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '163',
 'breaking_tests': '163',
 'breaking_failures': '3',
 'breaking_errors': '0',
 'test_effect_type': 'TEST_FAILURE',
 'test_effect_subtype': 'TEST_ASSERTION',
 'main_exception': 'java.lang.AssertionError',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'com.sun.xml.bind:jaxb-impl:4.0.0',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'JAXB implementation 4.0.0 registers a jakarta provider, incompatible '
                         'with retained javax JAXB API 2.3.1 and core 2.3.0.1. XML report creation '
                         'cannot find a compatible implementation; three integration tests fail '
                         'downstream assertions.',
 'pre_log': 'logs/batch_triage/4d4a773e_pre.log',
 'breaking_log': 'logs/batch_triage/4d4a773e_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Both original images ran 163 tests. PRE passed; '
          'BREAKING has three assertions and zero errors/skips. Fresh XML agrees with Maven. '
          'Actual JAR service descriptors and classes show loss of the javax provider. The '
          'internal ContextFactory named in the fallback ClassNotFoundException was absent from '
          'both original implementation JARs; it is not a newly removed PRE class. Root POM '
          'changes only jaxb-impl; affected classpaths also lose transitive JAXB API 2.3.3 and '
          'activation 1.2.2. No isolated substitution experiment or repair attempted. Agent '
          'assessment pending human review. The tee pipeline masks Maven failure. See '
          'results/case58_review.md and logs/case58_evidence/.'}


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
            raise ValueError('Case 58 differs from saved record; no changes made')
        print(f'Case 58 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case58.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case58.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 58 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
