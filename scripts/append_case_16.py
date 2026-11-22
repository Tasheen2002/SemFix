"""Save the evidence-backed Case 16 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '1750bac074c30b06ae5cdff7a25db401a4f45de2'
RECORD = {'case_id': '1750bac074c30b06ae5cdff7a25db401a4f45de2',
 'project': 'dropwizard-pac4j',
 'dependency_group': 'com.fasterxml.jackson.core',
 'dependency_artifact': 'jackson-databind',
 'old_version': '2.10.5.1',
 'new_version': '2.13.4',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '16',
 'breaking_tests': '16',
 'breaking_failures': '0',
 'breaking_errors': '16',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'JAVA_ERROR',
 'main_exception': 'java.lang.NoClassDefFoundError',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'com.fasterxml.jackson.core:jackson-databind:2.13.4',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'Jackson Databind 2.13.4 requires '
                         'com.fasterxml.jackson.core.util.JacksonFeature, but resolved '
                         'jackson-core 2.10.5 does not contain that class. All tests error during '
                         'ObjectMapper construction. This is runtime binary/linkage '
                         'incompatibility, not a behavioral contract change.',
 'pre_log': 'logs/batch_triage/1750bac0_pre.log',
 'breaking_log': 'logs/batch_triage/1750bac0_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Assessment author: CODEX_AGENT; provisional analysis awaiting human review. PRE: 16 '
          'tests, zero failures/errors/skips, Maven BUILD SUCCESS. BREAKING: 16 tests, zero '
          'failures/skips, 16 errors, Maven BUILD FAILURE. Both use Java 11.0.19 and Maven 3.9.2. '
          'Core and Annotations remain 2.10.5. Resolved Core JAR lacks JacksonFeature.class; '
          'Databind DeserializationContext bytecode references JacksonFeature in a method '
          'descriptor. The missing class is primary, confirmed by ClassNotFoundException, not a '
          'secondary Could not initialize class message. All 26 source/resource files match; only '
          'Databind version differs in POM and test classpath paths. Container exit codes are '
          'masked by tee and are not the Maven result. Evidence: results/case16_review.md, '
          'results/case16_assessment.json, logs/case16_evidence/. No semantic repair attempted.'}


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
            raise ValueError('Case 16 differs from saved record; no changes made')
        print(f'Case 16 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case16.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case16.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 16 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
