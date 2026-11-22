"""Extract failing test classes/methods for each BEHAVIORAL case from the original BREAKING logs (read-only).
Output: fix_mining/failing_tests.json  {case: {"classes": [...], "methods": [...]}}"""
import csv, json, os, re, sys
ROOT = sys.argv[1]
F = lambda *a: os.path.join(ROOT, *a)
cls = {r["case_id"]: r for r in csv.DictReader(open(F("results", "behavioral_classification.csv"), encoding="utf-8"))}
cases = json.load(open(F("fix_mining", "cases.json"), encoding="utf-8"))
def read(p):
    raw = open(p, "rb").read()
    t = raw.decode("utf-16", "replace") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8", "replace")
    return [re.sub(r"\x1b\[[0-9;]*m", "", l) for l in t.splitlines()]
out = {}
for c in cases:
    lines = read(F(cls[c["id"]]["breaking_log"]))
    classes, methods = set(), set()
    for l in lines:
        m = re.search(r"Tests run: \d+, Failures: (\d+), Errors: (\d+).*?<<< (?:FAILURE|ERROR)!? *-? *(?:in )?([\w.$]+)", l)
        if m: classes.add(m.group(3))
        m = re.search(r"^\[ERROR\]\s+([\w.$]+)\.([\w$\[\]]+)(?::\d+)?\s", l) or re.search(r"^\[ERROR\]\s+([\w$]+)\.(\w+):\d+", l)
        if m and not m.group(1).startswith(("Tests", "Failed", "Run", "Errors", "Failures")): methods.add(f"{m.group(1)}#{m.group(2)}")
        m = re.search(r"^([\w$]+)\(([\w.$]+)\)\s+Time elapsed", l)  # JUnit4 style lines
        m2 = re.search(r"^\[?(?:ERROR)?\]?\s*([\w$]+)\(([\w.$]+)\)\s+Time elapsed.*<<< (FAILURE|ERROR)", l)
        if m2: methods.add(f"{m2.group(2)}#{m2.group(1)}"); classes.add(m2.group(2))
        m3 = re.search(r"^\[ERROR\]\s+([\w$]+)\s+Time elapsed.*<<< (?:FAILURE|ERROR)", l)
    out[str(c["case"])] = dict(classes=sorted(classes), methods=sorted(methods)[:40])
    print(c["case"], len(classes), sorted(classes)[:3])
json.dump(out, open(F("fix_mining", "failing_tests.json"), "w", encoding="utf-8"), indent=1)
