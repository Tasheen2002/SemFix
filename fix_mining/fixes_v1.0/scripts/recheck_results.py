"""Re-check every recorded validation result against the stricter rule (added 2026-11-21 after Case 171
showed BUILD SUCCESS with 0 tests): a fix counts only if tests ran and every originally failing test class
ran in the fixed build. Reads the saved logs; does not rerun Docker. Prints any record that no longer holds.
Usage: python -I recheck_results.py <research root>
"""
import json, os, re, sys
ROOT = sys.argv[1]
bad = 0
for group in ("validation", "researcher_written"):
    p = os.path.join(ROOT, "fix_mining", group, "results.jsonl")
    for l in open(p, encoding="utf-8"):
        r = json.loads(l)
        if r["verdict"] != "FIX_VALIDATED":
            continue
        lines = open(os.path.join(ROOT, r["log"]), encoding="utf-8", errors="replace").read().splitlines()
        b = next((i for i, x in enumerate(lines) if "=== BUILD ===" in x), 0)
        e = next((i for i, x in enumerate(lines) if "=== DEPENDENCY TREE ===" in x), len(lines))
        ran = {m.group(1) for x in lines[b:e] for m in [re.search(r"Running ([\w.$]+)\s*$", re.sub(r"\x1b\[[0-9;]*m", "", x))] if m}
        targets = [t for t in r["target_classes"] if t != "TestSuite"]
        not_run = [t for t in targets if not any(t == x or x.endswith("." + t) or t.endswith("." + x) for x in ran)]
        ok = r["fixed"]["tests"] > 0 and not not_run
        if not ok:
            bad += 1
        print(f"{group:18s} case {r['case']:>3}  tests={r['fixed']['tests']:>5}  targets_ran={len(targets) - len(not_run)}/{len(targets)}"
              + ("" if ok else f"  <-- FAILS STRICT RULE: not run {not_run}"))
print("records failing the strict rule:", bad)
