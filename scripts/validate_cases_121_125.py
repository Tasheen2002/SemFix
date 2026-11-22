"""Validate Cases 121-125 without changing earlier records or evidence."""
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
BACKUP = ROOT / 'results/backups/before_cases121_125'
EXPECTED = {121: ((32, 0, 0, 0), (0, 0, 0, 0), 'NON_BEHAVIORAL', 'YES'),
 122: ((48, 0, 0, 0), (40, 0, 7, 0), 'NON_BEHAVIORAL', 'YES'),
 123: ((32, 0, 0, 0), (18, 1, 5, 0), 'NON_BEHAVIORAL', 'YES'),
 124: ((42, 0, 0, 0), (42, 0, 16, 0), 'NON_BEHAVIORAL', 'YES'),
 125: ((16, 0, 0, 0), (16, 0, 10, 0), 'NON_BEHAVIORAL', 'YES')}


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
    if n == 121:
        runtime = read_json(base / 'plugin_runtime_inspection.json')
        require(runtime['image_id'] == read_json(base / 'breaking/archive_summary.json')['image_id'], 'Plugin realm image differs')
        urls = [u['path'] for u in runtime['plugin_urls']]
        require(any('/maven-surefire-plugin/2.19.1/' in p for p in urls) and any('/junit-platform-surefire-provider/1.3.2/' in p for p in urls) and any('/common-java5/2.22.0/' in p for p in urls), 'Original mixed plugin realm not demonstrated')
        require('Original Maven failure' in runtime['path_source'], 'Plugin realm incorrectly attributed to project XML')
        utility = (base / 'breaking/common-java5-2.22.0_StringUtils_javap.txt').read_text()
        caller = (base / 'breaking/maven-surefire-common-2.19.1_AbstractForkInputStream_javap.txt').read_text()
        require(' requireNonNull(' not in utility, 'Expected missing utility method is present')
        require('StringUtils.requireNonNull:(Ljava/lang/Object;)Ljava/lang/Object;' in caller, 'Old runner caller descriptor missing')
        require(read_json(base / 'breaking/archive_summary.json')['report_count'] == 0, 'Expected provider failure before per-test XML')
    elif n == 122:
        jars = read_json(base / 'breaking/jar_inspection.json')['artifacts']
        core = next(j for j in jars if '/jackson-core/2.9.8/' in j['resolved_path'])
        require(not core['classes']['com.fasterxml.jackson.core.util.JacksonFeature']['present'], 'Missing Core type unexpectedly present')
        references = read_json(base / 'jackson_feature_references.json')
        direct = [r for r in references['references'] if r['direct_JacksonFeature_descriptor']]
        require(len(direct) == 1 and direct[0]['class'] == 'com.fasterxml.jackson.databind.DeserializationContext', 'Exact JacksonFeature reference not separated from prefix matches')
        caller = (base / 'breaking' / direct[0]['file']).read_text()
        require('JacksonFeatureSet.isEnabled:(Lcom/fasterxml/jackson/core/util/JacksonFeature;)Z' in caller, 'New Databind reference descriptor missing')
    elif n == 123:
        diagnostic = read_json(base / 'class_origins_results.json')
        require(len(diagnostic['runs']) == 2, 'Class-origin diagnostic incomplete')
        for run in diagnostic['runs']:
            require(run['exit_code'] == 0 and run['counts'] == {'tests': 1, 'failures': 0, 'errors': 0, 'skipped': 0}, 'Unexpected class-origin probe counts')
            require(run['image_id'] == read_json(base / run['phase'] / 'archive_summary.json')['image_id'], 'Class-origin probe image differs')
            require(any(r['resource'].endswith('/JsonKey.class') and r['origin'] == 'ABSENT' for r in run['resources']), 'Missing annotation not demonstrated in test classloader')
        jars = read_json(base / 'breaking/jar_inspection.json')['artifacts']
        annotations = next(j for j in jars if '/jackson-annotations/2.11.2/' in j['resolved_path'])
        require(not annotations['classes']['com.fasterxml.jackson.annotation.JsonKey']['present'], 'JsonKey unexpectedly present')
        new = (base / 'breaking/jackson-databind-2.13.3_JacksonAnnotationIntrospector_javap.txt').read_text()
        old = (base / 'pre/jackson-databind-2.9.10.8_JacksonAnnotationIntrospector_javap.txt').read_text()
        require('com/fasterxml/jackson/annotation/JsonKey' in new and 'com/fasterxml/jackson/annotation/JsonKey' not in old, 'Introduced annotation reference differs')
    elif n == 124:
        diagnostic = read_json(base / 'class_origins_results.json')
        for run in diagnostic['runs']:
            require(run['exit_code'] == 0 and run['counts'] == {'tests': 1, 'failures': 0, 'errors': 0, 'skipped': 0}, 'Unexpected Spring resource-inspection counts')
            require(run['image_id'] == read_json(base / run['phase'] / 'archive_summary.json')['image_id'], 'Spring resource-inspection image differs')
        inspections = [read_json(base / phase / 'affected_module_jar_inspection.json') for phase in ('pre', 'breaking')]
        require(all('affected module' in i['path_source'] for i in inspections), 'Affected Spring inspection confused with other module classpath')
        jars = [i['artifacts'] for i in inspections]
        require(all(len(j) == 1 for j in jars), 'Unexpected affected-module API artifacts')
        require('/2.3.2/' in jars[0][0]['resolved_path'] and '/3.0.1/' in jars[1][0]['resolved_path'], 'Actual Spring API versions differ')
        require(jars[0][0]['classes']['javax.xml.bind.JAXBException']['present'] and not jars[1][0]['classes']['javax.xml.bind.JAXBException']['present'] and jars[1][0]['classes']['jakarta.xml.bind.JAXBException']['present'], 'Namespace/missing-type evidence differs')
        breaking_resources = {r['resource']: r['origin'] for r in diagnostic['runs'][1]['resources']}
        require(breaking_resources['javax/xml/bind/JAXBException.class'] == 'ABSENT' and '/3.0.1/' in breaking_resources['jakarta/xml/bind/JAXBException.class'], 'Actual Spring test loader sees unexpected namespace')
    elif n == 125:
        jars = read_json(base / 'breaking/jar_inspection.json')['artifacts']
        util = next(j for j in jars if '/jetty-util/9.4.35.v20201120/' in j['resolved_path'])
        require(not util['classes']['org.eclipse.jetty.util.component.AbstractLifeCycle$StopException']['present'], 'Missing Jetty lifecycle type unexpectedly present')
        references = read_json(base / 'stop_exception_references.json')['references']
        server = next(r for r in references if r['class'] == 'org.eclipse.jetty.server.Server')
        require('org/eclipse/jetty/util/component/AbstractLifeCycle$StopException' in (base / 'breaking' / server['file']).read_text(), 'New Server type reference missing')


def main():
    path = ROOT / 'results/behavioral_classification.csv'
    original = path.read_bytes()
    require(original.startswith((BACKUP / 'behavioral_classification.csv').read_bytes()), 'Original 120 records changed')
    rows = read_rows(path)
    candidates = read_rows(ROOT / 'results/test_failure_candidates.csv')
    require(len(rows) == 125 and len({r['case_id'] for r in rows}) == 125, 'Missing/duplicate case records')
    require(all(None not in r and all(v is not None for v in r.values()) for r in rows), 'Malformed CSV rows')
    require([r['case_id'] for r in rows] == [r['case_id'] for r in candidates[:125]], 'Candidate order differs')
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
            counts = tuple(summary['aggregate_counts'][k] for k in ('tests', 'failures', 'errors', 'skipped'))
            summaries = re.findall(r'^(?:\[[A-Z]+\] )?Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)[ \t]*$', log, re.M)
            calculated = tuple(map(sum, zip(*(map(int, s) for s in summaries)))) if summaries else (0, 0, 0, 0)
            require(calculated == counts, f'Case {n} Maven/XML counts differ')
            require(counts == expected[index], f'Case {n} {phase} expected counts differ')
            if n != 121 or phase == 'breaking':
                if n == 121:
                    inspection = read_json(base / 'plugin_runtime_inspection.json')
                else:
                    filename = 'affected_module_jar_inspection.json' if n == 124 else 'jar_inspection.json'
                    inspection = read_json(base / phase / filename)
                require(inspection['case_id'] == row['case_id'] and inspection['phase'] == phase, 'JAR inspection identity differs')
                for jar in inspection['artifacts']:
                    require(digest(base / phase / 'jars' / Path(jar['resolved_path']).name) == jar['sha256'], 'JAR content differs from inspection')
        before, after = [s['source_and_pom_sha256'] for s in snapshots]
        pom = {121: 'core/pom.xml', 123: 'core/pom.xml', 124: 'camunda-bpm-camel-spring/pom.xml'}.get(n, 'pom.xml')
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
        checked[str(n)] = {'assessment': expected[2], 'binary_linkage_incompatibility': expected[3], 'pre_build_status': 'SUCCESS', 'breaking_build_status': 'FAILURE', 'test_discovery_aborted': n == 121, 'pre_counts': expected[0], 'breaking_counts': expected[1], 'original_images_run': 2, 'manifest_files_checked': len(manifest), 'append_idempotent': True}
    output = {'passed': True, 'classification_records': 125, 'counts_through_125': dict(Counter(r['behavioral_status'] for r in rows)), 'previous_120_records_byte_preserved': True, 'verified_repairs_and_case14_patch_byte_preserved': True, 'automated_triage_kept_separate': True, 'human_review_pending_for_new_cases': True, 'cases': checked}
    (ROOT / 'results/cases121_125_completion_check.json').write_text(json.dumps(output, indent=2), encoding='utf-8')
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
