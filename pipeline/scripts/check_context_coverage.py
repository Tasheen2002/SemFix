"""Context coverage: can the LLM see what the validated fix changes?

For each prompt in a dry run, checks against the case's frozen fix:
  files_shown : every existing file the fix edits appears in the prompt (new files need no context)
  lines_shown : every line the fix removes appears verbatim in the prompt
A case "covered" by both can, in principle, be repaired from the prompt alone. This measures the context
selection only (it does not use the fix to build prompts). Report it with the experiments.
Usage: python -I check_context_coverage.py <root> --label <dry-run label>
"""
import argparse, csv, json, os, re
from collections import Counter

ap = argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--label", required=True)
a = ap.parse_args()
P = lambda *x: os.path.join(a.root, *x)
d = P("pipeline", "runs", a.label)
idx = {int(r["case_number"]): r for r in csv.DictReader(open(P("fix_mining", "fixes_v1.0", "fix_index.csv"), encoding="utf-8"))}
rows = []
for f in sorted(os.listdir(d)):
    m = re.fullmatch(r"case(\d+)\.json", f)
    if not m:
        continue
    n = int(m.group(1))
    prompt = open(os.path.join(d, "prompts", f"case{n}_attempt1.md"), encoding="utf-8").read()
    patch = open(P("fix_mining", "fixes_v1.0", idx[n]["patch"]), encoding="utf-8", errors="replace").read()
    new_files = set(re.findall(r"^diff --git a/(\S+) b/\S+\nnew file mode", patch, re.M))
    files = set(re.findall(r"^diff --git a/(\S+) b/", patch, re.M)) - new_files
    removed = [l[1:].strip() for l in patch.splitlines() if l.startswith("-") and not l.startswith("---") and l[1:].strip()]
    files_missing = sorted(x for x in files if f"### {x} " not in prompt)
    lines_missing = [l for l in removed if l not in prompt]
    status = "COVERED" if not files_missing and not lines_missing else ("PARTIAL" if len(files_missing) < len(files) else "NOT_COVERED")
    rows.append(dict(case=n, status=status, reference_group=idx[n]["reference_group"], files=len(files), new_files=len(new_files),
                     files_missing=files_missing[:5], removed_lines=len(removed), lines_missing=len(lines_missing),
                     example_missing_line=lines_missing[0][:160] if lines_missing else ""))
out = P("pipeline", "runs", a.label, "context_coverage.json")
json.dump(rows, open(out, "w", encoding="utf-8"), indent=1)
c = Counter(r["status"] for r in rows)
print(f"context coverage ({a.label}): " + ", ".join(f"{k} {v}" for k, v in c.most_common()) + f" of {len(rows)}")
for r in rows:
    if r["status"] != "COVERED":
        print(f"  case {r['case']}: {r['status']}  missing files {r['files_missing']}  missing lines {r['lines_missing']}/{r['removed_lines']}  {r['example_missing_line'][:90]}")
