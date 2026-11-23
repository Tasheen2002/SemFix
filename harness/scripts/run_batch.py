"""Run the repair harness over many cases. Resumable: cases whose result JSON exists are skipped.

  --source fixes   : the frozen fix of every case (fix_mining/fixes_v1.0/fix_index.csv), label 'frozen_fixes'
  --source <dir>   : patches named case<N>.patch in <dir> (e.g. a repair tool's output), label from --label
Writes harness/runs/<label>/summary.json and summary.csv after each case.
Usage: python -I run_batch.py <research root> --source fixes|<dir> [--label L] [--cases 1,2,3]
"""
import argparse, csv, json, os, re, subprocess, sys
from collections import Counter

ap = argparse.ArgumentParser()
ap.add_argument("root"); ap.add_argument("--source", required=True); ap.add_argument("--label"); ap.add_argument("--cases")
a = ap.parse_args()
P = lambda *x: os.path.join(a.root, *x)
index = {int(r["case_number"]): r for r in csv.DictReader(open(P("fix_mining", "fixes_v1.0", "fix_index.csv"), encoding="utf-8"))}
label = a.label or ("frozen_fixes" if a.source == "fixes" else os.path.basename(os.path.normpath(a.source)))
todo = [int(x) for x in a.cases.split(",")] if a.cases else sorted(index)
out = P("harness", "runs", label); os.makedirs(out, exist_ok=True)

for n in todo:
    if os.path.exists(os.path.join(out, f"case{n}.json")):
        continue
    patch = P("fix_mining", "fixes_v1.0", index[n]["patch"]) if a.source == "fixes" else os.path.join(a.source, f"case{n}.patch")
    if not os.path.exists(patch):
        print(f"case {n}: no patch at {patch}", flush=True); continue
    subprocess.run([sys.executable, "-I", P("harness", "scripts", "evaluate_patch.py"), a.root, "--case", str(n),
                    "--patch", patch, "--label", label])
    sys.stdout.flush()

# Re-run INCONCLUSIVE cases (network/infrastructure) once, after the main pass.
for n in todo:
    jf = os.path.join(out, f"case{n}.json")
    if os.path.exists(jf) and json.load(open(jf, encoding="utf-8"))["verdict"] == "INCONCLUSIVE":
        prev = json.load(open(jf, encoding="utf-8"))
        os.replace(jf, os.path.join(out, f"case{n}_inconclusive_attempt.json"))
        print(f"case {n}: re-running INCONCLUSIVE ({prev.get('inconclusive_reason', '')})", flush=True)
        patch = P("fix_mining", "fixes_v1.0", index[n]["patch"]) if a.source == "fixes" else os.path.join(a.source, f"case{n}.patch")
        subprocess.run([sys.executable, "-I", P("harness", "scripts", "evaluate_patch.py"), a.root, "--case", str(n), "--patch", patch, "--label", label])

rows = [json.load(open(os.path.join(out, f), encoding="utf-8")) for f in sorted(os.listdir(out)) if re.fullmatch(r"case\d+\.json", f)]
summ = dict(label=label, cases=len(rows), harness_versions=Counter(r.get("harness_version", "v1") for r in rows),
            verdicts=Counter(r["verdict"] for r in rows), flaky_cases=sorted(r["case"] for r in rows if r.get("flaky")),
            failed_checks=Counter(k for r in rows for k in r["failed_checks"]),
            by_reference_group={g: Counter(r["verdict"] for r in rows if r["reference_group"] == g) for g in sorted({r["reference_group"] for r in rows})})
json.dump(summ, open(os.path.join(out, "summary.json"), "w", encoding="utf-8"), indent=1)
with open(os.path.join(out, "summary.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["case", "verdict", "flaky", "failed_checks", "reference_group", "tests", "failures", "errors", "pre_tests", "regressions", "resolved_versions", "seconds"])
    for r in sorted(rows, key=lambda r: r["case"]):
        w.writerow([r["case"], r["verdict"], r.get("flaky", False), ";".join(r["failed_checks"]), r["reference_group"], r["build"]["tests"], r["build"]["failures"],
                    r["build"]["errors"], r["pre_baseline"]["tests"], r["regression_count"], ";".join(r["resolved_versions"]), r["seconds"]])
print(json.dumps(summ, indent=1))
