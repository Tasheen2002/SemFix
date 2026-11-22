"""Freeze the fix dataset as v1.0 (fix_mining/fixes_v1.0/). Approved by the researcher 2026-11-21.

Copies (never moves) the validated fixes, results, logs, recipes and scripts into one folder; writes fix_index.csv
(one row per case, with the frozen patch path), repo_snapshot.json (commit of every mined repository), README.md and
SHA256SUMS.txt. Refuses to overwrite an existing freeze. The working folders are left untouched.
Usage: python -I freeze_fixes_v1.py <research root>
"""
import csv, datetime, hashlib, json, os, shutil, subprocess, sys
from collections import Counter

ROOT = sys.argv[1]
FM = lambda *a: os.path.join(ROOT, "fix_mining", *a)
OUT = FM("fixes_v1.0")
DATE = "2026-11-21"
if os.path.exists(OUT):
    sys.exit(f"{OUT} already exists; a frozen version is never overwritten (make v1.1 instead).")
O = lambda *a: os.path.join(OUT, *a)
for d in ("reference_fixes", "researcher_written_fixes", "failed_attempts", "developer_original_commits",
          "validation", "logs/reference", "logs/researcher_written", "scripts"):
    os.makedirs(O(d), exist_ok=True)

rows = list(csv.DictReader(open(FM("developer_fixes.csv"), encoding="utf-8")))
V = {json.loads(l)["case"]: json.loads(l) for l in open(FM("validation", "results.jsonl"), encoding="utf-8") if l.strip()}
R = {json.loads(l)["case"]: json.loads(l) for l in open(FM("researcher_written", "results.jsonl"), encoding="utf-8") if l.strip()}
cases = {c["case"]: c for c in json.load(open(FM("cases.json"), encoding="utf-8"))}
assert len(rows) == 56

index = []
for r in rows:
    n = int(r["case_number"]); g = r["reference_group"]
    ref = g in ("DEVELOPER_FIX", "DERIVED_MINIMAL_FIX")
    rec = (V if ref else R)[n]
    assert rec["verdict"] == "FIX_VALIDATED", (n, rec["verdict"])
    folder, logdir = ("reference_fixes", "logs/reference") if ref else ("researcher_written_fixes", "logs/researcher_written")
    patch = f"{folder}/case{n}.patch"
    shutil.copy2(os.path.join(ROOT, rec["patch"]), O(patch))
    log = f"{logdir}/case{n}_fixed.log"
    shutil.copy2(os.path.join(ROOT, rec["log"]), O(log))
    o, f = rec["original"], rec["fixed"]
    index.append(dict(
        case_number=n, case_id=r["case_id"], project=r["project"], dependency=r["dependency"],
        old_version=r["old_version"], new_version=r["new_version"], rule=r["rule"],
        behavior_change_category=r["behavior_change_category"], related_group=r["related_group"],
        reference_group=g, evaluation_mode=r["evaluation_mode"],
        fix_author={"DEVELOPER_FIX": "developer", "DERIVED_MINIMAL_FIX": "derived from developer fix (Claude)",
                    "RESEARCHER_WRITTEN_ONLY": "researcher-written (Claude); NOT a reference answer"}[g],
        fix_type=r["fix_type"] if ref else "RESEARCHER_WRITTEN", fix_status=r["fix_status"],
        developer_fix_commit=r["fix_commit"], developer_fix_date=r["fix_date"],
        patch=patch, patch_sha256=hashlib.sha256(open(O(patch), "rb").read()).hexdigest(),
        recipe_source=rec["recipe_source"], validation_verdict=rec["verdict"], validation_date=rec["date"],
        breaking_tests=o["tests"], breaking_failures=o["failures"], breaking_errors=o["errors"],
        fixed_tests=f["tests"], fixed_failures=f["failures"], fixed_errors=f["errors"], maven_exit=rec["maven_exit"],
        failing_test_classes=";".join(rec["target_classes"]), validation_log=log, image=rec["image"]))

with open(O("fix_index.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(index[0])); w.writeheader(); w.writerows(index)

# Record, not answer: Case 171's failed researcher-written attempt, plus the earlier failed attempts.
shutil.copy2(FM("researcher_written", "backports", "case171.patch"), O("failed_attempts", "case171_researcher_written_attempt7.patch"))
for d, tag in ((FM("validation", "logs"), "reference"), (FM("researcher_written", "logs"), "researcher_written")):
    for fn in os.listdir(d):
        if "attempt" in fn or "derived_logback_only" in fn:
            shutil.copy2(os.path.join(d, fn), O("failed_attempts", f"{tag}_{fn}"))
for fn in os.listdir(FM("patches")):
    shutil.copy2(FM("patches", fn), O("developer_original_commits", fn))
shutil.copy2(FM("validation", "case171_developer_replay.source.patch"), O("developer_original_commits", "case171_developer_replay.source.patch"))

for src, dst in ((FM("validation", "recipes.json"), "recipes_reference.json"),
                 (FM("researcher_written", "recipes.json"), "recipes_researcher_written.json"),
                 (FM("validation", "results.jsonl"), "results_reference.jsonl"),
                 (FM("researcher_written", "results.jsonl"), "results_researcher_written.jsonl"),
                 (FM("validation", "results_superseded.jsonl"), "results_reference_superseded.jsonl"),
                 (FM("researcher_written", "results_superseded.jsonl"), "results_researcher_written_superseded.jsonl")):
    shutil.copy2(src, O("validation", dst))
for fn in ("developer_fixes.csv", "fix_summary.json", "version_trace.json", "pr_meta.json", "cases.json", "failing_tests.json", "README.md"):
    shutil.copy2(FM(fn), O(fn if fn != "README.md" else "fix_mining_README.md"))
shutil.copy2(FM("researcher_written", "README.md"), O("researcher_written_README.md"))
for fn in os.listdir(FM("scripts")):
    if fn.endswith(".py"):
        shutil.copy2(FM("scripts", fn), O("scripts", fn))

snap = {}
for c in cases.values():
    repo = FM("repos", c["repo"])
    if c["slug"] not in snap:
        g = lambda *a: subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True).stdout.strip()
        ref = g("symbolic-ref", "--short", "refs/remotes/origin/HEAD")
        snap[c["slug"]] = dict(url=f"https://github.com/{c['slug']}", default_branch=ref.replace("origin/", ""),
                               default_branch_head=g("rev-parse", ref), fetched_by="git clone (full) on 2026-11-20/21")
json.dump(snap, open(O("repo_snapshot.json"), "w", encoding="utf-8"), indent=1)

cnt = Counter(x["reference_group"] for x in index)
readme = f"""# Fix dataset v1.0 (frozen {DATE})

This is a validated fix for every one of the 56 BEHAVIORAL cases in classification v1.0, each tested on its original BUMP BREAKING image. **Do not edit these files.** A later change should produce v1.1 with a change note.

| Reference group | Cases | Author | How a repair tool is judged |
|---|---:|---|---|
| DEVELOPER_FIX | {cnt['DEVELOPER_FIX']} | The project's developers (minimal backport, or replayed commit for Case 171) | Compare with this fix, plus tests |
| DERIVED_MINIMAL_FIX | {cnt['DERIVED_MINIMAL_FIX']} | Derived from the developer fix (pay-adminusers: logback 1.3.5 instead of the Dropwizard 3 migration) | Compare with this fix, plus tests |
| RESEARCHER_WRITTEN_ONLY | {cnt['RESEARCHER_WRITTEN_ONLY']} | Researcher-written (Claude). **Not a reference answer**; it only shows the case can be fixed. | Tests only: failing tests pass and nothing else breaks |

## Validation rule (all 56 pass)

Each fix was checked as follows:
- **Image:** a fresh `--rm` container of the original BREAKING image; the workspace was never mounted.
- **Apply:** `git apply --check`, then `git apply`.
- **Build:** `mvn clean test -B`. For btrplace (Cases 163, 168) only the `json` module and the modules it needs were built (`-pl json -am`).

A fix passes only if:
- the patch applies;
- at least one test runs, and every originally failing test class runs;
- BUILD SUCCESS with 0 failures, 0 errors, and `MAVEN_EXIT=0`.

This was an AI validation (Claude), not a human review.

## Known limitations

- **Failing-class names are missing for Cases 14, 114, 163 and 168** (h2 and TestNG `TestSuite` logs). For these, "target tests ran" rests on the whole suite passing.
- **"Nothing else breaks" was judged against the BREAKING run, not yet against the PRE test list.** The repair harness (next step) adds the PRE comparison.
- **Case 171's reference fix has two adjustments:** slf4j-api kept at 2.0.0, and the jax-rs-pac4j SNAPSHOT replaced by the 6.0.0 release.
- **Some fixes download artifacts** from Maven Central when run (new library versions not cached in the images).

## Files

| Path | Contents |
|---|---|
| `fix_index.csv` | **Start here.** One row per case: group, author, frozen patch path and SHA-256, validation counts, log |
| `reference_fixes/` | 28 patches (21 developer + 7 derived) |
| `researcher_written_fixes/` | 28 patches (not reference answers) |
| `developer_original_commits/` | The developers' full original commits as diffs, plus the Case 171 replay source |
| `failed_attempts/` | Superseded attempts kept as a record (Case 181 attempts 1–2, Case 171 derived and researcher-written attempts 1–7) |
| `validation/` | Recipes, final results and superseded results for both groups |
| `logs/` | The final validation log for every case |
| `developer_fixes.csv`, `fix_summary.json`, `version_trace.json`, `pr_meta.json`, `cases.json`, `failing_tests.json` | Mining data |
| `repo_snapshot.json` | The default-branch commit of each of the 18 mined repositories, to reproduce the mining |
| `scripts/` | Every script used (mining, validation, re-check, catalogue, this freeze) |
| `SHA256SUMS.txt` | Hashes of every frozen file |
"""
open(O("README.md"), "w", encoding="utf-8").write(readme)

with open(O("SHA256SUMS.txt"), "w", encoding="utf-8", newline="\n") as fh:   # LF, so `sha256sum -c` works
    for a, _, fs in sorted(os.walk(OUT)):
        for fn in sorted(fs):
            p = os.path.join(a, fn)
            if fn != "SHA256SUMS.txt":
                fh.write(f"{hashlib.sha256(open(p, 'rb').read()).hexdigest()}  {os.path.relpath(p, OUT).replace(os.sep, '/')}\n")
n_files = sum(len(fs) for _, _, fs in os.walk(OUT))
print(json.dumps(dict(cases=len(index), groups=cnt, files=n_files, out=os.path.relpath(OUT, ROOT)), indent=1))
