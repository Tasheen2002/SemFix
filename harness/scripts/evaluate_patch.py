"""Repair harness (v2): decide whether a candidate patch repairs a BUMP BEHAVIORAL case.

A patch is REPAIRED only if all five checks pass:
  APPLIES        git apply --check + git apply succeed on the BREAKING source
  BUILD          BUILD SUCCESS and MAVEN_EXIT=0 for the case's test command
  TARGET_FIXED   every originally failing test class ran and passed (0 failures, 0 errors)
  NO_REGRESSION  every PRE-passing test class (in the modules built) ran and passed; a missing class fails
                 (so deleting tests cannot pass). TestNG `TestSuite` modules are checked by module aggregate.
  UPDATE_KEPT    dependency:tree resolves the updated dependency at >= the case's new version (no revert)

Robustness (v2, 2026-11-22):
  * dependency:tree runs as `test-compile dependency:tree`, so multi-module builds resolve sibling modules
    (v1 ran it alone and failed on btrplace/sparql-anything). If it fails, it is retried once with the pinned
    plugin org.apache.maven.plugins:maven-dependency-plugin:3.6.1 (v1 failed on a download of plugin 2.8).
    If both fail, UPDATE_KEPT is UNKNOWN and the verdict is INCONCLUSIVE, never NOT_REPAIRED.
  * Flaky tests: if attempt 1 fails ONLY because tests failed (patch applied, update kept, no class missing),
    the whole evaluation is repeated once in a fresh container. A deterministic failure fails twice. A pass on
    attempt 2 is REPAIRED with flaky=true, and attempt 1's failures are kept in the result.

Verdicts: REPAIRED | NOT_REPAIRED | INCONCLUSIVE (infrastructure: dependency tree unavailable).
Reported but not part of the verdict: test files touched, @Test lines removed, test files deleted, fewer tests than
PRE in a class, and (reference cases) changed-file overlap with the frozen reference fix.

Each attempt uses a fresh `--rm` container of the original BREAKING image; the workspace is never mounted.
Output: harness/runs/<label>/case<N>.json and case<N>.log (attempt 2: case<N>_attempt2.log)
Usage: python -I evaluate_patch.py <research root> --case N --patch <file> --label <run label> [--keep-image] [--flaky-reruns 1]
"""
import argparse, csv, datetime, json, os, re, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("root"); ap.add_argument("--case", type=int, required=True); ap.add_argument("--patch", required=True)
ap.add_argument("--label", required=True); ap.add_argument("--keep-image", action="store_true")
ap.add_argument("--flaky-reruns", type=int, default=1)
a = ap.parse_args()
ROOT = a.root
P = lambda *x: os.path.join(ROOT, *x)
N = a.case
HARNESS_VERSION = "v2"

cases = {c["case"]: c for c in json.load(open(P("fix_mining", "cases.json"), encoding="utf-8"))}
c = cases[N]
base = json.load(open(P("harness", "baselines", "pre_tests.json"), encoding="utf-8"))[str(N)]
index = {int(r["case_number"]): r for r in csv.DictReader(open(P("fix_mining", "fixes_v1.0", "fix_index.csv"), encoding="utf-8"))}
ft = json.load(open(P("fix_mining", "failing_tests.json"), encoding="utf-8"))
# Case-specific build commands (identical to fix validation). btrplace's full build takes hours; its failure is in `json`.
COMMAND = {163: "mvn clean test -B -pl json -am", 168: "mvn clean test -B -pl json -am"}
cmd = COMMAND.get(N, "mvn clean test -B")
restricted = "-pl " in cmd
pl = " -pl json -am" if restricted else ""
dep = f"{c['group']}:{c['artifact']}"
TREE = f"mvn -B -DskipTests{pl} test-compile dependency:tree -Dincludes={dep}"
TREE_PINNED = f"mvn -B -DskipTests{pl} test-compile org.apache.maven.plugins:maven-dependency-plugin:3.6.1:tree -Dincludes={dep}"

sys.path.insert(0, P("harness", "scripts"))
from build_pre_baselines import parse, read  # same parser for PRE and candidate runs


def vkey(v):
    out = []
    for p in re.split(r"[.\-_]", v or ""):
        m = re.match(r"(\d+)(.*)", p)
        out.append((1, int(m.group(1)), m.group(2).lower()) if m else (0, 0, p.lower()))
    return out


def same(a_, b_):
    return a_ == b_ or a_.endswith("." + b_) or b_.endswith("." + a_)


def docker(*x):
    return subprocess.run(["docker", *x], capture_output=True, text=True, encoding="utf-8", errors="replace")


out_dir = P("harness", "runs", a.label); os.makedirs(out_dir, exist_ok=True)
img = f"ghcr.io/chains-project/breaking-updates:{c['id']}-breaking"
had = bool(docker("images", "-q", img).stdout.strip())
if not had:
    docker("pull", "-q", img)

SCRIPT = ("exec 2>&1; cat > /tmp/candidate.patch; echo '=== GIT APPLY CHECK ==='; "
          "if git apply --check -v /tmp/candidate.patch && git apply -v /tmp/candidate.patch; then echo APPLY_OK; else echo APPLY_FAILED; exit 3; fi; "
          f"echo '=== BUILD ==='; {cmd}; echo MAVEN_EXIT=$?; "
          f"echo '=== DEPENDENCY TREE ==='; {TREE}; rc=$?; echo TREE_EXIT=$rc; "
          f"if [ $rc -ne 0 ]; then echo '=== DEPENDENCY TREE RETRY ==='; {TREE_PINNED}; echo TREE_RETRY_EXIT=$?; fi")


def run_once(attempt):
    log = os.path.join(out_dir, f"case{N}.log" if attempt == 1 else f"case{N}_attempt{attempt}.log")
    start = datetime.datetime.now()
    with open(a.patch, "rb") as pin, open(log, "wb") as lout:
        subprocess.run(["docker", "run", "--rm", "-i", "--name", f"harness-{a.label}-case{N}-a{attempt}"[:60], "--entrypoint", "sh", img, "-c", SCRIPT],
                       stdin=pin, stdout=lout, stderr=subprocess.STDOUT)
    return log, round((datetime.datetime.now() - start).total_seconds())


def evaluate(log):
    lines = read(log)
    idx = lambda tag: next((i for i, l in enumerate(lines) if tag in l), None)
    b0, t0 = idx("=== BUILD ==="), idx("=== DEPENDENCY TREE ===")
    build = lines[b0:t0] if b0 is not None else []
    tree = lines[t0:] if t0 is not None else []
    checks, notes = {}, []
    checks["APPLIES"] = any(l.strip() == "APPLY_OK" for l in lines)
    status = ([m.group(1) for l in build for m in [re.search(r"BUILD (SUCCESS|FAILURE)", l)] if m] or ["NONE"])[0]
    mex = ([m.group(1) for l in build for m in [re.search(r"MAVEN_EXIT=(\d+)", l)] if m] or [""])[0]
    checks["BUILD"] = status == "SUCCESS" and mex == "0"

    run_mods = parse(build)
    run_classes = {k: v for m in run_mods.values() for k, v in m["classes"].items()}
    total = [sum((m["aggregate"] or [sum(x[i] for x in m["classes"].values()) for i in range(4)])[i] for m in run_mods.values()) for i in range(4)]

    def class_result(name):
        hit = [v for k, v in run_classes.items() if same(k, name)]
        return hit[0] if hit else None

    targets = [t for t in ft[str(N)]["classes"] if t != "TestSuite"]
    target_detail = {}
    for t in targets:
        v = class_result(t)
        target_detail[t] = "did not run" if v is None else ("passed" if v[0] > 0 and v[1] == v[2] == 0 else f"failed {v[1]}F/{v[2]}E")
    if targets:
        checks["TARGET_FIXED"] = all(s == "passed" for s in target_detail.values())
    else:
        checks["TARGET_FIXED"] = total[0] > 0 and total[1] == total[2] == 0
        notes.append("no failing-class names recorded for this case; TARGET_FIXED uses the whole run (tests ran, 0 failures/errors)")

    built = set(run_mods)
    regress, fewer, skipped_mods, missing = [], [], [], 0
    for mod, m in base["modules"].items():
        if restricted and mod not in built:
            skipped_mods.append(mod); continue
        if not m["classes"] and m["aggregate"]:
            r = run_mods.get(mod, {}).get("aggregate")
            if not r:
                regress.append(f"{mod}: module did not run tests"); missing += 1
            elif r[1] or r[2]:
                regress.append(f"{mod}: {r[1]}F/{r[2]}E")
            elif r[0] < m["aggregate"][0]:
                fewer.append(f"{mod}: {r[0]} < PRE {m['aggregate'][0]} tests")
            continue
        for k, v in m["classes"].items():
            if not (v[0] > 0 and v[1] == v[2] == 0):
                continue
            r = class_result(k)
            if r is None:
                regress.append(f"{k}: did not run"); missing += 1
            elif r[1] or r[2]:
                regress.append(f"{k}: {r[1]}F/{r[2]}E")
            elif r[0] < v[0]:
                fewer.append(f"{k}: {r[0]} < PRE {v[0]} tests")
    checks["NO_REGRESSION"] = not regress
    if skipped_mods:
        notes.append(f"PRE modules outside the restricted build ({cmd}) not checked: {len(skipped_mods)}")

    resolved = sorted({m.group(1) for l in tree for m in [re.search(re.escape(dep) + r":[\w-]+:([\w.\-]+)(?::[\w]+)?", l)] if m})
    tree_ok = any(re.search(r"TREE(_RETRY)?_EXIT=0", l) for l in tree)
    if resolved:
        checks["UPDATE_KEPT"] = all(vkey(v) >= vkey(c["new"]) for v in resolved)
    elif tree_ok:
        checks["UPDATE_KEPT"] = False      # tree worked but the dependency is gone: removing it is not keeping the update
        notes.append(f"{dep} absent from a successful dependency:tree (dependency removed)")
    else:
        checks["UPDATE_KEPT"] = None       # infrastructure: no tree at all
        notes.append("dependency:tree failed twice (plain and pinned 3.6.1); UPDATE_KEPT unknown")
    test_only_failure = (checks["APPLIES"] and checks["UPDATE_KEPT"] is not False and missing == 0 and
                         (not checks["BUILD"] or not checks["TARGET_FIXED"] or not checks["NO_REGRESSION"]) and
                         all(s == "passed" or s.startswith("failed") for s in target_detail.values()) and total[0] > 0)
    return dict(checks=checks, notes=notes, status=status, mex=mex, total=total, target_detail=target_detail,
                regress=regress, fewer=fewer, resolved=resolved, test_only_failure=test_only_failure)


def verdict_of(ev):
    vals = list(ev["checks"].values())
    if all(v is True for v in vals):
        return "REPAIRED"
    if any(v is False for v in vals):
        return "NOT_REPAIRED"
    return "INCONCLUSIVE"


attempts = []
log, secs = run_once(1)
ev = evaluate(log); attempts.append(dict(attempt=1, log=os.path.relpath(log, ROOT), seconds=secs, verdict=verdict_of(ev),
                                         failed=[k for k, v in ev["checks"].items() if v is False], regressions=ev["regress"][:20]))
for k in range(a.flaky_reruns):
    if verdict_of(ev) == "NOT_REPAIRED" and ev["test_only_failure"]:
        log, s2 = run_once(k + 2); secs += s2
        ev = evaluate(log); attempts.append(dict(attempt=k + 2, log=os.path.relpath(log, ROOT), seconds=s2, verdict=verdict_of(ev),
                                                 failed=[x for x, v in ev["checks"].items() if v is False], regressions=ev["regress"][:20]))
if not had and not a.keep_image:
    docker("rmi", img)

verdict = verdict_of(ev)
flaky = len(attempts) > 1 and verdict == "REPAIRED"

ptxt = open(a.patch, encoding="utf-8", errors="replace").read()
files = re.findall(r"^diff --git a/(\S+) b/", ptxt, re.M)
deleted = re.findall(r"^diff --git a/(\S+) b/\S+\n(?:old mode .*\n|new mode .*\n)*deleted file mode", ptxt, re.M)
test_files = [f for f in files if "/src/test/" in "/" + f]
removed_tests = len(re.findall(r"^-\s*@Test\b", ptxt, re.M)) - len(re.findall(r"^\+\s*@Test\b", ptxt, re.M))
info = dict(files_changed=files, test_files_changed=test_files, test_files_deleted=[f for f in deleted if "/src/test/" in "/" + f],
            net_test_annotations_removed=max(removed_tests, 0), classes_with_fewer_tests_than_pre=ev["fewer"][:20])
ref = index[N]
if ref["reference_group"] in ("DEVELOPER_FIX", "DERIVED_MINIMAL_FIX"):
    rp = open(P("fix_mining", "fixes_v1.0", ref["patch"]), encoding="utf-8", errors="replace").read()
    rfiles = set(re.findall(r"^diff --git a/(\S+) b/", rp, re.M))
    info["reference_fix_file_overlap"] = round(len(rfiles & set(files)) / len(rfiles | set(files)), 3) if files else 0.0
    info["identical_to_reference_fix"] = ptxt.replace("\r\n", "\n").strip() == rp.replace("\r\n", "\n").strip()

checks = {k: ("UNKNOWN" if v is None else v) for k, v in ev["checks"].items()}
res = dict(case=N, case_id=c["id"], label=a.label, harness_version=HARNESS_VERSION,
           patch=os.path.relpath(os.path.abspath(a.patch), ROOT), date=datetime.date.today().isoformat(),
           verdict=verdict, flaky=flaky, attempts=attempts, checks=checks, failed_checks=[k for k, v in ev["checks"].items() if v is False],
           evaluation_mode=ref["evaluation_mode"], reference_group=ref["reference_group"], command=cmd, tree_command=TREE, seconds=secs,
           build=dict(status=ev["status"], maven_exit=ev["mex"], tests=ev["total"][0], failures=ev["total"][1], errors=ev["total"][2], skipped=ev["total"][3]),
           pre_baseline=base["total"], target_classes=ev["target_detail"], regressions=ev["regress"][:50], regression_count=len(ev["regress"]),
           dependency=dep, new_version=c["new"], resolved_versions=ev["resolved"], info=info, notes=ev["notes"],
           log=attempts[-1]["log"], image=img, source=f"repair harness {HARNESS_VERSION} (Claude); AI evaluation")
json.dump(res, open(os.path.join(out_dir, f"case{N}.json"), "w", encoding="utf-8"), indent=1)
print(f"case {N} [{a.label}] {verdict}{' (flaky: passed on attempt ' + str(len(attempts)) + ')' if flaky else ''}  "
      + " ".join(f"{k}={'ok' if v is True else ('?' if v is None else 'FAIL')}" for k, v in ev["checks"].items())
      + f"  tests {ev['total'][0]}/{ev['total'][1]}/{ev['total'][2]}  {dep}={','.join(ev['resolved']) or '-'}  {secs}s"
      + (f"  regressions={len(ev['regress'])}" if ev["regress"] else ""))
