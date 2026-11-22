"""Supplement the original archives with Maven POMs at every module depth."""
import csv
import difflib
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    candidates = list(csv.DictReader((ROOT / 'results/test_failure_candidates.csv').open(encoding='utf-8-sig', newline='')))
    for n in range(161, 166):
        snapshots = []
        base = ROOT / f'logs/case{n}_evidence'
        for phase in ('pre', 'breaking'):
            meta = json.loads((base / phase / 'archive_summary.json').read_text())
            container = 'bump-' + candidates[n-1]['case_id'] + '-' + phase
            info = json.loads(subprocess.check_output(['docker', 'inspect', container], text=True))[0]
            if info['State']['Status'] != 'exited':
                raise ValueError('Container unfinished')
            sources = {}
            process = subprocess.Popen(['docker', 'cp', container + ':' + meta['working_directory'] + '/.', '-'], stdout=subprocess.PIPE)
            with (base / phase / 'all_poms.tar').open('xb') as output:
                try:
                    with tarfile.open(fileobj=process.stdout, mode='r|') as incoming, tarfile.open(fileobj=output, mode='w') as outgoing:
                        for member in incoming:
                            path = PurePosixPath(member.name)
                            if not member.isfile() or path.is_absolute() or '..' in path.parts or path.name != 'pom.xml' or any(p in path.parts for p in ('target', '.git', 'node_modules')):
                                continue
                            data = incoming.extractfile(member).read()
                            sources[path.as_posix()] = data
                            outgoing.addfile(member, io.BytesIO(data))
                    if process.wait() != 0:
                        raise RuntimeError('POM stream failed')
                finally:
                    process.stdout.close()
                    if process.poll() is None:
                        process.kill()
                        process.wait()
            hashes = {p: hashlib.sha256(data).hexdigest() for p, data in sorted(sources.items())}
            with (base / phase / 'all_poms_sha256.json').open('x', encoding='utf-8') as output:
                json.dump(hashes, output, indent=2)
            snapshots.append(sources)
        before, after = snapshots
        if before.keys() != after.keys():
            raise ValueError('POM paths differ; inspect before classification')
        changes = [p for p in sorted(before) if before[p] != after[p]]
        result = {'case_number': n, 'pom_count_per_phase': len(before), 'changed_poms': changes, 'diffs': {p: '\n'.join(difflib.unified_diff(before[p].decode().splitlines(), after[p].decode().splitlines(), fromfile='pre/' + p, tofile='breaking/' + p)) for p in changes}}
        with (base / 'all_poms_comparison.json').open('x', encoding='utf-8') as output:
            json.dump(result, output, indent=2)
        print(json.dumps(result), flush=True)

if __name__ == '__main__':
    main()
