"""Supplement the original archives with Maven POMs at every module depth."""
import argparse
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cases", nargs="*", type=int, choices=range(166, 189))
    for n in parser.parse_args().cases or range(166, 189):
        snapshots = []
        base = ROOT / f'logs/case{n}_evidence'
        if (base / 'all_poms_comparison.json').exists():
            continue
        for phase in ('pre', 'breaking'):
            meta = json.loads((base / phase / 'archive_summary.json').read_text())
            container = 'bump-' + candidates[n-1]['case_id'] + '-' + phase
            info = json.loads(subprocess.check_output(['docker', 'inspect', container], text=True))[0]
            if info['State']['Status'] != 'exited':
                raise ValueError('Container unfinished')
            tar_path = base / phase / 'all_poms.tar'
            hashes_path = base / phase / 'all_poms_sha256.json'
            if tar_path.exists() and hashes_path.exists():
                with tarfile.open(tar_path) as archive:
                    recovered = {PurePosixPath(m.name).as_posix(): archive.extractfile(m).read() for m in archive if m.isfile()}
                hashes = {p: hashlib.sha256(data).hexdigest() for p, data in recovered.items()}
                if hashes != json.loads(hashes_path.read_text()):
                    raise ValueError(f'Existing archived POM hashes differ in case {n} {phase}')
                snapshots.append(recovered)
                continue
            if tar_path.exists() or hashes_path.exists():
                from datetime import datetime
                suffix = '.interrupted-' + datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                for partial in (tar_path, hashes_path):
                    if partial.exists():
                        partial.rename(partial.with_name(partial.name + suffix))
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
