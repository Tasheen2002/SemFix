"""Validate Cases 106-110 without changing earlier records or evidence."""
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
BACKUP = ROOT / 'results/backups/before_cases106_110'
EXPECTED = {
    106: ((95, 0, 0, 3), (89, 2, 0, 1), 'NON_BEHAVIORAL', 'YES'),
    107: ((300, 0, 0, 0), (161, 0, 15, 0), 'NON_BEHAVIORAL', 'YES'),
    108: ((5, 0, 0, 0), (5, 0, 3, 0), 'NON_BEHAVIORAL', 'YES'),
    109: ((223, 0, 0, 3), (223, 0, 54, 3), 'PROVISIONAL_BEHAVIORAL', 'NO'),
    110: ((32, 0, 0, 0), (18, 0, 5, 0), 'NON_BEHAVIORAL', 'YES'),
}

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
    if n == 106:
        old = (base / 'pre/poi-ooxml-4.1.2_POIXMLTextExtractor_javap.txt').read_text()
        new = (base / 'breaking/poi-ooxml-5.2.0_POIXMLTextExtractor_javap.txt').read_text()
        core = (base / 'breaking/poi-4.1.2_POITextExtractor_javap.txt').read_text()
        require('public abstract class org.apache.poi.ooxml.extractor.POIXMLTextExtractor extends org.apache.poi.extractor.POITextExtractor' in old, 'Old OOXML inheritance differs')
        require('public interface org.apache.poi.ooxml.extractor.POIXMLTextExtractor extends org.apache.poi.extractor.POITextExtractor' in new and 'public abstract class org.apache.poi.extractor.POITextExtractor' in core, 'POI interface/class incompatibility evidence differs')
    elif n == 107:
        provider = (base / 'breaking/junit-jupiter-params-5.9.2_MethodArgumentsProvider_javap.txt').read_text()
        platform = (base / 'breaking/junit-platform-commons-1.9.1_ReflectionUtils_javap.txt').read_text()
        require('ReflectionUtils.parseQualifiedMethodName:(Ljava/lang/String;)[Ljava/lang/String;' in provider and 'parseQualifiedMethodName' not in platform, 'JUnit missing-method evidence differs')
    elif n == 108:
        old = (base / 'pre/sshd-common-2.9.2_WaitableFuture_javap.txt').read_text()
        new = (base / 'breaking/sshd-common-2.10.0_WaitableFuture_javap.txt').read_text()
        core = (base / 'breaking/sshd-core-2.9.2_SshServer_javap.txt').read_text()
        require('await(java.time.Duration)' in old and 'await(java.time.Duration)' not in new and 'await(java.time.Duration, org.apache.sshd.common.future.CancelOption...)' in new, 'SSHD await descriptors differ from assessment')
        require('CloseFuture.await:(Ljava/time/Duration;)Z' in core, 'Old SSHD caller descriptor missing')
        diagnostic = read_json(base / 'connection_debug_results.json')
        require(diagnostic['exit_code'] == 1 and diagnostic['counts'] == {'tests': 1, 'failures': 0, 'errors': 1, 'skipped': 0}, 'Unexpected connection diagnostic counts')
        require(diagnostic['image_id'] == read_json(base / 'breaking/archive_summary.json')['image_id'], 'Diagnostic image differs')
        trace = (base / 'connection_debug.log').read_text()
        require("NoSuchMethodError: 'boolean org.apache.sshd.common.future.DefaultKeyExchangeFuture.await(java.time.Duration)'" in trace and 'AbstractSession.doKexNegotiation' in trace, 'Connection-reset root cause not demonstrated')
    elif n == 109:
        probe = read_json(base / 'annotation_probe_results.json')
        require(probe['compile_exit_code'] == 0 and probe['class_major_version'] == 55, 'Probe compilation differs')
        require(digest(base / 'annotation_probe_classes/AnnotationCompatibilityProbe.class') == probe['class_sha256'], 'Shared probe class changed')
        require([r['exit_code'] for r in probe['runs']] == [0, 1], 'Guice probe outcomes differ')
        require('binding=Key[' in probe['runs'][0]['stdout'] and 'is not a binding annotation' in probe['runs'][1]['stderr'], 'Guice behavioral difference missing')
        for r in probe['runs']:
            require('@javax.inject.Qualifier()' in r['stdout'], 'Existing qualifier annotation missing')
            require(r['image_id'] == read_json(base / r['phase'] / 'archive_summary.json')['image_id'], 'Guice probe image differs')
        old = (base / 'pre/guice-5.1.0_Annotations_javap.txt').read_text()
        new = (base / 'breaking/guice-7.0.0_Annotations_javap.txt').read_text()
        require('class javax/inject/Qualifier' in old and 'class jakarta/inject/Qualifier' in new, 'Guice annotation-checker evidence differs')
        signature = 'get(java.lang.Class<T>, java.lang.Class<? extends java.lang.annotation.Annotation>)'
        require(all(signature in (base / phase / name).read_text() for phase, name in [('pre', 'guice-5.1.0_Key_javap.txt'), ('breaking', 'guice-7.0.0_Key_javap.txt')]), 'Public Guice API signature differs')
    elif n == 110:
        majors = []
        for phase in ('pre', 'breaking'):
            jars = read_json(base / phase / 'jar_inspection.json')['artifacts']
            require(len(jars) == 1, 'Unexpected Spring TX artifacts')
            majors.append(jars[0]['classes']['org.springframework.transaction.TransactionDefinition']['major_version'])
        require(majors == [52, 61], 'Spring TX bytecode evidence differs')

def main():
    path = ROOT / 'results/behavioral_classification.csv'
    original = path.read_bytes()
    require(original.startswith((BACKUP / 'behavioral_classification.csv').read_bytes()), 'Original 105 records changed')
    rows = read_rows(path)
    candidates = read_rows(ROOT / 'results/test_failure_candidates.csv')
    require(len(rows) == 110 and len({r['case_id'] for r in rows}) == 110, 'Missing/duplicate case records')
    require(all(None not in r and all(v is not None for v in r.values()) for r in rows), 'Malformed CSV rows')
    require([r['case_id'] for r in rows] == [r['case_id'] for r in candidates[:110]], 'Candidate order differs')
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
            if n == 106:
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
        pom = 'messaging/pom.xml' if n == 110 else 'pom.xml'
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
    output = {'passed': True, 'classification_records': 110, 'counts_through_110': dict(Counter(r['behavioral_status'] for r in rows)), 'previous_105_records_byte_preserved': True, 'verified_repairs_and_case14_patch_byte_preserved': True, 'automated_triage_kept_separate': True, 'human_review_pending_for_new_cases': True, 'cases': checked}
    (ROOT / 'results/cases106_110_completion_check.json').write_text(json.dumps(output, indent=2), encoding='utf-8')
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
