"""Validate original-image evidence, curated records and preservation for Cases 101-105."""
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKUP = ROOT / 'results/backups/before_cases101_105_20261110_124753_157351'
EXPECTED = {
    101: ((132, 0, 0, 3), (132, 0, 20, 2), 'NON_BEHAVIORAL', 'YES'),
    102: ((210, 0, 0, 3), (210, 7, 0, 3), 'NON_BEHAVIORAL', 'YES'),
    103: ((95, 0, 0, 3), (89, 4, 0, 1), 'NON_BEHAVIORAL', 'YES'),
    104: ((5, 0, 0, 0), (5, 0, 1, 0), 'NON_BEHAVIORAL', 'YES'),
    105: ((309, 0, 0, 0), (309, 6, 4, 0), 'NON_BEHAVIORAL', 'YES'),
}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def read_rows(path):
    return list(csv.DictReader(io.StringIO(path.read_text(encoding='utf-8-sig'), newline='')))

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

def main():
    require(set(EXPECTED) == set(range(101, 106)), 'Expected evidence for Case 105 is not finalized')
    path = ROOT / 'results/behavioral_classification.csv'
    original = path.read_bytes()
    clean = (BACKUP / 'behavioral_classification.cleaned.csv').read_bytes()
    damaged = (BACKUP / 'behavioral_classification.csv').read_bytes()
    repairs = [damaged.replace(pattern, b'jakarta.xml.bind-api', 1) for pattern in (b'jakarta.xml.\r\nbind-api', b'jakarta.xml.\nbind-api') if damaged.count(pattern) == 1]
    require(clean in repairs, 'Initial CSV repair differs from the documented single newline fix')
    require(original.startswith(clean), 'Cleaned original 100 records were changed')
    rows = read_rows(path)
    candidates = read_rows(ROOT / 'results/test_failure_candidates.csv')
    require(len(rows) == 105, 'Expected exactly 105 case records')
    require(len({r['case_id'] for r in rows}) == 105, 'Missing or duplicate case IDs')
    require(all(None not in r and all(v is not None for v in r.values()) for r in rows), 'Malformed CSV rows')
    require([r['case_id'] for r in rows] == [r['case_id'] for r in candidates[:105]], 'Cases differ from candidate order')
    for n in (42, 100):
        require(runpy.run_path(str(ROOT / f'scripts/append_case_{n}.py'))['RECORD'] == rows[n-1], f'Case {n} differs from saved record')
    for relative, backup in (('results/verified_repairs.jsonl', 'verified_repairs.jsonl'), ('repairs/case14_h2_clob.patch', 'case14_h2_clob.patch')):
        require((ROOT / relative).read_bytes() == (BACKUP / backup).read_bytes(), f'Preserved repair changed: {relative}')
    require(len((ROOT / 'results/verified_repairs.jsonl').read_text().splitlines()) == 1, 'Unexpected verified repair count')
    triage = read_rows(ROOT / 'results/batch_triage_results.csv')
    previous = read_rows(BACKUP / 'batch_triage_results.csv')
    require(all(r in triage for r in previous), 'Previous automated triage records changed')
    require(len(triage) == len(previous) + 5, 'Unexpected new automated triage count')
    checked = {}
    for n, expected in EXPECTED.items():
        row = rows[n-1]
        candidate = candidates[n-1]
        require(row['behavioral_status'] == expected[2] and row['binary_linkage_incompatibility'] == expected[3], f'Case {n} assessment differs')
        require(row['review_status'] == 'PENDING_HUMAN_REVIEW', 'Unexpected human-review status')
        require(all(row[k] == '' for k in ('reviewer_1_label', 'reviewer_2_label', 'final_label')), 'Human labels were populated')
        for key in ('project', 'dependency_group', 'dependency_artifact', 'new_version'):
            require(row[key] == candidate[key], f'Case {n} identity differs: {key}')
        require(row['old_version'] == candidate['previous_version'], 'Old version differs')
        require(runpy.run_path(str(ROOT / f'scripts/append_case_{n}.py'))['RECORD'] == row, 'Append script differs from CSV')
        require(len([r for r in triage if r['case_id'] == row['case_id']]) == 1, 'Missing/duplicate automated record')
        base = ROOT / f'logs/case{n}_evidence'
        manifest = read_json(base / 'sha256_manifest.json')
        required = {p.relative_to(ROOT).as_posix() for p in base.rglob('*') if p.is_file() and p.name != 'sha256_manifest.json'}
        required.update((f'scripts/append_case_{n}.py', f'results/case{n}_review.md', row['pre_log'], row['breaking_log']))
        require(required <= manifest.keys(), 'Evidence manifest incomplete')
        for name, digest in manifest.items():
            with (ROOT / name).open('rb') as stream:
                require(hashlib.file_digest(stream, 'sha256').hexdigest() == digest, f'Hash differs: {name}')
        summaries = []
        for index, phase in enumerate(('pre', 'breaking')):
            summary = read_json(base / phase / 'archive_summary.json')
            summaries.append(summary)
            require(summary['case_id'] == row['case_id'] and summary['phase'] == phase, 'Archive identity differs')
            require(summary['container_state']['Status'] == 'exited' and not summary['container_state']['OOMKilled'], 'Original container did not finish normally')
            require(summary['image_id'].startswith('sha256:') and summary['image_digests'], 'Image provenance missing')
            log = (ROOT / row[f'{phase}_log']).read_text(encoding='utf-8', errors='replace')
            outcome = 'SUCCESS' if phase == 'pre' else 'FAILURE'
            require(re.findall(r'BUILD (SUCCESS|FAILURE)', log) == [outcome], f'Case {n} {phase} Maven result differs')
            if n == 103:
                require(summary['report_count'] == 0, 'Unexpected Surefire reports in randomized case')
                runner = read_json(base / phase / 'randomized_summary.json')
                counts = runner['aggregate_counts']
                counts = tuple(counts[k] for k in ('tests', 'failures', 'errors', 'ignored'))
                require(len(runner['retained_runner_files']) == (0 if phase == 'pre' else 4), 'Runner evidence differs')
                module_summaries = re.findall(r'^\[INFO\] Tests summary: (\d+) suites?, (\d+) tests?([^\r\n]*)', log, re.M)
                require(sum(int(v[1]) for v in module_summaries) == counts[0], 'Runner log counts differ')
            else:
                aggregate = summary['aggregate_counts']
                if n == 105:
                    reconciled = read_json(base / phase / 'reconciled_counts.json')
                    require(reconciled['raw_xml_counts'] == aggregate and reconciled['duplicate_test_identities_and_statuses_verified'], 'TestNG reconciliation differs')
                    aggregate = reconciled['aggregate_counts']
                    require(set(reconciled['excluded_reports']) == {r['path'] for r in summary['reports'] if '/surefire-reports/junitreports/' in r['path']}, 'Unexpected TestNG exclusions')
                counts = tuple(aggregate[k] for k in ('tests', 'failures', 'errors', 'skipped'))
                matches = re.findall(r'^(?:\[[A-Z]+\] )?Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)[ \t]*$', log, re.M)
                log_counts = tuple(map(sum, zip(*(map(int, v) for v in matches)))) if matches else (0, 0, 0, 0)
                require(log_counts == counts, f'Case {n} Maven/XML counts differ: {log_counts} vs {counts}')
            require(counts == expected[index], f'Case {n} {phase} expected counts differ: {counts}')
        before, after = [s['source_and_pom_sha256'] for s in summaries]
        expected_changes = [] if n == 105 else ['pom.xml']
        require(before.keys() == after.keys() and [p for p in before if before[p] != after[p]] == expected_changes, 'Unexpected archived source/POM changes')
        poms = [read_json(base / phase / 'all_poms_sha256.json') for phase in ('pre', 'breaking')]
        changed_pom = 'spring/junit4-spring-boot-test/pom.xml' if n == 105 else 'pom.xml'
        require(poms[0].keys() == poms[1].keys() and [p for p in poms[0] if poms[0][p] != poms[1][p]] == [changed_pom], 'Unexpected all-depth POM changes')
        comparison = read_json(base / 'all_poms_comparison.json')
        require(comparison['changed_poms'] == [changed_pom], 'POM comparison differs')
        require('-            <version>' + row['old_version'] + '</version>' in comparison['diffs'][changed_pom] or '-                <version>' + row['old_version'] + '</version>' in comparison['diffs'][changed_pom], 'Old POM version differs')
        require('+            <version>' + row['new_version'] + '</version>' in comparison['diffs'][changed_pom] or '+                <version>' + row['new_version'] + '</version>' in comparison['diffs'][changed_pom], 'New POM version differs')
        jars = read_json(base / 'resolved_jar_inspection.json')
        if n == 101:
            api = [r for r in jars if '/jakarta.xml.bind-api/' in r['resolved_path']]
            require(len(api) == 2 and [r['classes']['javax/xml/bind/JAXBException.class'] for r in api] == [True, False], 'JAXB missing-type evidence differs')
        elif n == 102:
            impl = [r for r in jars if '/jaxb-impl/' in r['resolved_path']]
            require(len(impl) == 2, 'Implementation evidence incomplete')
            require('META-INF/services/javax.xml.bind.JAXBContextFactory' in impl[0]['services'] and 'META-INF/services/jakarta.xml.bind.JAXBContextFactory' in impl[1]['services'], 'JAXB provider evidence differs')
            require(all(not r['classes']['com/sun/xml/internal/bind/v2/ContextFactory.class'] for r in impl), 'Fallback lookup explanation differs')
        elif n == 103:
            old = (base / 'pre_poi-4.1.2_POITextExtractor_javap.txt').read_text()
            new = (base / 'breaking_poi-5.2.0_POITextExtractor_javap.txt').read_text()
            require('public abstract class org.apache.poi.extractor.POITextExtractor' in old and 'public interface org.apache.poi.extractor.POITextExtractor' in new, 'POI class/interface evidence differs')
            require('WORKBOOK_DIR_ENTRY_NAMES:[Ljava/lang/String;' in (base / 'breaking_tika-parser-microsoft-module-2.2.1_POIFSContainerDetector_javap.txt').read_text(), 'Tika field reference differs')
        elif n == 104:
            parent = (base / 'breaking_dss-pades-5.9_AbstractPDFSignatureService_javap.txt').read_text()
            updated = (base / 'breaking_dss-pades-pdfbox-5.10.2_PdfBoxSignatureService_javap.txt').read_text()
            require('checkDocumentPermissions(eu.europa.esig.dss.model.DSSDocument, java.lang.String)' in parent and 'checkDocumentPermissions:(Leu/europa/esig/dss/pdf/PdfDocumentReader;)V' in updated, 'DSS method descriptor evidence differs')
        elif n == 105:
            require(not any(r['contains_LoggerContextShutdownAware'] for r in jars), 'Missing Log4j type unexpectedly present')
            updated = [r for r in jars if '/log4j-core/2.16.0/' in r['resolved_path']]
            require(len(updated) == 1 and 'org/apache/logging/log4j/core/selector/ClassLoaderContextSelector.class' in updated[0]['classes_referencing_type'], 'Log4j type reference evidence differs')
            require('org.apache.logging.log4j.spi.LoggerContextShutdownAware' in (base / 'breaking_ClassLoaderContextSelector_javap.txt').read_text(), 'Log4j interface declaration differs')
        require([int(row[k]) for k in ('pre_tests', 'breaking_tests', 'breaking_failures', 'breaking_errors')] == [expected[0][0], *expected[1][:3]], 'CSV counts differ')
        result = subprocess.run([sys.executable, str(ROOT / f'scripts/append_case_{n}.py')], cwd=ROOT, capture_output=True, text=True)
        require(result.returncode == 0, result.stderr)
        require(path.read_bytes() == original, 'Idempotency check changed CSV')
        checked[str(n)] = {'assessment': expected[2], 'pre_counts': expected[0], 'breaking_counts': expected[1], 'original_images_run': 2, 'manifest_files_checked': len(manifest), 'append_idempotent': True}
    output = {'passed': True, 'classification_records': 105, 'counts_through_105': dict(Counter(r['behavioral_status'] for r in rows)), 'original_100_records_preserved_after_documented_case42_newline_repair': True, 'verified_repairs_and_case14_patch_byte_preserved': True, 'human_review_pending_for_new_cases': True, 'automated_triage_kept_separate': True, 'cases': checked}
    (ROOT / 'results/cases101_105_completion_check.json').write_text(json.dumps(output, indent=2), encoding='utf-8')
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
