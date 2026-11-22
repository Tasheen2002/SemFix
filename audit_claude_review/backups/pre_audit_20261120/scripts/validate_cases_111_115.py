"""Validate Cases 111-115 without changing earlier records or evidence."""
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
BACKUP = ROOT / 'results/backups/before_cases111_115'
EXPECTED = {111: ((88, 0, 0, 3), (82, 1, 0, 1), 'NON_BEHAVIORAL', 'YES'),
 112: ((62, 0, 0, 0), (62, 0, 1, 0), 'PROVISIONAL_BEHAVIORAL', 'NO'),
 113: ((787, 0, 0, 0), (529, 2, 0, 0), 'PROVISIONAL_BEHAVIORAL', 'NO'),
 114: ((190, 0, 0, 36), (52, 0, 22, 0), 'PROVISIONAL_BEHAVIORAL', 'NO'),
 115: ((89, 0, 0, 3), (83, 2, 0, 1), 'NON_BEHAVIORAL', 'YES')}


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

def validate_mechanism(n, base):
    if n == 111:
        caller = (base / 'breaking/poi-scratchpad-5.2.1_HWPFDocumentCore_javap.txt').read_text()
        core = (base / 'breaking/poi-4.1.2_IOUtils_javap.txt').read_text()
        require('IOUtils.toByteArray:(Ljava/io/InputStream;II)[B' in caller, 'Scratchpad caller descriptor differs')
        require('toByteArray(java.io.InputStream, long, int)' in core and 'toByteArray(java.io.InputStream, int, int)' not in core, 'Retained POI overload evidence differs')
    elif n == 112:
        probe = read_json(base / 'lexer_probe_results.json')
        require(probe['compile_exit_code'] == 0 and probe['source_identical_between_images'], 'Lexer diagnostic compilation/source differs')
        source = read_json(base / 'pre/archive_summary.json')['source_and_pom_sha256']
        require(source[probe['original_source_path']] == probe['original_source_sha256'], 'Probe lexer differs from original source')
        for name, sha256 in probe['class_sha256'].items():
            require(digest(base / 'lexer_probe_classes' / name) == sha256, 'Shared lexer/probe bytecode changed')
        require([r['exit_code'] for r in probe['runs']] == [0, 1], 'Lexer diagnostic outcomes differ')
        for run in probe['runs']:
            require('ATNDeserializer.deserialize(char[])' in run['stdout'], 'Compatible deserializer method missing')
            require(run['image_id'] == read_json(base / run['phase'] / 'archive_summary.json')['image_id'], 'Lexer diagnostic image differs')
        require('initialized=class' in probe['runs'][0]['stdout'] and 'version 3 (expected 4)' in probe['runs'][1]['stderr'], 'Serialized-input behavioral difference missing')
    elif n == 113:
        control = read_json(base / 'subclass_control_results.json')
        require(control['exit_code'] == 0 and control['state']['ExitCode'] == 0 and control['counts'] == {'tests': 2, 'failures': 0, 'errors': 0, 'skipped': 0}, 'Mockito control did not pass exactly two tests')
        require(control['image_id'] == read_json(base / 'breaking/archive_summary.json')['image_id'], 'Mockito control image differs')
        require(len(control['reports']) == 2 and all('/mockito-core/5.1.0/' in r['classpath'] for r in control['reports']), 'Mockito upgrade was not retained in control')
        for phase, version, expected in [('pre', '4.11.0', 'ByteBuddyMockMaker'), ('breaking', '5.1.0', 'InlineByteBuddyMockMaker')]:
            text = (base / phase / f'mockito-core-{version}_DefaultMockitoPlugins_javap.txt').read_text()
            text = text[text.index('static {};'):]
            default = re.search(r'class org/mockito/plugins/MockMaker[\s\S]{0,300}?String org\.mockito\.internal\.creation\.bytebuddy\.(\w+)', text)
            require(default and default[1] == expected, 'Mockito default mapping differs')
        tracer = (base / 'breaking/opencensus-api-0.31.1_Tracer_javap.txt').read_text()
        span = (base / 'breaking/opencensus-api-0.31.1_Span_javap.txt').read_text()
        require('public final io.opencensus.trace.Span getCurrentSpan()' in tracer and 'CurrentSpanUtils.getCurrentSpan' in tracer, 'Final tracer method evidence differs')
        require('public final void addAnnotation(java.lang.String)' in span and 'addAnnotation:(Ljava/lang/String;Ljava/util/Map;)V' in span, 'Final annotation delegation evidence differs')
    elif n == 114:
        probe = read_json(base / 'precision_probe_results.json')
        require(probe['compile_exit_code'] == 0 and digest(base / 'precision_probe_classes/H2PrecisionProbe.class') == probe['class_sha256'], 'Shared JDBC probe compilation/bytecode differs')
        require([r['exit_code'] for r in probe['runs']] == [0, 1], 'JDBC diagnostic outcomes differ')
        require('VARCHAR(10000000)' in probe['sql'] and 'CREATE TABLE accepted' in probe['runs'][0]['stdout'], 'Old H2 acceptance not demonstrated')
        require('Precision' in probe['runs'][1]['stderr'] and '1048576' in probe['runs'][1]['stderr'], 'New H2 precision rejection missing')
        for run in probe['runs']:
            require(run['image_id'] == read_json(base / run['phase'] / 'archive_summary.json')['image_id'], 'JDBC diagnostic image differs')
        diff = probe['persistence_test_classpath_difference']
        require(diff['property'] == 'surefire.test.class.path' and diff['removed'] == ['/root/.m2/repository/com/h2database/h2/1.3.175/h2-1.3.175.jar'] and diff['added'] == ['/root/.m2/repository/com/h2database/h2/2.1.210/h2-2.1.210.jar'], 'Effective persistence classpath differs beyond H2')
        for phase in ('pre', 'breaking'):
            require(len(read_json(base / phase / 'resolved_test_classpaths.json')) == read_json(base / phase / 'archive_summary.json')['report_count'], 'Supplemental old-Surefire classpaths incomplete')
    elif n == 115:
        old = (base / 'pre/poi-ooxml-4.1.2_POIXMLTextExtractor_javap.txt').read_text()
        new = (base / 'breaking/poi-ooxml-5.2.2_POIXMLTextExtractor_javap.txt').read_text()
        core = (base / 'breaking/poi-4.1.2_POITextExtractor_javap.txt').read_text()
        require('public abstract class org.apache.poi.ooxml.extractor.POIXMLTextExtractor extends org.apache.poi.extractor.POITextExtractor' in old, 'Old OOXML inheritance differs')
        require('public interface org.apache.poi.ooxml.extractor.POIXMLTextExtractor extends org.apache.poi.extractor.POITextExtractor' in new and 'public abstract class org.apache.poi.extractor.POITextExtractor' in core, 'OOXML/POI interface mismatch evidence differs')


def main():
    path = ROOT / 'results/behavioral_classification.csv'
    original = path.read_bytes()
    require(original.startswith((BACKUP / 'behavioral_classification.csv').read_bytes()), 'Original 110 records changed')
    rows = read_rows(path)
    candidates = read_rows(ROOT / 'results/test_failure_candidates.csv')
    require(len(rows) == 115 and len({r['case_id'] for r in rows}) == 115, 'Missing/duplicate case records')
    require(all(None not in r and all(v is not None for v in r.values()) for r in rows), 'Malformed CSV rows')
    require([r['case_id'] for r in rows] == [r['case_id'] for r in candidates[:115]], 'Candidate order differs')
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
            log = (ROOT / row[phase + '_log']).read_text(encoding='utf-8', errors='replace')
            require(re.findall(r'BUILD (SUCCESS|FAILURE)', log) == [('SUCCESS' if phase == 'pre' else 'FAILURE')], 'Original Maven outcome differs')
            if n in (111, 115):
                runner = read_json(base / phase / 'randomized_summary.json')
                aggregate = runner['aggregate_counts']
                counts = tuple(aggregate[k] for k in ('tests', 'failures', 'errors', 'ignored'))
                require(summary['report_count'] == 0 and len(runner['retained_runner_files']) == (0 if phase == 'pre' else 4), 'Randomized-runner evidence differs')
                summaries = re.findall(r'^\[INFO\] Tests summary: (\d+) suites?, (\d+) tests?([^\r\n]*)', log, re.M)
                calculated = (sum(int(s[1]) for s in summaries), *[sum(sum(map(int, re.findall(r'(\d+) ' + term, s[2]))) for s in summaries) for term in ('failure', 'error', 'ignored')])
                require(calculated == counts, 'Original runner log counts differ')
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
        pom = 'src/core/persistence/pom.xml' if n == 114 else 'pom.xml'
        require(before.keys() == after.keys() and [p for p in before if before[p] != after[p]] == [pom], 'Unexpected archived source/POM changes')
        poms = [read_json(base / phase / 'all_poms_sha256.json') for phase in ('pre', 'breaking')]
        require(poms[0].keys() == poms[1].keys() and [p for p in poms[0] if poms[0][p] != poms[1][p]] == [pom], 'Unexpected all-depth POM changes')
        comparison = read_json(base / 'all_poms_comparison.json')
        require(comparison['changed_poms'] == [pom], 'POM comparison differs')
        changes = [line for line in comparison['diffs'][pom].splitlines() if line.startswith(('-', '+')) and not line.startswith(('---', '+++'))]
        require(len(changes) == 2 and re.fullmatch(r'-\s*<version>' + re.escape(row['old_version']) + r'</version>', changes[0]) and re.fullmatch(r'\+\s*<version>' + re.escape(row['new_version']) + r'</version>', changes[1]), 'POM diff contains changes beyond the candidate version')
        require([int(row[k]) for k in ('pre_tests', 'breaking_tests', 'breaking_failures', 'breaking_errors')] == [expected[0][0], *expected[1][:3]], 'CSV test counts differ')
        validate_mechanism(n, base)
        result = subprocess.run([sys.executable, str(ROOT / f'scripts/append_case_{n}.py')], cwd=ROOT, capture_output=True, text=True)
        require(result.returncode == 0 and path.read_bytes() == original, 'Append idempotency check failed: ' + result.stderr)
        checked[str(n)] = {'assessment': expected[2], 'binary_linkage_incompatibility': expected[3], 'pre_counts': expected[0], 'breaking_counts': expected[1], 'original_images_run': 2, 'manifest_files_checked': len(manifest), 'append_idempotent': True}
    output = {'passed': True, 'classification_records': 115, 'counts_through_115': dict(Counter(r['behavioral_status'] for r in rows)), 'previous_110_records_byte_preserved': True, 'verified_repairs_and_case14_patch_byte_preserved': True, 'automated_triage_kept_separate': True, 'human_review_pending_for_new_cases': True, 'cases': checked}
    (ROOT / 'results/cases111_115_completion_check.json').write_text(json.dumps(output, indent=2), encoding='utf-8')
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
