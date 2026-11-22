"""Save the evidence-backed Case 79 assessment without claiming human review."""

import csv
import io
import os
import shutil
from datetime import datetime
from pathlib import Path

CASE_ID = '65b5a75419981118d5a65e295abfd2069dfce0b0'
RECORD = {'case_id': '65b5a75419981118d5a65e295abfd2069dfce0b0',
 'project': 'fscrawler',
 'dependency_group': 'org.apache.poi',
 'dependency_artifact': 'poi',
 'old_version': '4.1.2',
 'new_version': '5.2.2',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '89',
 'breaking_tests': '83',
 'breaking_failures': '4',
 'breaking_errors': '0',
 'test_effect_type': 'TEST_FAILURE',
 'test_effect_subtype': 'TEST_ASSERTION',
 'main_exception': 'java.lang.AssertionError',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'org.apache.poi:poi:5.2.2',
 'binary_linkage_incompatibility': 'YES',
 'behavioral_status': 'NON_BEHAVIORAL',
 'behavior_change_type': '',
 'behavior_description': 'POI 5.2.2 changes POITextExtractor from a class to an interface and '
                         'WORKBOOK_DIR_ENTRY_NAMES from a String array to a List. Legacy OOXML and '
                         'Tika binaries reference the earlier types, causing extraction failures '
                         'and four downstream assertions.',
 'pre_log': 'logs/batch_triage/65b5a754_pre.log',
 'breaking_log': 'logs/batch_triage/65b5a754_breaking.log',
 'review_status': 'PENDING_HUMAN_REVIEW',
 'reviewer_1_label': '',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Agent assessment pending human review. Randomized JUnit module summaries give 89 PRE '
          'and 83 BREAKING tests including three and one ignored respectively. Four failed-run '
          'event files and actual JAR disassembly establish the two binary mismatches. The tee '
          'pipeline masks Maven failure. See results/case79_review.md and logs/case79_evidence/.'}


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
            raise ValueError('Case 79 differs from saved record; no changes made')
        print(f'Case 79 already recorded; no changes made. Total: {len(rows)}')
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
    backup = backup_dir / (path.name + '.before_case79.' +
                          datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.case79.tmp')
    with temporary.open('xb') as stream:
        stream.write(updated)
    if path.read_bytes() != original:
        temporary.unlink()
        raise RuntimeError('Classification changed concurrently; original retained')
    os.replace(temporary, path)
    print(f'Case 79 appended. Total: {len(rows) + 1}. Backup: {backup}')


if __name__ == '__main__':
    main()
