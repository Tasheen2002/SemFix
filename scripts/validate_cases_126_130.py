"""Validate Cases 126-130 without changing earlier records or evidence."""
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
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BACKUP = ROOT / 'results/backups/before_cases126_130'
EXPECTED = {126: ((108, 0, 0, 1), (108, 0, 46, 1), 'NON_BEHAVIORAL', 'YES'), 127: ((62, 0, 0, 0), (62, 0, 1, 0), 'PROVISIONAL_BEHAVIORAL', 'NO'), 128: ((32, 0, 0, 0), (18, 1, 5, 0), 'NON_BEHAVIORAL', 'YES'), 129: ((67, 0, 0, 0), (67, 0, 48, 0), 'NON_BEHAVIORAL', 'YES'), 130: ((47, 0, 0, 0), (37, 0, 1, 0), 'NON_BEHAVIORAL', 'YES')}

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
    require(set(EXPECTED) == set(range(126, 131)), 'Expected data must cover the entire batch')
    path = ROOT / 'results/behavioral_classification.csv'
    original = path.read_bytes()
    require(original.startswith((BACKUP / 'behavioral_classification.csv').read_bytes()), 'Original 125 records changed')
    rows = read_rows(path)
    candidates = read_rows(ROOT / 'results/test_failure_candidates.csv')
    require(len(rows) == 130 and len({r['case_id'] for r in rows}) == 130, 'Missing/duplicate case records')
    require(all(None not in r and all(v is not None for v in r.values()) for r in rows), 'Malformed CSV rows')
    require([r['case_id'] for r in rows] == [r['case_id'] for r in candidates[:130]], 'Candidate order differs')
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
            inspection = read_json(base / phase / 'jar_inspection.json')
            require(inspection['case_id'] == row['case_id'] and inspection['phase'] == phase, 'JAR inspection identity differs')
            for jar in inspection['artifacts']:
                require(digest(base / phase / 'jars' / Path(jar['resolved_path']).name) == jar['sha256'], 'JAR content differs from inspection')
        before, after = [s['source_and_pom_sha256'] for s in snapshots]
        pom = 'core/pom.xml' if n == 128 else 'pom.xml'
        require(before.keys() == after.keys() and [p for p in before if before[p] != after[p]] == [pom], 'Unexpected archived source/POM changes')
        poms = [read_json(base / phase / 'all_poms_sha256.json') for phase in ('pre', 'breaking')]
        require(poms[0].keys() == poms[1].keys() and [p for p in poms[0] if poms[0][p] != poms[1][p]] == [pom], 'Unexpected all-depth POM changes')
        comparison = read_json(base / 'all_poms_comparison.json')
        require(comparison['changed_poms'] == [pom], 'POM comparison differs')
        changes = [line for line in comparison['diffs'][pom].splitlines() if line.startswith(('-', '+')) and not line.startswith(('---', '+++'))]
        require(len(changes) == 2 and re.fullmatch(r'-\s*<version>' + re.escape(row['old_version']) + r'</version>', changes[0]) and re.fullmatch(r'\+\s*<version>' + re.escape(row['new_version']) + r'</version>', changes[1]), 'POM diff contains changes beyond the candidate version')
        require([int(row[k]) for k in ('pre_tests', 'breaking_tests', 'breaking_failures', 'breaking_errors')] == [expected[0][0], *expected[1][:3]], 'CSV test counts differ')
        if n == 127:
            probe = read_json(base / 'lexer_probe_results.json')
            require(probe['source_identical_between_images'] and probe['compile_exit_code'] == 0, 'Lexer probe compilation/source differs')
            require(before[probe['original_source_path']] == probe['original_source_sha256'], 'Probe lexer differs from baseline archive')
            require(all(digest(base / 'lexer_probe_classes' / name) == sha for name, sha in probe['class_sha256'].items()), 'Probe class bytes differ')
            require([r['image_id'] for r in probe['runs']] == [s['image_id'] for s in snapshots], 'Lexer probe used different images')
            require([r['exit_code'] for r in probe['runs']] == [0, 1] and all('deserialize(char[])' in r['stdout'] for r in probe['runs']), 'Lexer API diagnostic differs')
            require('initialized=class' in probe['runs'][0]['stdout'] and 'version 3 (expected 4)' in probe['runs'][1]['stderr'], 'Changed serialized-input acceptance missing')
        if n == 128:
            diagnostic = read_json(base / 'class_origins_results.json')
            require([r['image_id'] for r in diagnostic['runs']] == [s['image_id'] for s in snapshots], 'Class-origin probe used different images')
            for run in diagnostic['runs']:
                require(run['exit_code'] == 0 and run['counts'] == {'tests': 1, 'failures': 0, 'errors': 0, 'skipped': 0}, 'Unexpected probe counts')
                require(any(r['resource'].endswith('/JsonKey.class') and r['origin'] == 'ABSENT' for r in run['resources']), 'JsonKey resource absence missing')
        if n in (126, 128):
            version = row['new_version']
            caller = (base / 'breaking' / f'jackson-databind-{version}_JacksonAnnotationIntrospector_javap.txt').read_text()
            jars = read_json(base / 'breaking/jar_inspection.json')['artifacts']
            annotations = next(j for j in jars if '/jackson-annotations/' in j['resolved_path'])
            require('com/fasterxml/jackson/annotation/JsonKey' in caller and not annotations['classes']['com.fasterxml.jackson.annotation.JsonKey']['present'], 'Jackson missing-type evidence differs')
        if n == 129:
            probe = read_json(base / 'logger_probe_results.json')
            require(digest(base / 'pre/Case129LoggerProbe.class') == probe['class_sha256'], 'Logger probe bytecode differs')
            require([r['image_id'] for r in probe['runs']] == [s['image_id'] for s in snapshots], 'Logger probe used different images')
            require([r['exit_code'] for r in probe['runs']] == [0, 1] and 'NoSuchFieldError: EMPTY_BYTE_ARRAY' in probe['runs'][1]['stderr'], 'Missing-field probe differs')
            caller = (base / 'breaking/log4j-core-2.15.0_ConfigurationSource_javap.txt').read_text()
            owner = (base / 'breaking/log4j-api-2.12.1_Constants_javap.txt').read_text()
            require('org/apache/logging/log4j/util/Constants.EMPTY_BYTE_ARRAY:[B' in caller and 'EMPTY_BYTE_ARRAY' not in owner, 'Field linkage evidence differs')
        if n == 130:
            jars = read_json(base / 'breaking/jar_inspection.json')['artifacts']
            sentry = next(j for j in jars if '/dropwizard-sentry/' in j['resolved_path'])
            require('META-INF/services/io.dropwizard.logging.AppenderFactory' in sentry['services'], 'Legacy appender registration missing')
            caller = (base / 'breaking/dropwizard-sentry-4.0.0_SentryAppenderFactory_javap.txt').read_text()
            with zipfile.ZipFile(base / 'breaking/jars/dropwizard-logging-2.1.6.jar') as logging:
                require('extends io.dropwizard.logging.common.AbstractAppenderFactory' in caller and 'io/dropwizard/logging/common/AbstractAppenderFactory.class' not in logging.namelist(), 'Missing superclass evidence differs')
        result = subprocess.run([sys.executable, str(ROOT / f'scripts/append_case_{n}.py')], cwd=ROOT, capture_output=True, text=True)
        require(result.returncode == 0 and path.read_bytes() == original, 'Append idempotency check failed: ' + result.stderr)
        checked[str(n)] = {'assessment': expected[2], 'binary_linkage_incompatibility': expected[3], 'pre_build_status': 'SUCCESS', 'breaking_build_status': 'FAILURE', 'pre_counts': expected[0], 'breaking_counts': expected[1], 'original_images_run': 2, 'manifest_files_checked': len(manifest), 'append_idempotent': True}
    output = {'passed': True, 'classification_records': 130, 'counts_through_130': dict(Counter(r['behavioral_status'] for r in rows)), 'previous_125_records_byte_preserved': True, 'verified_repairs_and_case14_patch_byte_preserved': True, 'automated_triage_kept_separate': True, 'human_review_pending_for_new_cases': True, 'cases': checked}
    (ROOT / 'results/cases126_130_completion_check.json').write_text(json.dumps(output, indent=2), encoding='utf-8')
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
