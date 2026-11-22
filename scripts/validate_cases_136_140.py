"""Validate Cases 136-140 without changing earlier records or evidence."""
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
BACKUP = ROOT / 'results/backups/before_cases136_140'
EXPECTED = {136: ((16, 0, 0, 0), (16, 0, 10, 0), 'NON_BEHAVIORAL', 'YES'),
 137: ((12, 0, 0, 0), (12, 2, 0, 0), 'NON_BEHAVIORAL', 'YES'),
 138: ((59, 0, 0, 0), (59, 20, 0, 0), 'NON_BEHAVIORAL', 'YES'),
 139: ((59, 0, 0, 0), (59, 20, 0, 0), 'NON_BEHAVIORAL', 'YES'),
 140: ((944, 0, 0, 0), (904, 1, 0, 0), 'PROVISIONAL_BEHAVIORAL', 'NO')}
POM_PATHS = {140: 'safeplace/pom.xml'}

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
    require(set(EXPECTED) == set(range(136, 141)), 'Expected data must cover the entire batch')
    path = ROOT / 'results/behavioral_classification.csv'
    original = path.read_bytes()
    require(original.startswith((BACKUP / 'behavioral_classification.csv').read_bytes()), 'Original 135 records changed')
    rows = read_rows(path)
    candidates = read_rows(ROOT / 'results/test_failure_candidates.csv')
    require(len(rows) == 140 and len({r['case_id'] for r in rows}) == 140, 'Missing/duplicate case records')
    require(all(None not in r and all(v is not None for v in r.values()) for r in rows), 'Malformed CSV rows')
    require([r['case_id'] for r in rows] == [r['case_id'] for r in candidates[:140]], 'Candidate order differs')
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
            if n in (138, 139, 140):
                reconciled = read_json(base / phase / 'reconciled_counts.json')
                reconcile = runpy.run_path(str(ROOT / 'scripts/reconcile_cases_136_140_reports.py'))['reconcile']
                require(reconciled == reconcile(base / phase), 'TestNG reconciliation differs')
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
        if n == 136:
            jars = read_json(breaking / 'jar_inspection.json')['artifacts']
            common = next(jar for jar in jars if '/jersey-common/2.32/' in jar['resolved_path'])
            require(not common['classes']['org.glassfish.jersey.internal.DynamicFeatureConfigurator']['present'], 'Missing Jersey class unexpectedly present')
            caller = (breaking / 'jersey-server-2.39.1_ApplicationHandler_javap.txt').read_text()
            require('org/glassfish/jersey/internal/DynamicFeatureConfigurator' in caller, 'Updated Jersey class reference missing')
        if n == 137:
            binder = 'org.slf4j.impl.StaticLoggerBinder'
            for phase, version, present in [('pre', '1.2.11', True), ('breaking', '1.4.4', False)]:
                jars = read_json(base / phase / 'jar_inspection.json')['artifacts']
                classic = next(jar for jar in jars if f'/logback-classic/{version}/' in jar['resolved_path'])
                require(classic['classes'][binder]['present'] == present, 'Logback binder evidence differs')
            caller = (breaking / 'slf4j-api-1.7.36_LoggerFactory_javap.txt').read_text()
            require('org/slf4j/impl/StaticLoggerBinder.getSingleton' in caller and 'java/lang/NoClassDefFoundError' in caller, 'Direct binder call and fallback evidence missing')
        if n in (138, 139):
            previous = (base / 'pre/snakeyaml-1.13_CollectionNode_javap.txt').read_text()
            current = (breaking / f"snakeyaml-{row['new_version']}_CollectionNode_javap.txt").read_text()
            caller = (breaking / 'raml-parser-0.9-SNAPSHOT_TemplateResolver$ResourceTemplateMerger_javap.txt').read_text()
            require('java.lang.Boolean getFlowStyle()' in previous and 'DumperOptions$FlowStyle getFlowStyle()' in current, 'SnakeYAML return signature evidence differs')
            require('SequenceNode.getFlowStyle:()Ljava/lang/Boolean;' in caller, 'Old RAML call descriptor missing')
        if n == 140:
            probe = read_json(base / 'lexer_probe_results.json')
            require(probe['compile_exit_code'] == 0 and probe['source_identical_between_images'], 'Generated lexer probe compilation/source differs')
            require(all(digest(base / phase / 'CstrSpecLexer.java') == probe['original_source_sha256'] for phase in ('pre', 'breaking')), 'Original generated lexer hashes differ')
            require(all(digest(base / 'lexer_probe_classes' / name) == sha for name, sha in probe['class_sha256'].items()), 'Probe class bytes differ')
            require([r['image_id'] for r in probe['runs']] == [s['image_id'] for s in snapshots], 'Lexer probe used different images')
            require([r['exit_code'] for r in probe['runs']] == [0, 1] and all('deserialize(char[])' in r['stdout'] for r in probe['runs']), 'Lexer API diagnostic differs')
            require('initialized=class' in probe['runs'][0]['stdout'] and 'version 3 (expected 4)' in probe['runs'][1]['stderr'], 'Changed serialized-input acceptance missing')
        result = subprocess.run([sys.executable, str(ROOT / f'scripts/append_case_{n}.py')], cwd=ROOT, capture_output=True, text=True)
        require(result.returncode == 0 and path.read_bytes() == original, 'Append idempotency check failed: ' + result.stderr)
        checked[str(n)] = {'assessment': expected[2], 'binary_linkage_incompatibility': expected[3], 'pre_build_status': 'SUCCESS', 'breaking_build_status': 'FAILURE', 'pre_counts': expected[0], 'breaking_counts': expected[1], 'original_images_run': 2, 'manifest_files_checked': len(manifest), 'append_idempotent': True}
    output = {'passed': True, 'classification_records': 140, 'counts_through_140': dict(Counter(r['behavioral_status'] for r in rows)), 'previous_135_records_byte_preserved': True, 'verified_repairs_and_case14_patch_byte_preserved': True, 'automated_triage_kept_separate': True, 'human_review_pending_for_new_cases': True, 'cases': checked}
    (ROOT / 'results/cases136_140_completion_check.json').write_text(json.dumps(output, indent=2), encoding='utf-8')
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
