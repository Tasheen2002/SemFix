"""Re-judge saved harness logs with the CURRENT rules of evaluate_patch.py, without Docker.

Use after changing a rule, to see how existing runs would be judged now. Nothing is written to the run folder;
the result is printed (and optionally saved with --out).
Usage: python -I reevaluate_logs.py <research root> --label <run label> [--out file.json]
"""
import argparse, json, os, re, sys
from collections import Counter

ap = argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--label", required=True); ap.add_argument("--out")
a = ap.parse_args()
src_path = os.path.join(a.root, "harness", "scripts", "evaluate_patch.py")
src = open(src_path, encoding="utf-8").read()
head = src[:src.index("attempts = []")]               # definitions only; stops before any container is run
head = head.replace('if not had:\n    docker("pull", "-q", img)', "")  # never pull images during a re-check
run = os.path.join(a.root, "harness", "runs", a.label)
results = {}
for f in sorted(os.listdir(run)):
    m = re.fullmatch(r"case(\d+)\.log", f)
    if not m:
        continue
    n = int(m.group(1))
    g = {"__name__": "reevaluate"}
    sys.argv = ["evaluate_patch.py", a.root, "--case", str(n), "--patch", os.devnull, "--label", "_reevaluate_tmp"]
    exec(compile(head, src_path, "exec"), g)
    # Judge the LAST attempt, as the harness does (attempt 1 may be a flaky failure that attempt 2 resolved).
    later = sorted((int(m2.group(1)), x) for x in os.listdir(run) for m2 in [re.fullmatch(rf"case{n}_attempt(\d+)\.log", x)] if m2)
    ev = g["evaluate"](os.path.join(run, later[-1][1] if later else f))
    old = json.load(open(os.path.join(run, f"case{n}.json"), encoding="utf-8")) if os.path.exists(os.path.join(run, f"case{n}.json")) else {}
    results[n] = dict(old_verdict=old.get("verdict"), new_verdict=g["verdict_of"](ev), network=ev["network"][:2],
                      failed=[k for k, v in ev["checks"].items() if v is False])
tmp = os.path.join(a.root, "harness", "runs", "_reevaluate_tmp")
if os.path.isdir(tmp) and not os.listdir(tmp):
    os.rmdir(tmp)
print("new verdicts:", dict(Counter(r["new_verdict"] for r in results.values())))
changed = {n: r for n, r in results.items() if r["old_verdict"] != r["new_verdict"]}
print(f"changed: {len(changed)}")
for n, r in sorted(changed.items()):
    print(f"  case {n}: {r['old_verdict']} -> {r['new_verdict']}  {r['network'][:1]}")
if a.out:
    json.dump(results, open(a.out, "w", encoding="utf-8"), indent=1)
