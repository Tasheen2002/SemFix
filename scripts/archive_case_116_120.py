"""Archive source and fresh reports from a retained, stopped BUMP container.

Reads Docker's tar stream without extracting it. Reports are accepted only from
modules whose target directory the current Maven log explicitly deleted.
"""

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case-number', required=True, type=int)
    parser.add_argument('--phase', required=True, choices=('pre', 'breaking'))
    args = parser.parse_args()
    base = Path(__file__).resolve().parents[1]
    with (base / 'results/test_failure_candidates.csv').open(encoding='utf-8-sig', newline='') as f:
        candidates = list(csv.DictReader(f))
    if not 1 <= args.case_number <= len(candidates):
        raise ValueError('Candidate number outside dataset')
    case_id = candidates[args.case_number - 1]['case_id']
    name = f'bump-{case_id}-{args.phase}'
    info = json.loads(subprocess.check_output(['docker', 'inspect', name], text=True))[0]
    if info['State']['Running']:
        raise ValueError('Wait for the container to stop before archiving final evidence')
    workdir = info['Config']['WorkingDir'].rstrip('/')
    log_path = base / f'logs/batch_triage/{case_id[:8]}_{args.phase}.log'
    log = log_path.read_text(encoding='utf-8', errors='replace')
    clean_modules = set()
    for match in re.finditer(r'Deleting ' + re.escape(workdir) + r'(/[^\r\n]*)?/target\s*$', log, re.M):
        clean_modules.add((match.group(1) or '').strip('/') or '.')
    destination = base / f'logs/case{args.case_number}_evidence/{args.phase}'
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / 'artifacts.tar'
    report_rows = []
    sources = {}
    image = json.loads(subprocess.check_output(['docker', 'image', 'inspect', info['Image']], text=True))[0]
    metadata = {
        'case_id': case_id, 'phase': args.phase, 'container_state': info['State'],
        'working_directory': workdir, 'command': info['Config']['Cmd'],
        'image_id': info['Image'], 'image_digests': image.get('RepoDigests', []),
        'platform': image['Os'] + '/' + image['Architecture'],
        'cleaned_modules': sorted(clean_modules),
        'freshness_rule': 'Only report directories under a target explicitly deleted in this run are included',
    }
    # Stream all root contents, retaining only sources, POMs, and fresh reports.
    # No paths from the stream are extracted to the local filesystem.
    with archive.open('xb') as stream:
        process = subprocess.Popen(['docker', 'cp', name + ':' + workdir + '/.', '-'], stdout=subprocess.PIPE)
        try:
            with tarfile.open(fileobj=process.stdout, mode='r|') as incoming, tarfile.open(fileobj=stream, mode='w') as outgoing:
                for member in incoming:
                    if not member.isfile():
                        continue
                    relative = PurePosixPath(member.name)
                    if relative.is_absolute() or '..' in relative.parts:
                        continue
                    # docker cp WORKDIR/. emits paths relative to WORKDIR.
                    # A first component matching the checkout name can be a
                    # real module and must be preserved.
                    parts = relative.parts
                    if not parts:
                        continue
                    is_source = 'src' in parts and 'target' not in parts and 'node_modules' not in parts
                    is_pom = parts[-1] == 'pom.xml' and len(parts) <= 2
                    is_report = False
                    if 'target' in parts:
                        target_index = parts.index('target')
                        module = '/'.join(parts[:target_index]) or '.'
                        is_report = (module in clean_modules and parts[target_index + 1:target_index + 2] == ('surefire-reports',))
                    if not (is_source or is_pom or is_report):
                        continue
                    member.name = relative.as_posix()
                    if 'path' in member.pax_headers:
                        member.pax_headers['path'] = member.name
                    content = incoming.extractfile(member)
                    if is_report and parts[-1].startswith('TEST-') and parts[-1].endswith('.xml'):
                        data = content.read()
                        root = ET.fromstring(data)
                        props = {p.get('name'): p.get('value') for p in root.findall('properties/property')}
                        report_rows.append({
                            'path': member.name, 'module': module, 'test_class': root.get('name'),
                            'counts': {key: int(root.get(key, 0)) for key in ('tests', 'failures', 'errors', 'skipped')},
                            'java_version': props.get('java.version'),
                            'classpath': props.get('surefire.test.class.path') or props.get('java.class.path', ''),
                            'classpath_property': 'surefire.test.class.path' if props.get('surefire.test.class.path') else 'java.class.path',
                            'errors': [{'test_name': t.get('name'), 'type': e.get('type'),
                                        'message': e.get('message'), 'stacktrace': e.text}
                                       for t in root.findall('testcase') for e in t.findall('error')],
                            'failures': [{'test_name': t.get('name'), 'type': e.get('type'),
                                          'message': e.get('message'), 'stacktrace': e.text}
                                         for t in root.findall('testcase') for e in t.findall('failure')],
                        })
                        outgoing.addfile(member, io.BytesIO(data))
                    elif is_source or is_pom:
                        data = content.read()
                        sources[member.name] = hashlib.sha256(data).hexdigest()
                        outgoing.addfile(member, io.BytesIO(data))
                    else:
                        outgoing.addfile(member, content)
            if process.wait() != 0:
                raise RuntimeError('Docker evidence stream failed; retained archive may be incomplete')
        finally:
            process.stdout.close()
            if process.poll() is None:
                process.kill()
                process.wait()
    metadata['report_count'] = len(report_rows)
    metadata['reports'] = report_rows
    metadata['source_and_pom_sha256'] = sources
    metadata['aggregate_counts'] = {key: sum(r['counts'][key] for r in report_rows)
                                    for key in ('tests', 'failures', 'errors', 'skipped')}
    with (destination / 'archive_summary.json').open('x', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    print(json.dumps({key: metadata[key] for key in ('phase', 'cleaned_modules', 'report_count', 'aggregate_counts')}))


if __name__ == '__main__':
    main()
