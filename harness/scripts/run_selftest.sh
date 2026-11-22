#!/bin/sh
# Run the harness self-test: 4 patches with known expected verdicts (harness/selftest/expected.json).
ROOT="$1"
cd "$ROOT" || exit 1
python -I - "$ROOT" <<'PY'
import json, subprocess, sys
root = sys.argv[1]
ok = True
for t in json.load(open("harness/selftest/expected.json", encoding="utf-8")):
    name = t["patch"].rsplit("/", 1)[-1].replace(".patch", "")
    label = "selftest_v2_" + name
    subprocess.run([sys.executable, "-I", "harness/scripts/evaluate_patch.py", root, "--case", str(t["case"]), "--patch", t["patch"], "--label", label])
    r = json.load(open(f"harness/runs/{label}/case{t['case']}.json", encoding="utf-8"))
    good = r["verdict"] == t["expected_verdict"] and set(t["expected_failed_checks"]) <= set(r["failed_checks"])
    ok &= good
    print(f"SELFTEST {'PASS' if good else 'FAIL'}: {name}: expected {t['expected_verdict']} {t['expected_failed_checks']}, got {r['verdict']} {r['failed_checks']}", flush=True)
print("SELFTEST OVERALL:", "PASS" if ok else "FAIL")
PY
