"""Compare manual_verification reruns of the 47 sample cases with the original BUMP runs.
Adds ai_rerun_* columns to verification_plan/human_sample.csv (human_* columns untouched) and writes
manual_verification/rerun_report.md and rerun_comparison.json.
"""
import csv, json, os, re, sys, datetime
ROOT = sys.argv[1]
A = lambda *a: os.path.join(ROOT, "audit_claude_review", *a)
AGG = re.compile(r"Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)\s*$")
RND = re.compile(r"Tests summary: \d+ suites?(?: \(\d+ ignored\))?, (\d+) tests?(?:, (\d+) failures?)?(?:, (\d+) errors?)?(?:, (\d+) ignored)?")
LINK = re.compile(r"NoClassDefFoundError|NoSuchMethodError|NoSuchFieldError|AbstractMethodError|IncompatibleClassChangeError|UnsupportedClassVersionError|VerifyError|IllegalAccessError|ClassNotFoundException|API incompatibility")
EXC = re.compile(r"\b((?:[a-z_][\w$]*\.)+[A-Z][\w$]*(?:Exception|Error|Failure))\b")


def read(path):
    raw = open(path, "rb").read()
    t = raw.decode("utf-16", "replace") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8-sig", "replace")
    return [re.sub(r"\x1b\[[0-9;]*m", "", l) for l in t.splitlines()]


def summarize(lines):
    agg, prev = [], None
    for i, l in enumerate(lines):
        m = AGG.search(l)
        if m and "Time elapsed" not in l:
            v = tuple(map(int, m.groups()))
            if prev and v == prev[1] and i - prev[0] < 6: continue
            agg.append(v); prev = (i, v)
    rnd = [tuple(int(x) if x else 0 for x in m.groups()) for l in lines for m in [RND.search(l)] if m]
    tot = [sum(x[i] for x in agg) + sum(x[i] for x in rnd) for i in range(3)]
    status = ([m.group(1) for l in lines for m in [re.search(r"BUILD (SUCCESS|FAILURE)", l)] if m] or ["NONE"])[-1]
    mex = ([m.group(1) for l in lines for m in [re.search(r"MAVEN_EXIT=(\d+)", l)] if m] or [""])[-1]
    link = sorted({m.group(0) for l in lines for m in [LINK.search(l)] if m})
    fail_exc = []
    for i, l in enumerate(lines):
        if re.search(r"<<< (FAILURE|ERROR)!", l) and "Tests run" not in l:
            for nxt in lines[i + 1:i + 4]:
                m = EXC.search(nxt)
                if m: fail_exc.append(m.group(1)); break
    causes = [EXC.search(l).group(1) for l in lines if l.strip().startswith("Caused by:") and EXC.search(l)]
    return dict(status=status, maven_exit=mex, tests=tot[0], failures=tot[1], errors=tot[2], link=link,
                fail_exc=sorted(set(fail_exc)), causes=sorted(set(causes)))


cands = [r["case_id"] for r in csv.DictReader(open(os.path.join(ROOT, "results", "test_failure_candidates.csv"), encoding="utf-8"))]
cls = {r["case_id"]: r for r in csv.DictReader(open(os.path.join(ROOT, "results", "behavioral_classification.csv"), encoding="utf-8"))}
final = {r["case_number"]: r for r in csv.DictReader(open(os.path.join(ROOT, "results", "final_classification_rule_based.csv"), encoding="utf-8"))}
sp = A("verification_plan", "human_sample.csv")
sample = list(csv.DictReader(open(sp, encoding="utf-8")))
today = datetime.date.today().isoformat()
res = []
for s in sample:
    n = s["case_number"]; cid = cands[int(n) - 1]
    rl = A("manual_verification", "logs", f"case{n}_breaking.log")
    if not os.path.exists(rl):
        res.append(dict(case=n, verdict="NOT_RUN", notes="no rerun log")); continue
    o = summarize(read(os.path.join(ROOT, cls[cid]["breaking_log"])))
    r = summarize(read(rl))
    issues = []
    if r["status"] != o["status"]: issues.append(f"build {o['status']} -> {r['status']}")
    if (r["tests"], r["failures"], r["errors"]) != (o["tests"], o["failures"], o["errors"]):
        issues.append(f"counts t/f/e {o['tests']}/{o['failures']}/{o['errors']} -> {r['tests']}/{r['failures']}/{r['errors']}")
    if set(o["link"]) != set(r["link"]): issues.append(f"linkage signals {o['link']} -> {r['link']}")
    sig_o = set(o["fail_exc"]) | set(o["causes"]); sig_r = set(r["fail_exc"]) | set(r["causes"])
    if sig_o and not (sig_o & sig_r): issues.append(f"no shared exception types (orig {sorted(sig_o)[:4]} / rerun {sorted(sig_r)[:4]})")
    if r["status"] == "NONE": issues.append("rerun log has no BUILD line (run interrupted or image problem)")
    same_core = r["status"] == o["status"] and (not sig_o or sig_o & sig_r) and set(o["link"]) == set(r["link"])
    verdict = "REPRODUCED" if not issues else ("REPRODUCED_WITH_COUNT_DIFFERENCE" if same_core else "MISMATCH")
    res.append(dict(case=n, verdict=verdict, orig=o, rerun=r, issues=issues,
                    proposed=final[n]["rule_based_label"], rule=final[n]["rule"]))
json.dump(res, open(A("manual_verification", "rerun_comparison.json"), "w", encoding="utf-8"), indent=1)

by = {x["case"]: x for x in res}
for s in sample:
    x = by[s["case_number"]]
    s["ai_rerun_verified"] = x["verdict"]
    s["ai_rerun_notes"] = ("; ".join(x.get("issues", [])) or "Rerun matches the original BREAKING run (build result, counts, linkage signals, exception types).") if x["verdict"] != "NOT_RUN" else x["notes"]
    s["ai_rerun_maven_exit"] = x.get("rerun", {}).get("maven_exit", "")
    s["ai_rerun_date"] = today if x["verdict"] != "NOT_RUN" else ""
    s["ai_rerun_source"] = "AI verification (Claude), not a human review"
cols = list(sample[0].keys())
with open(sp, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(sample)

from collections import Counter
cnt = Counter(x["verdict"] for x in res)
L = ["# Rerun verification of the 47 sample cases", "",
     f"**Run:** manual_verification/verify_case.ps1 against the original BREAKING images. Fresh `--rm` containers, Maven exit code captured directly. **Compared with:** the original BUMP BREAKING logs. **Date:** {today}. **Source:** AI verification (Claude), not a human review.", "",
     "| Verdict | Cases |", "|---|---:|"] + [f"| {k} | {v} |" for k, v in cnt.most_common()] + ["",
     "- **REPRODUCED:** same build result, test counts, linkage signals and exception types.",
     "- **REPRODUCED_WITH_COUNT_DIFFERENCE:** same failure mechanism, but the counts differ (for example a flaky or time-dependent test).",
     "- **MISMATCH:** the mechanism differs; the case needs a human look before its label is accepted.", "",
     "## Cases needing attention", ""]
att = [x for x in res if x["verdict"] != "REPRODUCED"]
if not att: L.append("None.")
for x in att:
    L.append(f"- **Case {x['case']}** ({x.get('proposed','')}, {x.get('rule','')}): {x['verdict']}. " + ("; ".join(x.get("issues", [])) or x.get("notes", "")))
L += ["", "## All cases", "", "| Case | Proposed | Rule | Verdict | Rerun build / exit | Rerun t/f/e |", "|---|---|---|---|---|---|"]
for x in res:
    r = x.get("rerun")
    L.append(f"| {x['case']} | {x.get('proposed','')} | {x.get('rule','')} | {x['verdict']} | " + (f"{r['status']} / {r['maven_exit']} | {r['tests']}/{r['failures']}/{r['errors']}" if r else "– | –") + " |")
open(A("manual_verification", "rerun_report.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print(cnt)
