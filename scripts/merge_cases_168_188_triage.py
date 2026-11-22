"""Merge the original triage rows staged by the two tail runners."""
import csv
import io
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'

def rows(source):
    reader = csv.DictReader(source)
    data = list(reader)
    if not reader.fieldnames or any(None in row or None in row.values() for row in data):
        raise ValueError('Malformed triage CSV')
    return reader.fieldnames, data

def main():
    path = RESULTS / 'batch_triage_results.csv'
    original = path.read_bytes()
    fields, existing = rows(io.StringIO(original.decode('utf-8-sig'), newline=''))
    by_id = {row['case_id']: row for row in existing}
    assert len(by_id) == len(existing)
    with (RESULTS / 'test_failure_candidates.csv').open(encoding='utf-8-sig', newline='') as stream:
        _, candidates = rows(stream)
    for n in range(168, 189):
        group = '168_174' if n <= 174 else '175_188'
        source = RESULTS / f'archive/cases{group}_triage/case{n}.csv'
        with source.open(encoding='utf-8-sig', newline='') as stream:
            stage_fields, staged = rows(stream)
        assert set(stage_fields) == set(fields) and len(staged) == 1
        row = staged[0]
        assert row['case_id'] == candidates[n-1]['case_id'] and int(row['candidate_number']) == n
        stored = by_id.setdefault(row['case_id'], row)
        if stored != row:
            raise ValueError(f'Different triage rows for candidate {n}')
    if len(by_id) == len(existing):
        print('All tail rows already merged')
        return
    temp = path.with_suffix('.merge.tmp')
    with temp.open('x', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(by_id.values(), key=lambda r: int(r['candidate_number'])))
    if path.read_bytes() != original:
        temp.unlink()
        raise RuntimeError('Triage table changed during merge')
    os.replace(temp, path)
    print(f'Merged {len(by_id)-len(existing)} automated rows')

if __name__ == '__main__':
    main()
