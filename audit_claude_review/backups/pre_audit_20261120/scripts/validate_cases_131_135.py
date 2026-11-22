"""Validate Cases 131-135 without changing earlier records or evidence."""
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
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BACKUP = ROOT / 'results/backups/before_cases131_135'
EXPECTED = {131: ((95, 0, 0, 3), (89, 3, 0, 1), 'NON_BEHAVIORAL', 'YES'),
 132: ((291, 0, 0, 13), (94, 0, 3, 10), 'PROVISIONAL_BEHAVIORAL', 'NO'),
 133: ((180, 0, 0, 9), (134, 0, 131, 1), 'NON_BEHAVIORAL', 'YES'),
 134: ((38, 0, 0, 0), (38, 0, 12, 0), 'PROVISIONAL_BEHAVIORAL', 'NO'),
 135: ((32, 0, 0, 0), (18, 1, 5, 0), 'NON_BEHAVIORAL', 'YES')}
POM_PATHS = {135: 'core/pom.xml'}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def read_rows(path):
    return list(csv.DictReader(io.StringIO(path.read_text(encoding='utf-8-sig'), newline='')))

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def main():
    require(set(EXPECTED) == set(range(131, 136)), 'Expected data must cover the entire batch')
    path = ROOT / 'results/behavioral_classification.csv'
    original = path.read_bytes()
    require(original.startswith((BACKUP / 'behavioral_classification.csv').read_bytes()), 'Original 130 records changed')
    rows = read_rows(path)
    candidates = read_rows(ROOT / 'results/test_failure_candidates.csv')
    require(len(rows) == 135 and len({r['case_id'] for r in rows}) == 135, 'Missing/duplicate case records')
    require(all(None not in r and all(v is not None for v in r.values()) for r in rows), 'Malformed CSV rows')
    require([r['case_id'] for r in rows] == [r['case_id'] for r in candidates[:135]], 'Candidate order differs')
    for relative, backup in [('results/verified_repairs.jsonl', 'verified_repairs.jsonl'), ('repairs/case14_h2_clob.patch', 'case14_h2_clob.patch')]:
        require((ROOT / relative).read_bytes() == (BACKUP / backup).read_bytes(), 'Existing repair evidence changed')
    require(len((ROOT / 'results/verified_repairs.jsonl').read_text().splitlines()) == 1, 'Unexpected verified repair count')
    triage = read_rows(ROOT / 'results/batch_triage_results.csv')
    previous = read_rows(BACKUP / 'batch_triage_results.csv')
    require(all(r in triage for r in previous) and len(triage) == len(previous) + 5, 'Previous/new automated triage records differ')
    checked = {}
    for n, expected in EXPECTED.items():
        row, candidate = rows[n-1], candidates[n-1]
        require(row['behavioral_status'] == expected[2] and row['binary_linkage_incompatibility'] == expected[3], f'Case {n} assessment differs')
        require(row['review_status'] == 'PENDING_HUMAN_REVIEW' and all(row[k] == '' for k in ('reviewer_1_label', 'reviewer_2_label', 'final_label')), 'Independent review incorrectly claimed')
        for key in ('case_id', 'project', 'dependency_group', 'dependency_artifact', 'new_version'):
            require(row[key] == candidate[key], f'Case {n} candidate identity differs')
        require(row['old_version'] == candidate['previous_version'], 'Previous version differs')
        require(runpy.run_path(str(ROOT / f'scripts/append_case_{n}.py'))['RECORD'] == row, 'Append record differs from CSV')
        require(len([r for r in triage if r['case_id'] == row['case_id']]) == 1, 'Missing/duplicate automated record')
        base = ROOT / f'logs/case{n}_evidence'
        manifest = read_json(base / 'sha256_manifest.json')
        required = {p.relative_to(ROOT).as_posix() for p in base.rglob('*') if p.is_file() and p.name != 'sha256_manifest.json'}
        required.update([f'scripts/append_case_{n}.py', f'results/case{n}_review.md', row['pre_log'], row['breaking_log']])
        require(required <= manifest.keys(), 'Incomplete evidence manifest')
        for name, sha256 in manifest.items():
            require(digest(ROOT / name) == sha256, 'Evidence hash changed: ' + name)
        snapshots = []
        for index, phase in enumerate(('pre', 'breaking')):
            summary = read_json(base / phase / 'archive_summary.json')
            snapshots.append(summary)
            require(summary['case_id'] == row['case_id'] and summary['phase'] == phase, 'Archive identity differs')
            require(summary['container_state']['Status'] == 'exited' and not summary['container_state']['OOMKilled'], 'Original container unfinished or OOM killed')
            require(summary['image_id'].startswith('sha256:') and summary['image_digests'], 'Missing image identity')
            expected_reports = {r['path'] for r in summary['reports']}
            require(len(expected_reports) == summary['report_count'], 'Duplicate report paths')
            archived_counts = dict.fromkeys(('tests', 'failures', 'errors', 'skipped'), 0)
            found = set()
            with tarfile.open(base / phase / 'artifacts.tar') as archive:
                for member in archive:
                    if member.name not in expected_reports:
                        continue
                    xml = ET.fromstring(archive.extractfile(member).read())
                    found.add(member.name)
                    for key in archived_counts:
                        archived_counts[key] += int(xml.get(key, '0'))
            require(found == expected_reports and archived_counts == summary['aggregate_counts'], 'Archived XML and metadata counts/path names differ')
            require(all(r['module'] in summary['cleaned_modules'] for r in summary['reports']), 'Stale module report included')
            log = (ROOT / row[phase + '_log']).read_text(encoding='utf-8', errors='replace')
            require(re.findall(r'BUILD (SUCCESS|FAILURE)', log) == [('SUCCESS' if phase == 'pre' else 'FAILURE')], 'Original Maven outcome differs')
            if n == 131:
                runner = read_json(base / phase / 'randomized_summary.json')
                counts = tuple(runner['aggregate_counts'][key] for key in ('tests', 'failures', 'errors', 'ignored'))
                module_summaries = re.findall(r'^\[INFO\] Tests summary: (\d+) suites?, (\d+) tests?([^\r\n]*)', log, re.M)
                totals = (sum(int(m[1]) for m in module_summaries), *[
                    sum(sum(map(int, re.findall(r'(\d+) ' + term, m[2]))) for m in module_summaries)
                    for term in ('failure', 'error', 'ignored')])
                require(totals == counts and summary['report_count'] == 0, 'Randomized-runner totals differ')
            else:
                counts = tuple(summary['aggregate_counts'][k] for k in ('tests', 'failures', 'errors', 'skipped'))
                summaries = re.findall(r'^(?:\[[A-Z]+\] )?Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)[ \t]*$', log, re.M)
                calculated = tuple(map(sum, zip(*(map(int, s) for s in summaries)))) if summaries else (0, 0, 0, 0)
                require(calculated == counts, f'Case {n} Maven/XML counts differ')
            require(counts == expected[index], f'Case {n} {phase} expected counts differ')
            inspection = read_json(base / phase / 'jar_inspection.json')
            require(inspection['case_id'] == row['case_id'] and inspection['phase'] == phase, 'JAR inspection identity differs')
            for jar in inspection['artifacts']:
                require(digest(base / phase / 'jars' / Path(jar['resolved_path']).name) == jar['sha256'], 'JAR content differs from inspection')
        before, after = [s['source_and_pom_sha256'] for s in snapshots]
        pom = POM_PATHS.get(n, 'pom.xml')
        require(before.keys() == after.keys() and [p for p in before if before[p] != after[p]] == [pom], 'Unexpected archived source/POM changes')
        poms = [read_json(base / phase / 'all_poms_sha256.json') for phase in ('pre', 'breaking')]
        require(poms[0].keys() == poms[1].keys() and [p for p in poms[0] if poms[0][p] != poms[1][p]] == [pom], 'Unexpected all-depth POM changes')
        comparison = read_json(base / 'all_poms_comparison.json')
        require(comparison['changed_poms'] == [pom], 'POM comparison differs')
        changes = [line for line in comparison['diffs'][pom].splitlines() if line.startswith(('-', '+')) and not line.startswith(('---', '+++'))]
        require(len(changes) == 2 and re.fullmatch(r'-\s*<version>' + re.escape(row['old_version']) + r'</version>', changes[0]) and re.fullmatch(r'\+\s*<version>' + re.escape(row['new_version']) + r'</version>', changes[1]), 'POM diff contains changes beyond the candidate version')
        require([int(row[k]) for k in ('pre_tests', 'breaking_tests', 'breaking_failures', 'breaking_errors')] == [expected[0][0], *expected[1][:3]], 'CSV test counts differ')
        if n == 131:
            breaking = base / 'breaking'
            require('public interface org.apache.poi.extractor.POITextExtractor' in (breaking / 'poi-5.0.0_POITextExtractor_javap.txt').read_text(), 'Expected POI interface missing')
            require('extends org.apache.poi.extractor.POITextExtractor' in (breaking / 'poi-ooxml-4.1.2_POIXMLTextExtractor_javap.txt').read_text(), 'Expected OOXML superclass missing')
            signature = 'getByteArray(byte[], int, int, int)'
            require(signature in (base / 'pre/poi-4.1.2_LittleEndian_javap.txt').read_text(), 'Baseline overload missing')
            require(signature not in (breaking / 'poi-5.0.0_LittleEndian_javap.txt').read_text(), 'Updated overload unexpectedly present')
            require('LittleEndian.getByteArray:([BIII)[B' in (breaking / 'poi-scratchpad-4.1.2_org.apache.poi.hwpf.model.ComplexFileTable_javap.txt').read_text(), 'Retained Scratchpad call missing')
        if n in (132, 134):
            probe = read_json(base / 'logger_probe_results.json')
            require(digest(base / 'logger_probe_classes/LoggerSelectionProbe.class') == probe['class_sha256'], 'Logger probe bytecode differs')
            require([r['image_id'] for r in probe['runs']] == [s['image_id'] for s in snapshots], 'Logger probe used different images')
            require([r['exit_code'] for r in probe['runs']] == [0, 0], 'Compatible logger API did not execute in both images')
            baseline_logger = 'logger=ch.qos.logback.classic.Logger' if n == 132 else 'logger=com.sun.proxy.$Proxy'
            require(baseline_logger in probe['runs'][0]['stdout'] and 'logger=org.slf4j.helpers.NOPLogger' in probe['runs'][1]['stdout'], 'Logger-selection change missing')
        if n == 133:
            jars = read_json(base / 'breaking/jar_inspection.json')['artifacts']
            api = next(jar for jar in jars if '/log4j-api/2.17.2/' in jar['resolved_path'])
            require(not api['classes']['org.apache.logging.log4j.util.ServiceLoaderUtil']['present'], 'Retained Log4j API unexpectedly contains ServiceLoaderUtil')
            caller = (base / 'breaking/log4j-core-2.18.0_ThreadContextDataInjector_javap.txt').read_text()
            require('org/apache/logging/log4j/util/ServiceLoaderUtil.loadServices' in caller, 'Updated Core call missing')
        if n == 135:
            diagnostic = read_json(base / 'class_origins_results.json')
            require([r['image_id'] for r in diagnostic['runs']] == [s['image_id'] for s in snapshots], 'Class-origin probe used different images')
            for run in diagnostic['runs']:
                require(run['exit_code'] == 0 and run['counts'] == {'tests': 1, 'failures': 0, 'errors': 0, 'skipped': 0}, 'Unexpected probe counts')
                require(any(r['resource'].endswith('/JsonKey.class') and r['origin'] == 'ABSENT' for r in run['resources']), 'JsonKey resource absence missing')
            jars = read_json(base / 'breaking/jar_inspection.json')['artifacts']
            annotations = next(j for j in jars if '/jackson-annotations/2.11.2/' in j['resolved_path'])
            caller = (base / 'breaking/jackson-databind-2.13.3_JacksonAnnotationIntrospector_javap.txt').read_text()
            require('com/fasterxml/jackson/annotation/JsonKey' in caller and not annotations['classes']['com.fasterxml.jackson.annotation.JsonKey']['present'], 'Jackson missing-type evidence differs')
        result = subprocess.run([sys.executable, str(ROOT / f'scripts/append_case_{n}.py')], cwd=ROOT, capture_output=True, text=True)
        require(result.returncode == 0 and path.read_bytes() == original, 'Append idempotency check failed: ' + result.stderr)
        checked[str(n)] = {'assessment': expected[2], 'binary_linkage_incompatibility': expected[3], 'pre_build_status': 'SUCCESS', 'breaking_build_status': 'FAILURE', 'pre_counts': expected[0], 'breaking_counts': expected[1], 'original_images_run': 2, 'manifest_files_checked': len(manifest), 'append_idempotent': True}
    output = {'passed': True, 'classification_records': 135, 'counts_through_135': dict(Counter(r['behavioral_status'] for r in rows)), 'previous_130_records_byte_preserved': True, 'verified_repairs_and_case14_patch_byte_preserved': True, 'automated_triage_kept_separate': True, 'human_review_pending_for_new_cases': True, 'cases': checked}
    (ROOT / 'results/cases131_135_completion_check.json').write_text(json.dumps(output, indent=2), encoding='utf-8')
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
