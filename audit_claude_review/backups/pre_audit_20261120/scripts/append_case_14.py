from pathlib import Path
import csv

CASE_ID = '12e237710199fafa086fd2299edefd5f8f05a63c'
RECORD = {'case_id': '12e237710199fafa086fd2299edefd5f8f05a63c',
 'project': 'geostore',
 'dependency_group': 'com.h2database',
 'dependency_artifact': 'h2',
 'old_version': '1.3.175',
 'new_version': '2.0.206',
 'bump_category': 'TEST_FAILURE',
 'pre_build_status': 'SUCCESS',
 'breaking_build_status': 'FAILURE',
 'pre_tests': '32',
 'breaking_tests': '32',
 'breaking_failures': '0',
 'breaking_errors': '22',
 'test_effect_type': 'TEST_ERROR',
 'test_effect_subtype': 'RUNTIME_EXCEPTION',
 'main_exception': 'org.h2.jdbc.JdbcSQLSyntaxErrorException',
 'failure_origin': 'UPDATED_LIBRARY',
 'origin_library': 'com.h2database:h2:2.0.206',
 'binary_linkage_incompatibility': 'NO',
 'behavioral_status': 'PROVISIONAL_BEHAVIORAL',
 'behavior_change_type': 'OTHER_BEHAVIORAL_CHANGE',
 'behavior_description': 'H2 2.0.206 rejects Hibernate-generated VARCHAR(10000000), which H2 1.3.175 '
                         'accepted. The table creation fails and dependent tests report missing table '
                         'errors.',
 'pre_log': 'logs/batch_triage/12e23771_pre.log',
 'breaking_log': 'logs/batch_triage/12e23771_breaking.log',
 'review_status': 'PENDING_SECOND_REVIEW',
 'reviewer_1_label': 'PROVISIONAL_BEHAVIORAL',
 'reviewer_2_label': '',
 'final_label': '',
 'notes': 'Verified repair in BUMP environment: replace length = 10000000 with columnDefinition = CLOB in '
          'StoredData.java. Updated H2 retained. Relevant tests: 32 passed, 0 failures, 0 errors. Maven '
          'BUILD SUCCESS. Evidence: logs/case14_clob_fixed.log. Separate module: 32 skipped tests. Final '
          'semantic classification requires independent review; cross-database compatibility not verified.'}

def main():
    path = Path(__file__).resolve().parents[1] / 'results' / 'behavioral_classification.csv'
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    if not fields or set(fields) != set(RECORD):
        raise ValueError('CSV schema differs from saved Case 14 record')
    existing = [row for row in rows if row.get('case_id') == CASE_ID]
    if len(existing) > 1:
        raise ValueError('Duplicate Case 14 records')
    if existing:
        if existing[0] == RECORD:
            print('Case 14 already recorded; no changes made. Total:', len(rows))
            return
        raise ValueError('Case 14 record differs; no changes made')
    with path.open('a', encoding='utf-8', newline='') as stream:
        csv.DictWriter(stream, fieldnames=fields).writerow(RECORD)
    print('Case 14 appended. Total:', len(rows)+1)

if __name__ == '__main__':
    main()
