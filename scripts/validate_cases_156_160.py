"""Validate Cases 156-160 without changing earlier records or evidence."""
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
BACKUP = ROOT / 'results/backups/before_cases156_160'
EXPECTED = {156: ((72, 0, 0, 0), (72, 2, 0, 0), 'PROVISIONAL_BEHAVIORAL', 'NO'),
 157: ((69, 0, 0, 2), (57, 4, 46, 2), 'NON_BEHAVIORAL', 'YES'),
 158: ((26, 0, 0, 0), (26, 1, 0, 0), 'PROVISIONAL_BEHAVIORAL', 'NO'),
 159: ((739, 0, 0, 0), (708, 0, 12, 0), 'PROVISIONAL_BEHAVIORAL', 'NO'),
 160: ((180, 0, 0, 9), (134, 0, 82, 4), 'NON_BEHAVIORAL', 'YES')}
POM_PATHS = {157: 'avans/pom.xml'}

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
    require(set(EXPECTED) == set(range(156, 161)), 'Expected data must cover the entire batch')
    path = ROOT / 'results/behavioral_classification.csv'
    original = path.read_bytes()
    require(original.startswith((BACKUP / 'behavioral_classification.csv').read_bytes()), 'Original 155 records changed')
    rows = read_rows(path)
    candidates = read_rows(ROOT / 'results/test_failure_candidates.csv')
    require(len(rows) == 160 and len({r['case_id'] for r in rows}) == 160, 'Missing/duplicate case records')
    require(all(None not in r and all(v is not None for v in r.values()) for r in rows), 'Malformed CSV rows')
    require([r['case_id'] for r in rows] == [r['case_id'] for r in candidates[:160]], 'Candidate order differs')
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
        if n in (156, 159):
            probe = read_json(base / 'logger_probe_results.json')
            require(digest(base / 'logger_probe_classes/LoggerSelectionProbe.class') == probe['class_sha256'], 'Logger probe class bytes differ')
            require([r['image_id'] for r in probe['runs']] == [m['image_id'] for m in snapshots], 'Logger probe image identities differ')
            require(all(r['exit_code'] == 0 for r in probe['runs']), 'Logger probe did not link/execute successfully')
            for run, summary in zip(probe['runs'], snapshots):
                report = next(r for r in summary['reports'] if r['test_class'] == probe['test_classpath_source'])
                cp = '/probe:' + ':'.join(p for p in report['classpath'].split(':') if p.endswith('.jar'))
                require(run['command'][run['command'].index('-cp') + 1] == cp, 'Logger probe classpath differs')
            require('logger=org.slf4j.helpers.NOPLogger' in probe['runs'][1]['stdout'] and 'logger=org.slf4j.helpers.NOPLogger' not in probe['runs'][0]['stdout'], 'Logger selection differs')
            require('Ignoring binding found at' in probe['runs'][1]['stderr'], 'Legacy binder diagnostic absent')
            jars = read_json(breaking / 'jar_inspection.json')['artifacts']
            require(any(j['classes']['org.slf4j.impl.StaticLoggerBinder']['present'] for j in jars), 'Retained binder absent')
            if n == 156:
                require('factory=uk.org.lidalia.slf4jtest.TestLoggerFactory' in probe['runs'][0]['stdout'], 'PRE test logger differs')
            if n == 159:
                require(any(j['classes']['ch.qos.logback.classic.LoggerContext']['present'] for j in jars), 'Retained Logback type absent')
                before_reports = {r['test_class']: r for r in snapshots[0]['reports']}
                collapsed = [r for r in snapshots[1]['reports'] if r['test_class'].split('.')[-1] in ('ServiceResourceCreateTest','ServiceResourceFindTest','ServiceResourceSearchTest','ServiceResourceUpdateTest')]
                require(len(collapsed) == 4 and sum(before_reports[r['test_class']]['counts']['tests'] for r in collapsed) == 35 and all(r['counts']['tests'] == 1 and r['counts']['errors'] == 1 for r in collapsed), 'Resource class-count collapse differs')
                require(all('Unable to acquire the logger context' in r['errors'][0]['stacktrace'] for r in collapsed), 'Resource logger-context cause differs')
        if n == 157:
            refs = read_json(base / 'missing_class_references.json')
            require(not refs['pre']['referring_classes'] and len(refs['breaking']['referring_classes']) == 4, 'Jackson missing-type scan differs')
            for phase, meta in refs.items():
                jar = next((base / phase / 'jars').glob('jackson-databind-*.jar'))
                require(digest(jar) == meta['jar_sha256'], 'Jackson reference scan bytes differ')
            jars = read_json(breaking / 'jar_inspection.json')['artifacts']
            require(all(not j['classes']['com.fasterxml.jackson.core.util.JacksonFeature']['present'] for j in jars), 'JacksonFeature unexpectedly present')
            require(any('/jackson-core/2.4.2/' in j['resolved_path'] for j in jars), 'Retained Jackson Core version differs')
            require('com/fasterxml/jackson/core/util/JacksonFeature' in (breaking / 'jackson-databind-2.13.3_DeserializationContext_javap.txt').read_text(), 'Updated Databind reference absent')
        if n == 158:
            diagnostic = read_json(base / 'message_probe_results.json')
            require([r['image_id'] for r in diagnostic['runs']] == [m['image_id'] for m in snapshots], 'Message diagnostic image identities differ')
            for run, phase in zip(diagnostic['runs'], ('pre', 'breaking')):
                require(run['exit_code'] == 0 and run['state']['Status'] == 'exited' and not run['state']['OOMKilled'], 'Message diagnostic failed')
                require(run['counts'] == dict(tests=1, failures=0, errors=0, skipped=0), 'Diagnostic counts incorrectly mixed with original counts')
                counts = dict.fromkeys(('tests','failures','errors','skipped'), 0)
                with tarfile.open(base / f'message_probe_{phase}_reports.tar') as archive:
                    for member in archive:
                        if member.isfile() and Path(member.name).name.startswith('TEST-') and member.name.endswith('.xml'):
                            root = ET.fromstring(archive.extractfile(member).read())
                            for key in counts:
                                counts[key] += int(root.get(key, '0'))
                require(counts == run['counts'], 'Diagnostic report counts differ')
                prefix = '' if phase == 'pre' else 'status code: 400, reason phrase: '
                require(run['messages'] == {'parent': [prefix + 'm'], 'client': [prefix + 'm (400 response phrase)']}, 'Exception message evidence differs')
                version = '4.5.1' if phase == 'pre' else '4.5.13'
                require(f'/httpclient/{version}/' in run['origins']['httpclient'], 'Loaded HttpClient origin differs')
                inspection = read_json(base / phase / 'jar_inspection.json')
                require({j['resolved_path'] for j in inspection['artifacts']} == set(run['resolved_http_paths']), 'Original HTTP JAR paths differ from diagnostic origins')
                code = (base / phase / f'httpclient-{version}_HttpResponseException_javap.txt').read_text()
                require('descriptor: (ILjava/lang/String;)V' in code, 'HTTP constructor descriptor differs')
                require(('String status code: %d' in code) == (phase == 'breaking'), 'Changed message construction differs')
        if n == 160:
            for phase, version, major in [('pre','10.15.2.0',53), ('breaking','10.16.1.1',61)]:
                jars = read_json(base / phase / 'jar_inspection.json')['artifacts']
                engine = next(j for j in jars if f'/derby/{version}/' in j['resolved_path'])
                require(engine['classes']['org.apache.derby.iapi.jdbc.JDBCBoot']['present'] and engine['classes']['org.apache.derby.iapi.jdbc.JDBCBoot']['major_version'] == major, 'Derby engine class-file evidence differs')
                tools = next(j for j in jars if '/derbytools/10.15.2.0/' in j['resolved_path'])
                require(tools['classes']['org.apache.derby.jdbc.EmbeddedDriver']['present'], 'Retained EmbeddedDriver absent')
            require(all(r['java_version'].startswith('11.') for r in snapshots[1]['reports']), 'Original runtime not Java 11')
            errors = [e for r in snapshots[1]['reports'] for e in r['errors']]
            require(Counter(e['type'] for e in errors) == {'java.lang.UnsupportedClassVersionError': 1, 'java.lang.NoClassDefFoundError': 81}, 'Derby error breakdown differs')
            first = next(e for e in errors if e['type'] == 'java.lang.UnsupportedClassVersionError')
            require('JDBCBoot' in first['stacktrace'] and '61.0' in first['stacktrace'] and '55.0' in first['stacktrace'], 'Runtime class-format error differs')
        result = subprocess.run([sys.executable, str(ROOT / f'scripts/append_case_{n}.py')], cwd=ROOT, capture_output=True, text=True)
        require(result.returncode == 0 and path.read_bytes() == original, 'Append idempotency check failed: ' + result.stderr)
        checked[str(n)] = {'assessment': expected[2], 'binary_linkage_incompatibility': expected[3], 'pre_build_status': 'SUCCESS', 'breaking_build_status': 'FAILURE', 'pre_counts': expected[0], 'breaking_counts': expected[1], 'original_images_run': 2, 'manifest_files_checked': len(manifest), 'append_idempotent': True}
    output = {'passed': True, 'classification_records': 160, 'counts_through_160': dict(Counter(r['behavioral_status'] for r in rows)), 'previous_155_records_byte_preserved': True, 'verified_repairs_and_case14_patch_byte_preserved': True, 'automated_triage_kept_separate': True, 'human_review_pending_for_new_cases': True, 'cases': checked}
    (ROOT / 'results/cases156_160_completion_check.json').write_text(json.dumps(output, indent=2), encoding='utf-8')
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
