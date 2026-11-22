"""Save the evidence-backed Case 57 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '4c7b193ce573e31766da82268ffc9ba51412faa6'
RECORD = {'case_id': '4c7b193ce573e31766da82268ffc9ba51412faa6',
 'project': 'fscrawler',
 'dependency_group': 'org.apache.poi',
 'dependency_artifact': 'poi-ooxml',
 'old_version': '4.1.2',
 'new_version': '5.2.1',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '88',
 'breaking_tests': '82',
 'breaking_failures': '2',
 'breaking_errors': '0',
 'test_effect_type': 'TEST_FAILURE',
 'test_effect_subtype': 'TEST_ASSERTION',
 'main_exception': 'java.lang.AssertionError',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'org.apache.poi:poi-ooxml:5.2.1',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'POI OOXML 5.2.1 declares POIXMLTextExtractor as an interface extending '
                         'POITextExtractor, but retained POI 4.1.2 provides POITextExtractor as an '
                         'abstract class. Extraction fails and two DOCX tests receive null text.',
 'pre_log': 'logs/batch_triage/4c7b193c_pre.log',
 'breaking_log': 'logs/batch_triage/4c7b193c_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending independent human review. PRE reports 88 tests including three '
          'ignored; BREAKING reports 82 including one ignored and two assertions, then skips '
          'downstream modules. Randomized-runner summaries supply counts; no Surefire XML exists. '
          'Failed-run events, mixed POI versions and actual JAR type declarations corroborate '
          'binary incompatibility. Additional protected-DOCX missing-class log is not a third '
          'failure. No repair attempted. The tee pipeline masks Maven failure. See '
          'results/case57_review.md and logs/case57_evidence/.'}


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
            raise ValueError('Case 57 differs from saved record; no changes made')
        print(f'Case 57 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case57.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case57.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 57 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
