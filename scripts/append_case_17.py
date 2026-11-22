"""Save the evidence-backed Case 17 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '18102f7a87e7ab8308a86208d47696c060110d0c'
RECORD = {'case_id': '18102f7a87e7ab8308a86208d47696c060110d0c',
 'project': 'ORCID-Source',
 'dependency_group': 'com.fasterxml.jackson.core',
 'dependency_artifact': 'jackson-databind',
 'old_version': '2.10.0',
 'new_version': '2.12.6.1',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'FAILURE',
 'breaking_build_status': 'INTERRUPTED',
 'pre_tests': '4104',
 'breaking_tests': '222',
 'breaking_failures': '0',
 'breaking_errors': '13',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'JAVA_ERROR',
 'main_exception': 'java.lang.NoClassDefFoundError',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'com.fasterxml.jackson.core:jackson-databind:2.12.6.1',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'UNCERTAIN',
 'behavior_change_type': '',
 'behavior_description': 'Full PRE build fails a date-sensitive assertion: expected 5 current '
                         'affiliations but observed 2. BREAKING independently exhibits missing '
                         'JacksonFeature with resolved Jackson Core 2.10.1 and Databind 2.12.6.1. '
                         'Observed update failure is a non-behavioral linkage candidate, but '
                         'full-case reproduction remains inconclusive because PRE does not pass.',
 'pre_log': 'logs/batch_triage/18102f7a_pre.log',
 'breaking_log': 'logs/batch_triage/18102f7a_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Assessment author: CODEX_AGENT; not a human-reviewed label. AUTO_BASELINE_PROBLEM. PRE '
          'completed: 4104 tests, 1 assertion failure, 0 errors/skips; message-listener '
          'OrcidRecordToSolrDocumentTest.convertTest:62 fails. Source uses LocalDate.now(); three '
          'fixture affiliations ended in 2025, explaining the 2026 result by static analysis, not '
          'a time-controlled rerun. BREAKING deliberately interrupted after repeated Spring '
          'startup errors; 222 tests and 13 errors are totals of completed fresh XML reports only, '
          'not complete reactor totals. No full BREAKING Maven result claimed; container exit 143. '
          'Initial classpath comparison shows only Databind version differs; Core stays 2.10.1, '
          'Annotations 2.9.5. JAR inspection confirms missing JacksonFeature. All 4574 archived '
          'source/POM files match except root POM dependency version. See '
          'results/case17_review.md, results/case17_assessment.json, logs/case17_evidence/. '
          'Baseline resolution and human adjudication required before final classification. No '
          'repair attempted.'}


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
            raise ValueError('Case 17 differs from saved record; no changes made')
        print(f'Case 17 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case17.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case17.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 17 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
