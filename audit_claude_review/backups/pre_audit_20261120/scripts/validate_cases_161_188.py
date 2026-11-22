"""Validate Cases 161-188 without changing earlier records or evidence."""
from collections import Counter
import argparse
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
BACKUP = ROOT / 'results/backups/before_cases161_188'
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--through', type=int, choices=range(161, 189), default=188)
    end = parser.parse_args().through
    path = ROOT / 'results/behavioral_classification.csv'
    original = path.read_bytes()
    backup_path = BACKUP / 'behavioral_classification.csv'
    backup_bytes = backup_path.read_bytes()
    exact_prefix = original.startswith(backup_bytes)
    rows = read_rows(path)
    previous_rows = read_rows(backup_path)
    require(len(previous_rows) == 160 and rows[:160] == previous_rows, 'Original 160 CSV records changed')
    if not exact_prefix:
        without_blank_lines = lambda data: [line for line in data.splitlines(keepends=True) if line.strip()]
        expected = without_blank_lines(backup_bytes)
        require(without_blank_lines(original)[:len(expected)] == expected, 'Original CSV differs beyond blank lines')
    candidates = read_rows(ROOT / 'results/test_failure_candidates.csv')
    require(len(rows) == end and len({r['case_id'] for r in rows}) == end, 'Missing/duplicate case records')
    require(all(None not in r and all(v is not None for v in r.values()) for r in rows), 'Malformed CSV rows')
    require([r['case_id'] for r in rows] == [r['case_id'] for r in candidates[:end]], 'Candidate order differs')
    for relative, backup in [('results/verified_repairs.jsonl', 'verified_repairs.jsonl'), ('repairs/case14_h2_clob.patch', 'case14_h2_clob.patch')]:
        require((ROOT / relative).read_bytes() == (BACKUP / backup).read_bytes(), 'Existing repair evidence changed')
    require(len((ROOT / 'results/verified_repairs.jsonl').read_text().splitlines()) == 1, 'Unexpected verified repair count')
    triage = read_rows(ROOT / 'results/batch_triage_results.csv')
    previous = read_rows(BACKUP / 'batch_triage_results.csv')
    require(all(r in triage for r in previous) and len({r['case_id'] for r in triage}) == len(triage), 'Previous/new automated triage records differ')
    checked = {}
    for n in range(161, end + 1):
        row, candidate = rows[n-1], candidates[n-1]
        require(row['behavioral_status'] in {'NON_BEHAVIORAL', 'PROVISIONAL_BEHAVIORAL'}, 'Assessment label differs')
        phase_counts = []
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
            if (base / phase / 'reconciled_counts.json').exists():
                reconciler = runpy.run_path(str(ROOT / 'scripts/reconcile_cases_161_188_reports.py'))['reconcile']
                reconciled = read_json(base / phase / 'reconciled_counts.json')
                require(reconciled == reconciler(base / phase), 'TestNG reconciliation differs')
                totals = reconciled['aggregate_counts']
            counts = tuple(totals[k] for k in ('tests', 'failures', 'errors', 'skipped'))
            summaries = re.findall(r'^(?:\[[A-Z]+\] )?Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)[ \t]*$', log, re.M)
            calculated = tuple(map(sum, zip(*(map(int, s) for s in summaries)))) if summaries else (0, 0, 0, 0)
            if n == 167:
                randomized = read_json(base / phase / 'randomized_summary.json')
                require(randomized['case_id'] == row['case_id'] and randomized['phase'] == phase, 'Randomized runner identity mismatch')
                matches = re.findall(r'^\[INFO\] Tests summary: \d+ suites?, (\d+) tests?([^\r\n]*)', log, re.M)
                require(bool(matches), 'Missing randomized runner summaries')
                calculated = (sum(int(m[0]) for m in matches), *(sum(int(x) for m in matches for x in re.findall(r'(\d+) '+term,m[1])) for term in ('failure','error','ignored')))
                totals = randomized['aggregate_counts']
                counts = tuple(totals[k] for k in ('tests','failures','errors','ignored'))
            require(calculated == counts, f'Case {n} Maven/XML counts differ: {calculated} != {counts}')
            phase_counts.append(counts)
            if (base / phase / 'jar_inspection.json').exists():
                inspection = read_json(base / phase / 'jar_inspection.json')
                require(inspection['case_id'] == row['case_id'] and inspection['phase'] == phase, 'JAR inspection identity differs')
                for jar in inspection['artifacts']:
                    require(digest(base / phase / 'jars' / Path(jar['resolved_path']).name) == jar['sha256'], 'JAR content differs from inspection')
        before, after = [s['source_and_pom_sha256'] for s in snapshots]
        changes = sorted(set(before) ^ set(after) | {k for k in before.keys() & after.keys() if before[k] != after[k]})
        poms = [read_json(base / phase / 'all_poms_sha256.json') for phase in ('pre', 'breaking')]
        changed_poms = sorted(k for k in poms[0].keys() | poms[1].keys() if poms[0].get(k) != poms[1].get(k))
        comparison = read_json(base / 'all_poms_comparison.json')
        require(comparison['changed_poms'] == changed_poms, 'POM comparison differs')
        require([int(row[k]) for k in ('pre_tests', 'breaking_tests', 'breaking_failures', 'breaking_errors')] == [phase_counts[0][0], *phase_counts[1][:3]], 'CSV test counts differ')
        require(row['main_exception'] in (ROOT / row['breaking_log']).read_text(errors='replace'), f'Case {n} main exception absent from original failure log')
        result = subprocess.run([sys.executable, str(ROOT / f'scripts/append_case_{n}.py')], cwd=ROOT, capture_output=True, text=True)
        require(result.returncode == 0 and path.read_bytes() == original, 'Append idempotency check failed: ' + result.stderr)
        checked[str(n)] = {'assessment': row['behavioral_status'], 'binary_linkage_incompatibility': row['binary_linkage_incompatibility'], 'pre_build_status': 'SUCCESS', 'breaking_build_status': 'FAILURE', 'pre_counts': phase_counts[0], 'breaking_counts': phase_counts[1], 'original_images_run': 2, 'changed_archived_files': changes, 'changed_poms': changed_poms, 'manifest_files_checked': len(manifest), 'append_idempotent': True}
    output = {'passed': True, 'classification_records': end, 'classification_counts': dict(Counter(r['behavioral_status'] for r in rows)), 'previous_160_records_values_preserved': True, 'original_csv_byte_prefix_unchanged': exact_prefix, 'verified_repairs_and_case14_patch_byte_preserved': True, 'automated_triage_kept_separate': True, 'human_review_pending_for_new_cases': True, 'cases': checked}
    (ROOT / f'results/cases161_{end}_completion_check.json').write_text(json.dumps(output, indent=2), encoding='utf-8')
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
