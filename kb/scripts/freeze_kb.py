"""Freeze the knowledge base for the experiments (handbook Phase 4.3).

Writes kb/FROZEN.json with the SHA-256 of kb/entries.jsonl, the entry counts and the date. From then on:
  * build_kb.py refuses to overwrite entries.jsonl (a change must become a new KB version);
  * retrieve.load() / verify_frozen() check the fingerprint every time the KB is used, and the repair
    pipeline records it in every run, so each result can be traced to the exact KB it used.
Refuses to run if a freeze already exists.
Usage: python -I freeze_kb.py <research root> [--version kb-v1.0]
"""
import argparse, datetime, hashlib, json, os, sys
from collections import Counter

ap = argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--version", default="kb-v1.0")
a = ap.parse_args()
P = lambda *x: os.path.join(a.root, "kb", *x)
if os.path.exists(P("FROZEN.json")):
    sys.exit("kb/FROZEN.json already exists: the KB is frozen. A changed KB must be built as a new version.")
raw = open(P("entries.jsonl"), "rb").read()
entries = [json.loads(l) for l in raw.decode("utf-8").splitlines() if l.strip()]
cases = [e["case_number"] for e in entries]
assert len(cases) == len(set(cases)) == 56, "expected 56 unique cases"
frozen = dict(
    version=a.version, frozen_on=datetime.date.today().isoformat(),
    entries_file="kb/entries.jsonl", entries_sha256=hashlib.sha256(raw).hexdigest(), entries=len(entries),
    by_fix_author=dict(Counter(e["fix"]["author"] for e in entries)),
    built_from=["results/classification_v1.0", "fix_mining/fixes_v1.0", "bump/data/benchmark (BUMP @324d551)"],
    protocol="Protocol 2 (handbook 4.0): BUMP-internal entries; leakage controlled at query time by L1/L2/L3 exclusions",
    note="Do not edit kb/entries.jsonl. Rebuild as a new version (new FROZEN.json) and record the change.")
json.dump(frozen, open(P("FROZEN.json"), "w", encoding="utf-8", newline="\n"), indent=1)
print(json.dumps(frozen, indent=1))
