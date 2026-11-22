"""Validate minimal backports of the developer fixes on the original BUMP BREAKING images.

Per case (from fix_mining/validation/recipes.json):
 1. build a unified diff against the breaking commit's own file (backports/case<N>.patch);
 2. in a fresh --rm container of the BREAKING image: `git apply --check`, `git apply`, then the original
    `mvn clean test -B` (or the recipe's command), with Maven's exit code captured (MAVEN_EXIT=);
 3. for POM fixes, `mvn dependency:tree -Dincludes=...` in the same container;
 4. compare with the original BREAKING log: build result, totals, and whether each originally failing test class still fails.
Pulled images are removed afterwards unless they were already present. Results append to validation/results.jsonl;
cases already there are skipped (resumable). The workspace is never mounted.
Usage: python -I validate_fixes.py <research root> [comma-separated case numbers] [--researcher]
  --researcher: use fix_mining/researcher_written/ (recipes.json, backports/, logs/, results.jsonl) instead of validation/.
"""
import csv, datetime, difflib, json, os, re, subprocess, sys

ROOT = sys.argv[1]
F = lambda *a: os.path.join(ROOT, "fix_mining", *a)
# Second positional/optional flag --researcher selects the separate researcher-written group.
RESEARCHER = "--researcher" in sys.argv
if RESEARCHER:
    sys.argv.remove("--researcher")
GROUP_DIR = "researcher_written" if RESEARCHER else "validation"
V = lambda *a: F(GROUP_DIR, *a)
for d in ("backports", "logs"):
    os.makedirs(V(d), exist_ok=True)
cases = {c["case"]: c for c in json.load(open(F("cases.json"), encoding="utf-8"))}
ft = json.load(open(F("failing_tests.json"), encoding="utf-8"))
cls = {r["case_id"]: r for r in csv.DictReader(open(os.path.join(ROOT, "results", "behavioral_classification.csv"), encoding="utf-8"))}
recipes = {n: r for r in json.load(open(V("recipes.json"), encoding="utf-8")) for n in r["cases"]}
only = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else sorted(recipes)
done = set()
if os.path.exists(V("results.jsonl")):
    done = {json.loads(l)["case"] for l in open(V("results.jsonl"), encoding="utf-8") if l.strip()}


def gshow(repo, rev, path):
    r = subprocess.run(["git", "-C", F("repos", repo), "show", f"{rev}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8") if r.returncode == 0 else None


def edit_patch(n, c, r):
    """Unified diff for one edit of the breaking commit's file (or a new file)."""
    old = gshow(c["repo"], c["id"], r["file"])
    if r["kind"] == "new_file":
        assert old is None, f"case {n}: {r['file']} already exists"
        body = r["content"] if r["content"].endswith("\n") else r["content"] + "\n"
        lines = body.splitlines(keepends=True)
        return (f"diff --git a/{r['file']} b/{r['file']}\nnew file mode 100644\n--- /dev/null\n+++ b/{r['file']}\n"
                f"@@ -0,0 +1,{len(lines)} @@\n" + "".join("+" + l for l in lines))
    assert old is not None, f"case {n}: {r['file']} missing at breaking commit"
    crlf = "\r\n" in old
    o = old.replace("\r\n", "\n")
    if r["kind"] == "replace":
        assert o.count(r["old"]) == 1, f"case {n}: expected exactly one match, found {o.count(r['old'])}"
        new = o.replace(r["old"], r["new"])
    elif r["kind"] == "regex":
        new, k = re.subn(r["old"], r["new"], o)
        assert k == 1, f"case {n}: regex matched {k} times"
    elif r["kind"] == "regex_all":
        new, k = re.subn(r["old"], r["new"], o)
        assert k >= r.get("min_matches", 1), f"case {n}: regex matched {k} times"
    elif r["kind"] == "subs":   # sequential regex substitutions: [[pattern, replacement, min_matches], ...]
        new = o
        for pat, rep, mn in r["subs"]:
            new, k = re.subn(pat, rep, new)
            assert k >= mn, f"case {n}: {pat!r} matched {k} times (need {mn})"
    elif r["kind"] == "file_from_commit":
        new = gshow(c["repo"], r["commit"], r["file"]).replace("\r\n", "\n")
    else:
        raise ValueError(f"case {n}: unknown edit kind {r['kind']}")
    if crlf:
        o, new = o.replace("\n", "\r\n"), new.replace("\n", "\r\n")
    a, b = o.splitlines(keepends=True), new.splitlines(keepends=True)
    out = []
    for line in difflib.unified_diff(a, b, f"a/{r['file']}", f"b/{r['file']}", n=3):
        out.append(line)
        if not line.endswith("\n"):
            out.append("\n\\ No newline at end of file\n")
    return f"diff --git a/{r['file']} b/{r['file']}\n" + "".join(out)


def make_patch(n):
    c, r = cases[n], recipes[n]
    if r.get("kind") == "raw_patch":   # a ready-made patch against the breaking commit (e.g. a replayed developer commit)
        text = open(os.path.join(ROOT, r["patch_file"]), encoding="utf-8", newline="").read()
    else:
        text = "".join(edit_patch(n, c, e) for e in (r["edits"] if "edits" in r else [r]))
    path = V("backports", f"case{n}.patch")
    open(path, "w", encoding="utf-8", newline="").write(text)
    return path, text


def read_log(p):
    raw = open(p, "rb").read()
    t = raw.decode("utf-16", "replace") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8", "replace")
    return [re.sub(r"\x1b\[[0-9;]*m", "", l) for l in t.splitlines()]


AGG = re.compile(r"Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)\s*$")


def summarize(lines):
    agg, prev = [], None
    for i, l in enumerate(lines):
        m = AGG.search(l)
        if m and "Time elapsed" not in l:
            v = tuple(map(int, m.groups()))
            if prev and v == prev[1] and i - prev[0] < 6:
                continue
            agg.append(v); prev = (i, v)
    tot = [sum(x[i] for x in agg) for i in range(3)]
    status = ([m.group(1) for l in lines for m in [re.search(r"BUILD (SUCCESS|FAILURE)", l)] if m] or ["NONE"])
    failing = set()
    for l in lines:
        m = re.search(r"Tests run: \d+, Failures: \d+, Errors: \d+.*?<<< (?:FAILURE|ERROR)!? *-? *(?:in )?([\w.$]+)", l)
        if m:
            failing.add(m.group(1))
    return dict(build=status[0] if status else "NONE", builds=status, tests=tot[0], failures=tot[1], errors=tot[2],
                failing_classes=sorted(failing))


def docker(*a, **k):
    return subprocess.run(["docker", *a], capture_output=True, text=True, encoding="utf-8", errors="replace", **k)


for n in only:
    if n in done:
        print(n, "already validated, skipping"); continue
    c, r = cases[n], recipes[n]
    patch_path, patch = make_patch(n)
    img = f"ghcr.io/chains-project/breaking-updates:{c['id']}-breaking"
    had = bool(docker("images", "-q", img).stdout.strip())
    if not had:
        docker("pull", "-q", img)
    mvn = r.get("mvn", "mvn clean test -B")
    tree = ""
    if r.get("tree"):
        inc = r["tree"]
        tree = f"; echo '=== DEPENDENCY TREE ==='; mvn -B -DskipTests dependency:tree -Dincludes={inc}; echo TREE_EXIT=$?"
        if "-pl" in mvn:
            tree = tree.replace("dependency:tree", "-pl json -am dependency:tree")
    script = ("exec 2>&1; cat > /tmp/fix.patch; echo '=== GIT APPLY CHECK ==='; "
              "if git apply --check -v /tmp/fix.patch && git apply -v /tmp/fix.patch; then echo APPLY_OK; else echo APPLY_FAILED; exit 3; fi; "
              f"echo '=== BUILD ==='; {mvn}; echo MAVEN_EXIT=$?{tree}")
    log = V("logs", f"case{n}_fixed.log")
    start = datetime.datetime.now()
    with open(patch_path, "rb") as pin, open(log, "wb") as lout:
        rc = subprocess.run(["docker", "run", "--rm", "-i", "--name", f"fixval-case{n}", "--entrypoint", "sh", img, "-c", script],
                            stdin=pin, stdout=lout, stderr=subprocess.STDOUT).returncode
    secs = (datetime.datetime.now() - start).total_seconds()
    if not had:
        docker("rmi", img)
    lines = read_log(log)
    applied = any(l.strip() == "APPLY_OK" for l in lines)
    build_lines = lines[next((i for i, l in enumerate(lines) if "=== BUILD ===" in l), 0):]
    build_lines = build_lines[:next((i for i, l in enumerate(build_lines) if "=== DEPENDENCY TREE ===" in l), len(build_lines))]
    fixed = summarize(build_lines)
    mex = ([m.group(1) for l in lines for m in [re.search(r"MAVEN_EXIT=(\d+)", l)] if m] or [""])[0]
    orig = summarize(read_log(os.path.join(ROOT, cls[c["id"]]["breaking_log"])))
    target = set(ft[str(n)]["classes"]) or set(orig["failing_classes"])
    still = sorted(t for t in target if any(t == f or f.endswith("." + t) or t.endswith("." + f) for f in fixed["failing_classes"]))
    tree_lines = []
    if "=== DEPENDENCY TREE ===" in "\n".join(lines):
        i = next(i for i, l in enumerate(lines) if "=== DEPENDENCY TREE ===" in l)
        inc = [x.split(":")[0] for x in r["tree"].split(",")]
        tree_lines = [l.replace("[INFO] ", "").strip() for l in lines[i:] if any(g in l for g in inc) and ":" in l and "Includes" not in l][:12]
    # A fix only counts if the originally failing test classes actually ran in the fixed build.
    ran = {m.group(1) for l in build_lines for m in [re.search(r"Running ([\w.$]+)\s*$", l)] if m}
    not_run = sorted(t for t in target if t != "TestSuite" and not any(t == x or x.endswith("." + t) or t.endswith("." + x) for x in ran))
    if not applied:
        verdict = "PATCH_DID_NOT_APPLY"
    elif fixed["tests"] == 0:
        verdict = "NO_TESTS_RAN"   # compilation error, or tests silently skipped: nothing is "fixed"
    elif not_run:
        verdict = "TARGET_TESTS_DID_NOT_RUN"
    elif fixed["build"] == "SUCCESS" and mex == "0":
        verdict = "FIX_VALIDATED"
    elif not still and fixed["failures"] + fixed["errors"] < orig["failures"] + orig["errors"]:
        verdict = "TARGET_TESTS_FIXED_OTHER_FAILURES"
    else:
        verdict = "FIX_NOT_EFFECTIVE"
    res = dict(case=n, date=datetime.date.today().isoformat(), image=img, recipe_source=r["source"], group=("researcher-written" if RESEARCHER else "developer-or-derived"), patch=os.path.relpath(patch_path, ROOT),
               command=mvn, applied=applied, maven_exit=mex, seconds=round(secs), verdict=verdict,
               original=dict(build=orig["build"], tests=orig["tests"], failures=orig["failures"], errors=orig["errors"]),
               fixed=dict(build=fixed["build"], tests=fixed["tests"], failures=fixed["failures"], errors=fixed["errors"],
                          failing_classes=fixed["failing_classes"][:10]),
               target_classes=sorted(target), target_classes_still_failing=still, target_classes_not_run=not_run,
               dependency_tree=tree_lines,
               log=os.path.relpath(log, ROOT), source="AI validation (Claude) on the original BREAKING image", fix_author=("researcher-written (Claude); shows the case is fixable, NOT a reference answer" if RESEARCHER else "developer (or derived from the developer fix)"))
    open(V("results.jsonl"), "a", encoding="utf-8").write(json.dumps(res) + "\n")
    print(n, verdict, f"exit={mex}", f"orig t/f/e {orig['tests']}/{orig['failures']}/{orig['errors']}",
          f"-> {fixed['tests']}/{fixed['failures']}/{fixed['errors']}", f"still failing {still}", f"{round(secs)}s", flush=True)
