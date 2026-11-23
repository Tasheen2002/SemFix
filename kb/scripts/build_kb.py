"""Build the knowledge base (KB) of behavioral breakages and their validated fixes.

One entry per BEHAVIORAL case (56), from frozen sources only:
  breakage  : dependency, versions, failing test classes, exception types and first error lines (BREAKING log)
  behavior  : rule, behavior-change category/description, primary cause, mechanism family (classification v1.0)
  library   : GitHub compare link and Maven source links between the two versions (BUMP benchmark)
  fix       : validated patch text, fix type, author label (developer / derived / researcher-written), explanation
  leakage   : exclusion lists for L1/L2/L3 (results/retrieval_exclusions.csv) and the grouped fold
Every entry is labelled with its fix author; whether researcher-written fixes are retrievable is a retrieval-time switch.

Output: kb/entries.jsonl (+ kb/kb_manifest.json)
Usage: python -I build_kb.py <research root>
"""
import csv, hashlib, json, os, re, sys
from collections import Counter

ROOT = sys.argv[1]
P = lambda *x: os.path.join(ROOT, *x)
FX = lambda *x: P("fix_mining", "fixes_v1.0", *x)

index = {int(r["case_number"]): r for r in csv.DictReader(open(FX("fix_index.csv"), encoding="utf-8"))}
final = {int(r["case_number"]): r for r in csv.DictReader(open(P("results", "classification_v1.0", "final_classification_rule_based.csv"), encoding="utf-8"))}
cls = {r["case_id"]: r for r in csv.DictReader(open(P("results", "classification_v1.0", "behavioral_classification.csv"), encoding="utf-8"))}
excl = {int(r["case_number"]): r for r in csv.DictReader(open(P("results", "classification_v1.0", "retrieval_exclusions.csv"), encoding="utf-8"))}
folds = {int(r["case_number"]): r for r in csv.DictReader(open(P("results", "classification_v1.0", "evaluation_folds.csv"), encoding="utf-8"))}
devfix = {int(r["case_number"]): r for r in csv.DictReader(open(FX("developer_fixes.csv"), encoding="utf-8"))}

EXC = re.compile(r"\b((?:[a-z_][\w$]*\.)+[A-Z][\w$]*(?:Exception|Error|Failure))\b")


def read(p):
    raw = open(p, "rb").read()
    t = raw.decode("utf-16", "replace") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8", "replace")
    return [re.sub(r"\x1b\[[0-9;]*m", "", l) for l in t.splitlines()]


def signature(lines):
    """Exception types and the first distinct error lines of the failing tests."""
    exc, msgs = Counter(), []
    for i, l in enumerate(lines):
        if re.search(r"<<< (FAILURE|ERROR)!", l) and "Tests run" not in l:
            for nxt in lines[i + 1:i + 4]:
                m = EXC.search(nxt)
                if m:
                    exc[m.group(1)] += 1
                    s = nxt.strip()[:300]
                    if s not in msgs:
                        msgs.append(s)
                    break
        if l.strip().startswith("Caused by:"):
            m = EXC.search(l)
            if m:
                exc[m.group(1)] += 1
                s = l.strip()[:300]
                if s not in msgs:
                    msgs.append(s)
    slf4j = [l.strip() for l in lines if l.startswith("SLF4J:")][:4]
    return dict(exception_types=[e for e, _ in exc.most_common(8)], error_lines=msgs[:6], slf4j_console=slf4j)


def ids(field):
    return sorted(int(x) for x in (field or "").split())


bump = {}
for n, r in index.items():
    bump[n] = json.load(open(P("bump", "data", "benchmark", r["case_id"] + ".json"), encoding="utf-8"))

entries = []
for n in sorted(index):
    ix, fc, c, ex, fo, dv, bm = index[n], final[n], cls[index[n]["case_id"]], excl[n], folds[n], devfix[n], bump[n]
    sig = signature(read(P(c["breaking_log"])))
    patch = open(FX(ix["patch"]), encoding="utf-8", errors="replace").read()
    changed = re.findall(r"^diff --git a/(\S+) b/", patch, re.M)
    u = bm["updatedDependency"]
    g, a = ix["dependency"].split(":")
    author = ix["fix_author"]
    # The explanation must describe the patch actually stored: developer fixes use the developers' commit notes;
    # derived and researcher-written fixes use their own recipe description, without internal bookkeeping labels.
    if ix["reference_group"] == "DEVELOPER_FIX":
        explanation = dv["notes"]
    else:
        explanation = re.sub(r"^(RESEARCHER-WRITTEN \(Claude\), not a developer fix: shows the case is fixable; NOT a reference answer\. |"
                             r"DERIVED minimal companion fix \(NOT the developer's\): )", "", ix["recipe_source"]).strip()
    e = dict(
        kb_id=f"BUMP-BEH-{n:03d}", case_number=n, case_id=ix["case_id"], project=ix["project"],
        breakage=dict(dependency=ix["dependency"], group_id=g, artifact_id=a, old_version=ix["old_version"], new_version=ix["new_version"],
                      version_update_type=u["versionUpdateType"], dependency_scope=u["dependencyScope"],
                      failing_test_classes=[t for t in ix["failing_test_classes"].split(";") if t],
                      breaking_tests=int(ix["breaking_tests"]), breaking_failures=int(ix["breaking_failures"]), breaking_errors=int(ix["breaking_errors"]),
                      **sig),
        behavior=dict(rule=fc["rule"], rule_name=fc["rule_name"], category=fc["behavior_change_category"],
                      description=fc["behavior_change"], primary_cause=fc["primary_cause"], mechanism_family=fo["mechanism_family"],
                      binary_linkage=fc["binary_linkage"]),
        library_change=dict(github_compare_link=u["githubCompareLink"] if u["githubCompareLink"].startswith("http") else "",
                            maven_source_pre=u["mavenSourceLinkPre"], maven_source_new=u["mavenSourceLinkBreaking"],
                            note="links only; library diffs are not yet downloaded into the KB"),
        fix=dict(reference_group=ix["reference_group"], author=author, is_reference_answer=ix["reference_group"] != "RESEARCHER_WRITTEN_ONLY",
                 fix_type=ix["fix_type"], developer_commit=ix["developer_fix_commit"], explanation=explanation,
                 changed_files=changed, patch=patch, patch_sha256=ix["patch_sha256"],
                 validated=dict(verdict=ix["validation_verdict"], tests=int(ix["fixed_tests"]), failures=int(ix["fixed_failures"]),
                                errors=int(ix["fixed_errors"]), maven_exit=ix["maven_exit"], date=ix["validation_date"])),
        leakage=dict(fold=int(fo["fold"]), project_dependency_group=fo["project_dependency_group"],
                     exclude_L1=ids(ex["exclude_L1_duplicates"]),
                     exclude_L2=sorted(set(ids(ex["exclude_L1_duplicates"])) | set(ids(ex["exclude_L2_same_project_dependency"]))),
                     exclude_L3=sorted(set(ids(ex["exclude_L1_duplicates"])) | set(ids(ex["exclude_L2_same_project_dependency"]))
                                       | set(ids(ex["exclude_L3_same_mechanism"])))),
        provenance=dict(classification="results/classification_v1.0", fixes="fix_mining/fixes_v1.0", breaking_log=c["breaking_log"],
                        bump_record=f"bump/data/benchmark/{ix['case_id']}.json"),
    )
    # Text used by lexical/semantic retrieval: what a NEW breakage would also show (no fix text, so queries match on symptoms).
    e["retrieval_text"] = " ".join([
        e["breakage"]["dependency"], g, a, f"{ix['old_version']} -> {ix['new_version']}", u["versionUpdateType"],
        " ".join(e["breakage"]["failing_test_classes"]), " ".join(sig["exception_types"]), " ".join(sig["error_lines"]),
        " ".join(sig["slf4j_console"]), e["behavior"]["category"], e["behavior"]["description"], e["behavior"]["primary_cause"]])
    entries.append(e)

os.makedirs(P("kb"), exist_ok=True)
with open(P("kb", "entries.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
    for e in entries:
        fh.write(json.dumps(e, ensure_ascii=False) + "\n")
man = dict(entries=len(entries), built_from=["results/classification_v1.0", "fix_mining/fixes_v1.0", "bump/data/benchmark (BUMP @324d551)"],
           by_fix_author=Counter(e["fix"]["author"] for e in entries), by_category=Counter(e["behavior"]["category"] for e in entries),
           by_mechanism=Counter(e["behavior"]["mechanism_family"] for e in entries),
           with_compare_link=sum(1 for e in entries if e["library_change"]["github_compare_link"]),
           with_exception_types=sum(1 for e in entries if e["breakage"]["exception_types"]),
           entries_sha256=hashlib.sha256(open(P("kb", "entries.jsonl"), "rb").read()).hexdigest())
json.dump(man, open(P("kb", "kb_manifest.json"), "w", encoding="utf-8"), indent=1)
print(json.dumps(man, indent=1))
