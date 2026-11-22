"""Validate Cases 116-120 without changing earlier records or evidence."""
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
BACKUP = ROOT / 'results/backups/before_cases116_120'
EXPECTED = {116: ((7, 0, 0, 0), (0, 0, 0, 0), 'NON_BEHAVIORAL', 'NO'),
 117: ((72, 0, 0, 0), (72, 2, 0, 0), 'PROVISIONAL_BEHAVIORAL', 'NO'),
 118: ((47, 0, 0, 0), (37, 0, 1, 0), 'NON_BEHAVIORAL', 'NO'),
 119: ((5, 0, 0, 0), (5, 0, 2, 0), 'NON_BEHAVIORAL', 'YES'),
 120: ((13, 0, 0, 0), (13, 0, 6, 0), 'NON_BEHAVIORAL', 'YES')}


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
    if n == 116:
        before = read_json(base / 'pre/discovery_classpaths.json')
        after = read_json(base / 'breaking/discovery_classpaths.json')
        junit = '/root/.m2/repository/junit/junit/3.8.1/junit-3.8.1.jar'
        require(junit not in before['test_classpath'] and junit in after['test_classpath'], 'JUnit introduction differs from classpath evidence')
        require(any('/junit-vintage-engine/5.9.3/' in p for p in after['provider_classpath']), 'Vintage provider classpath evidence missing')
        chain = '\n'.join(after['dependency_chain_excerpt'])
        require('doxia-integration-tools' in chain and 'plexus-container-default' in chain and 'junit:junit:jar:3.8.1:compile' in chain, 'Selected transitive dependency chain differs')
        diagnostic = read_json(base / 'discovery_debug_results.json')
        require(diagnostic['exit_code'] == 1 and diagnostic['state']['Status'] == 'exited' and diagnostic['image_id'] == read_json(base / 'breaking/archive_summary.json')['image_id'], 'Discovery diagnostic image/outcome differs')
        require('Separate' in read_json(base / 'breaking/jar_inspection.json')['path_source'], 'Diagnostic provenance not distinguished from original XML')
        with tarfile.open(base / 'breaking/artifacts.tar') as archive:
            dumps = [archive.extractfile(m).read().decode(errors='replace') for m in archive if m.isfile() and m.name.endswith('.dump')]
        require(len(dumps) == 1 and 'Unsupported version of junit:junit: 3.8.1' in dumps[0] and '4.12 or later' in dumps[0], 'Original discovery root cause differs')
        vintage = (base / 'breaking/junit-vintage-engine-5.9.3_JUnit4VersionCheck_javap.txt').read_text()
        require('String 4.12' in vintage and 'Unsupported version of junit:junit:' in vintage, 'Vintage minimum-version guard differs')
        require(read_json(base / 'breaking/archive_summary.json')['report_count'] == 0, 'Expected no per-test XML before discovery')
    elif n == 117:
        probe = read_json(base / 'logger_probe_results.json')
        require(probe['compile_exit_code'] == 0 and digest(base / 'logger_probe_classes/LoggerSelectionProbe.class') == probe['class_sha256'], 'Shared logger probe bytecode differs')
        require([r['exit_code'] for r in probe['runs']] == [0, 0], 'Logger probe did not link/execute in both environments')
        require('factory=uk.org.lidalia.slf4jtest.TestLoggerFactory' in probe['runs'][0]['stdout'] and 'captured=1' in probe['runs'][0]['stdout'], 'PRE logging capture differs')
        require('factory=org.slf4j.helpers.NOPLoggerFactory' in probe['runs'][1]['stdout'] and 'captured=0' in probe['runs'][1]['stdout'], 'BREAKING logging behavior differs')
        for run in probe['runs']:
            require(run['image_id'] == read_json(base / run['phase'] / 'archive_summary.json')['image_id'], 'Logger probe image differs')
        captures = []
        for phase in ('pre', 'breaking'):
            jars = read_json(base / phase / 'jar_inspection.json')['artifacts']
            capture = next(j for j in jars if '/slf4j-test/' in j['resolved_path'])
            captures.append(capture)
            require(capture['classes']['org.slf4j.impl.StaticLoggerBinder']['present'] and 'META-INF/services/org.slf4j.spi.SLF4JServiceProvider' not in capture['services'], 'Legacy binding evidence differs')
        require(captures[0]['sha256'] == captures[1]['sha256'], 'Capture binding changed across original images')
    elif n == 118:
        sentry = []
        logging = []
        for phase in ('pre', 'breaking'):
            jars = read_json(base / phase / 'jar_inspection.json')['artifacts']
            sentry.append(next(j for j in jars if '/dropwizard-sentry/' in j['resolved_path']))
            logging.append(next(j for j in jars if '/dropwizard-logging/' in j['resolved_path']))
        require('META-INF/services/io.dropwizard.logging.AppenderFactory' in sentry[0]['services'], 'Old appender provider registration differs')
        require('META-INF/services/io.dropwizard.logging.common.AppenderFactory' in sentry[1]['services'] and 'META-INF/services/io.dropwizard.logging.AppenderFactory' not in sentry[1]['services'], 'New appender registration differs')
        require(logging[0]['sha256'] == logging[1]['sha256'] and logging[1]['classes']['io.dropwizard.logging.AppenderFactory']['present'], 'Retained logging runtime differs')
        signature = (base / 'breaking/dropwizard-sentry-4.0.1-3_SentryAppenderFactory_javap.txt').read_text()
        require('extends io.dropwizard.logging.common.AbstractAppenderFactory' in signature, 'New appender superclass differs')
    elif n == 119:
        classic = (base / 'breaking/logback-classic-1.4.6_DateConverter_javap.txt').read_text()
        core = (base / 'breaking/logback-core-1.4.5_CachingDateFormatter_javap.txt').read_text()
        require('CachingDateFormatter."<init>":(Ljava/lang/String;Ljava/time/ZoneId;Ljava/util/Locale;)V' in classic, 'Updated Classic constructor call differs')
        require('CachingDateFormatter(java.lang.String, java.time.ZoneId)' in core and 'CachingDateFormatter(java.lang.String, java.time.ZoneId, java.util.Locale)' not in core, 'Retained Core constructor signatures differ')
    elif n == 120:
        jars = read_json(base / 'breaking/jar_inspection.json')['artifacts']
        api = next(j for j in jars if '/log4j-api/2.17.2/' in j['resolved_path'])
        require(not api['classes']['org.apache.logging.log4j.util.ServiceLoaderUtil']['present'], 'Missing Log4j API class unexpectedly present')
        core = (base / 'breaking/log4j-core-2.19.0_ThreadContextDataInjector_javap.txt').read_text()
        require('org/apache/logging/log4j/util/ServiceLoaderUtil' in core, 'New Log4j Core type reference missing')
        case_id = read_json(base / 'breaking/archive_summary.json')['case_id']
        log = ROOT / 'logs/batch_triage' / (case_id[:8] + '_breaking.log')
        text = log.read_text(encoding='utf-8', errors='replace')
        require('NoClassDefFoundError: org/apache/logging/log4j/util/ServiceLoaderUtil' in text and 'ThreadContextDataInjector.getServiceProviders' in text, 'Primary missing-type failure not distinguished from cascading initialization errors')


def main():
    path = ROOT / 'results/behavioral_classification.csv'
    original = path.read_bytes()
    require(original.startswith((BACKUP / 'behavioral_classification.csv').read_bytes()), 'Original 115 records changed')
    rows = read_rows(path)
    candidates = read_rows(ROOT / 'results/test_failure_candidates.csv')
    require(len(rows) == 120 and len({r['case_id'] for r in rows}) == 120, 'Missing/duplicate case records')
    require(all(None not in r and all(v is not None for v in r.values()) for r in rows), 'Malformed CSV rows')
    require([r['case_id'] for r in rows] == [r['case_id'] for r in candidates[:120]], 'Candidate order differs')
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
        pom = 'maven-plugin/pom.xml' if n == 116 else 'pom.xml'
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
        checked[str(n)] = {'assessment': expected[2], 'binary_linkage_incompatibility': expected[3], 'pre_build_status': 'SUCCESS', 'breaking_build_status': 'FAILURE', 'test_discovery_aborted': n == 116, 'pre_counts': expected[0], 'breaking_counts': expected[1], 'original_images_run': 2, 'manifest_files_checked': len(manifest), 'append_idempotent': True}
    output = {'passed': True, 'classification_records': 120, 'counts_through_120': dict(Counter(r['behavioral_status'] for r in rows)), 'previous_115_records_byte_preserved': True, 'verified_repairs_and_case14_patch_byte_preserved': True, 'automated_triage_kept_separate': True, 'human_review_pending_for_new_cases': True, 'cases': checked}
    (ROOT / 'results/cases116_120_completion_check.json').write_text(json.dumps(output, indent=2), encoding='utf-8')
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
