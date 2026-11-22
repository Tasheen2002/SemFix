"""Build the PRE test baseline for each of the 56 BEHAVIORAL cases from the original PRE logs (read-only).

For every Maven module of the PRE build: the module's aggregate surefire result and, per test class, its
tests/failures/errors/skipped. Surefire's console names individual methods only when they fail, so the
baseline is at test-class level (plus module aggregates, which cover TestNG `TestSuite` runs).
A test class (or TestNG module) counts as a PRE-passing unit when it ran >= 1 test with 0 failures and 0 errors.

Output: harness/baselines/pre_tests.json
Usage: python -I build_pre_baselines.py <research root>
"""
import csv, json, os, re, sys

MODULE =re.compile(r"^\[INFO\] Building (?!jar:|war:|tar:|zip:)([\w.\-]+) [\w.\-]+(?:\s+\[\d+/\d+\])?\s*$")
RUNNING = re.compile(r"Running ([\w.$]+)\s*$")
CLASS_RES = re.compile(r"Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+), Time elapsed: [^-<]*(?:<<<[^-]*)?(?:-\s*in ([\w.$]+))?")
AGG = re.compile(r"Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)\s*$")


def read(p):
    raw = open(p, "rb").read()
    t = raw.decode("utf-16", "replace") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8", "replace")
    return [re.sub(r"\x1b\[[0-9;]*m", "", l) for l in t.splitlines()]


def parse(lines):
    """{module: {"classes": {cls: [t,f,e,s]}, "aggregate": [t,f,e,s] or None}}"""
    mods, cur, running, last_agg_line = {}, "(root)", None, -10
    for i, l in enumerate(lines):
        m = MODULE.match(l)
        if m:
            cur = m.group(1); mods.setdefault(cur, {"classes": {}, "aggregate": None}); running = None; continue
        mods.setdefault(cur, {"classes": {}, "aggregate": None})
        m = RUNNING.search(l)
        if m and "Tests run" not in l:
            running = m.group(1); continue
        m = CLASS_RES.search(l)
        if m:
            name = m.group(5) or running
            if name:
                v = list(map(int, m.groups()[:4]))
                old = mods[cur]["classes"].get(name)
                mods[cur]["classes"][name] = v if not old else [a + b for a, b in zip(old, v)]   # reruns/forks add up
            continue
        m = AGG.search(l)
        if m and i - last_agg_line > 5:        # surefire prints the aggregate once per module (ignore the echo)
            v = list(map(int, m.groups()))
            a = mods[cur]["aggregate"]
            mods[cur]["aggregate"] = v if not a else [x + y for x, y in zip(a, v)]
            last_agg_line = i
    return {k: v for k, v in mods.items() if v["classes"] or v["aggregate"]}


def main():
    ROOT = sys.argv[1]
    P = lambda *a: os.path.join(ROOT, *a)
    cls ={r["case_id"]: r for r in csv.DictReader(open(P("results", "behavioral_classification.csv"), encoding="utf-8"))}
    cases = json.load(open(P("fix_mining", "cases.json"), encoding="utf-8"))
    out, report = {}, []
    for c in cases:
        row = cls[c["id"]]
        mods = parse(read(P(row["pre_log"])))
        total = [sum((m["aggregate"] or [sum(x[i] for x in m["classes"].values()) for i in range(4)])[i] for m in mods.values()) for i in range(4)]
        passing_units = sum(1 for m in mods.values() for v in m["classes"].values() if v[0] > 0 and v[1] == v[2] == 0)
        out[str(c["case"])] = dict(case_id=c["id"], pre_log=row["pre_log"], modules=mods, total=dict(zip(("tests", "failures", "errors", "skipped"), total)),
                                   passing_classes=passing_units)
        exp = row["pre_tests"]
        report.append((c["case"], total[0], exp, len(mods), passing_units, total[1] + total[2]))

    os.makedirs(P("harness", "baselines"), exist_ok=True)
    json.dump(out, open(P("harness", "baselines", "pre_tests.json"), "w", encoding="utf-8"), indent=1)
    mism = [r for r in report if str(r[1]) != str(r[2])]
    print(f"{len(out)} cases; PRE totals matching results/behavioral_classification.csv pre_tests: {len(report) - len(mism)}/{len(report)}")
    for r in mism:
        print(f"  case {r[0]}: extracted {r[1]} vs recorded {r[2]} (modules {r[3]}, passing classes {r[4]})")
    print("cases with PRE failures/errors:", [r[0] for r in report if r[5]] or "none")
    print("total PRE-passing test classes:", sum(r[4] for r in report))


if __name__ == "__main__":   # importing this module (the harness does) must not rebuild the baseline
    main()
