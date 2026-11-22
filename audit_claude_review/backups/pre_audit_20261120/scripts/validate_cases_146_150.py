"""Validate Cases 146-150 without changing earlier records or evidence."""
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
BACKUP = ROOT / 'results/backups/before_cases146_150'
EXPECTED = {146: ((12, 0, 0, 0), (12, 2, 0, 0), 'NON_BEHAVIORAL', 'YES'),
 147: ((38, 0, 0, 0), (38, 0, 12, 0), 'PROVISIONAL_BEHAVIORAL', 'NO'),
 148: ((389, 0, 0, 0), (235, 0, 5, 0), 'PROVISIONAL_BEHAVIORAL', 'NO'),
 149: ((16, 0, 0, 0), (16, 0, 10, 0), 'NON_BEHAVIORAL', 'YES'),
 150: ((757, 0, 0, 0), (726, 0, 12, 0), 'PROVISIONAL_BEHAVIORAL', 'NO')}
POM_PATHS = {}

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
    require(set(EXPECTED) == set(range(146, 151)), 'Expected data must cover the entire batch')
    path = ROOT / 'results/behavioral_classification.csv'
    original = path.read_bytes()
    require(original.startswith((BACKUP / 'behavioral_classification.csv').read_bytes()), 'Original 145 records changed')
    rows = read_rows(path)
    candidates = read_rows(ROOT / 'results/test_failure_candidates.csv')
    require(len(rows) == 150 and len({r['case_id'] for r in rows}) == 150, 'Missing/duplicate case records')
    require(all(None not in r and all(v is not None for v in r.values()) for r in rows), 'Malformed CSV rows')
    require([r['case_id'] for r in rows] == [r['case_id'] for r in candidates[:150]], 'Candidate order differs')
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
            totals = summary['aggregate_counts']
            if n == 149:
                reconciled = read_json(base / phase / 'reconciled_counts.json')
                reconcile = runpy.run_path(str(ROOT / 'scripts/reconcile_case_149_reports.py'))['reconcile']
                require(reconciled == reconcile(base / phase), 'Request/teardown reconciliation differs')
                totals = reconciled['aggregate_counts']
            counts = tuple(totals[k] for k in ('tests', 'failures', 'errors', 'skipped'))
            summaries = re.findall(r'^(?:\[[A-Z]+\] )?Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)[ \t]*$', log, re.M)
            calculated = tuple(map(sum, zip(*(map(int, s) for s in summaries)))) if summaries else (0, 0, 0, 0)
            require(calculated == counts, f'Case {n} Maven/XML counts differ: {calculated} != {counts}')
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
        breaking = base / 'breaking'
        require(all((base / phase / 'jar_inspection.json').is_file() for phase in ('pre', 'breaking')), 'Resolved artifact evidence absent')
        require(row['main_exception'] in (ROOT / row['breaking_log']).read_text(errors='replace'), 'Main exception absent from original failure log')
        if n == 146:
            for phase, version, present in [('pre', '1.2.11', True), ('breaking', '1.4.0', False)]:
                jars = read_json(base / phase / 'jar_inspection.json')['artifacts']
                classic = next(j for j in jars if f'/logback-classic/{version}/' in j['resolved_path'])
                require(classic['classes']['org.slf4j.impl.StaticLoggerBinder']['present'] == present, 'Logback binder evidence differs')
            caller = (breaking / 'slf4j-api-1.7.36_LoggerFactory_javap.txt').read_text()
            require('org/slf4j/impl/StaticLoggerBinder.getSingleton' in caller and 'java/lang/NoClassDefFoundError' in caller, 'Direct SLF4J binder call evidence missing')
        if n in (147, 148, 150):
            probe = read_json(base / 'logger_probe_results.json')
            require(digest(base / 'logger_probe_classes/LoggerSelectionProbe.class') == probe['class_sha256'], 'Logger probe class hash differs')
            require([r['image_id'] for r in probe['runs']] == [m['image_id'] for m in snapshots], 'Logger probe image identities differ')
            require(all(r['exit_code'] == 0 for r in probe['runs']), 'Logger probe did not execute successfully')
            require('logger=org.slf4j.helpers.NOPLogger' in probe['runs'][1]['stdout'] and 'logger=org.slf4j.helpers.NOPLogger' not in probe['runs'][0]['stdout'], 'Logger selection evidence differs')
            require('Ignoring binding found at' in probe['runs'][1]['stderr'], 'Legacy binding diagnostic absent')
            jars = read_json(breaking / 'jar_inspection.json')['artifacts']
            require(any(j['classes']['org.slf4j.impl.StaticLoggerBinder']['present'] for j in jars), 'Retained binder absent')
            if n == 147:
                for phase in ('pre', 'breaking'):
                    supplement = read_json(base / phase / 'mock_common_inspection.json')
                    require(supplement['case_id'] == row['case_id'] and supplement['phase'] == phase, 'Mock-common identity differs')
                    for jar in supplement['artifacts']:
                        require(digest(base / phase / 'jars' / Path(jar['resolved_path']).name) == jar['sha256'], 'Mock common hash differs')
                        require(jar['classes']['org.simplify4u.slf4jmock.internal.ProxyMock']['present'], 'Expected ProxyMock absent')
                caller = (breaking / 'slf4j-mock-common-2.3.0_LoggerAnnotationEngine_javap.txt').read_text()
                require('checkcast' in caller and 'org/simplify4u/slf4jmock/internal/ProxyMock' in caller, 'Mock caller cast absent')
            if n == 148:
                require('factory=ch.qos.logback.classic.LoggerContext' in probe['runs'][0]['stdout'], 'PRE factory differs')
                require(any(j['classes']['ch.qos.logback.classic.LoggerContext']['present'] for j in jars), 'LoggerContext unexpectedly absent')
        if n == 149:
            current = (breaking / 'jetty-server-9.4.49.v20220914_AllowedResourceAliasChecker$AllowedResourceAliasCheckListener_javap.txt').read_text()
            interface = (breaking / 'jetty-util-9.4.35.v20201120_LifeCycle$Listener_javap.txt').read_text()
            require('implements org.eclipse.jetty.util.component.LifeCycle$Listener' in current and 'void lifeCycleStarted(' in current and 'void lifeCycleFailure(' not in current, 'Jetty implementing class differs')
            require('public abstract void lifeCycleFailure(' in interface, 'Retained Jetty interface differs')
            counts = [read_json(base / phase / 'reconciled_counts.json') for phase in ('pre', 'breaking')]
            require(counts[0]['test_identities'] == counts[1]['test_identities'], 'Original test identities differ')
        result = subprocess.run([sys.executable, str(ROOT / f'scripts/append_case_{n}.py')], cwd=ROOT, capture_output=True, text=True)
        require(result.returncode == 0 and path.read_bytes() == original, 'Append idempotency check failed: ' + result.stderr)
        checked[str(n)] = {'assessment': expected[2], 'binary_linkage_incompatibility': expected[3], 'pre_build_status': 'SUCCESS', 'breaking_build_status': 'FAILURE', 'pre_counts': expected[0], 'breaking_counts': expected[1], 'original_images_run': 2, 'manifest_files_checked': len(manifest), 'append_idempotent': True}
    output = {'passed': True, 'classification_records': 150, 'counts_through_150': dict(Counter(r['behavioral_status'] for r in rows)), 'previous_145_records_byte_preserved': True, 'verified_repairs_and_case14_patch_byte_preserved': True, 'automated_triage_kept_separate': True, 'human_review_pending_for_new_cases': True, 'cases': checked}
    (ROOT / 'results/cases146_150_completion_check.json').write_text(json.dumps(output, indent=2), encoding='utf-8')
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
