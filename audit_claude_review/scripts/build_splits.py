"""Leakage-safe retrieval exclusions and grouped folds for the repair experiments (RQ2-RQ4).
Writes results/retrieval_exclusions.csv, results/evaluation_folds.csv, results/evaluation_split_design.md
"""
import csv, collections, os, sys
ROOT = sys.argv[1]
P = lambda *a: os.path.join(ROOT, *a)
rows = list(csv.DictReader(open(P("results", "final_classification_rule_based.csv"), encoding="utf-8")))
by = {r["case_number"]: r for r in rows}
fam = lambda r: r["related_group"].split(" | ")[0]
pdg = lambda r: f"{r['project']}::{r['dependency']}"
exact = lambda r: (r["project"], r["dependency"], r["old_version"], r["new_version"])

g_exact, g_pd, g_fam = collections.defaultdict(set), collections.defaultdict(set), collections.defaultdict(set)
for r in rows:
    g_exact[exact(r)].add(r["case_number"]); g_pd[pdg(r)].add(r["case_number"])
    if fam(r) != "SINGLETON":
        g_fam[fam(r)].add(r["case_number"])
srt = lambda s: " ".join(sorted(s, key=int))
beh = [r for r in rows if r["rule_based_label"] == "BEHAVIORAL"]
behset = {r["case_number"] for r in beh}
ex = []
for r in beh:
    n = r["case_number"]
    l1 = g_exact[exact(r)] - {n}
    l2 = (g_exact[exact(r)] | g_pd[pdg(r)]) - {n}
    l3 = (l2 | g_fam.get(fam(r), set())) - {n}
    ex.append(dict(case_number=n, case_id=r["case_id"], project=r["project"], dependency=r["dependency"],
                   behavior_change_category=r["behavior_change_category"], mechanism_family=fam(r), project_dependency_group=pdg(r),
                   exclude_L1_duplicates=srt(l1), exclude_L2_same_project_dependency=srt(l2), exclude_L3_same_mechanism=srt(l3),
                   behavioral_pool_remaining_L2=len(behset - l2 - {n}), behavioral_pool_remaining_L3=len(behset - l3 - {n}),
                   same_mechanism_examples_available_L2=len((g_fam.get(fam(r), set()) & behset) - l2 - {n})))
with open(P("results", "retrieval_exclusions.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(ex[0])); w.writeheader(); w.writerows(ex)

# Grouped 3-fold split over the behavioral cases: a project+dependency group never spans folds; greedy balance by size
groups = collections.defaultdict(list)
for r in beh: groups[pdg(r)].append(r["case_number"])
folds = {0: [], 1: [], 2: []}
for g, cs in sorted(groups.items(), key=lambda x: (-len(x[1]), x[0])):
    k = min(folds, key=lambda i: (len(folds[i]), i)); folds[k] += [(c, g) for c in cs]
fo = [dict(case_number=c, case_id=by[c]["case_id"], fold=k, project_dependency_group=g, mechanism_family=fam(by[c]),
           behavior_change_category=by[c]["behavior_change_category"]) for k, v in folds.items() for c, g in v]
fo.sort(key=lambda x: int(x["case_number"]))
with open(P("results", "evaluation_folds.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(fo[0])); w.writeheader(); w.writerows(fo)

dups = [srt(v) for v in g_exact.values() if len(v) > 1]
fs = {k: collections.Counter(by[c]["behavior_change_category"] for c, _ in v) for k, v in folds.items()}
zero_l2 = [e["case_number"] for e in ex if e["same_mechanism_examples_available_L2"] == 0]
md = f"""# Evaluation split design for the repair experiments (RQ2–RQ4)

**Scope:** the 56 BEHAVIORAL cases in `results/final_classification_rule_based.csv` are the repair targets. These files decide which cases may be retrieved for each target. No fixes have been searched for or generated yet.

**Rule from the brief:** a target case's own fix must never be retrieved. Some benchmark entries are the same breakage under another case ID, and some projects contribute several updates of one dependency. Excluding only the case ID would still let the identical fix leak, so three exclusion levels are defined.

| Level | What is excluded for a target | Purpose |
|---|---|---|
| L1 | Exact duplicates (same project, dependency, old and new version) | Minimum to stop identical fixes leaking |
| **L2 (primary)** | L1 + every case of the same project **and** dependency | The same client code is usually repaired the same way for a neighbouring version, so this is the realistic "unseen project-dependency pair" setting |
| L3 (strict, sensitivity) | L2 + every case in the same mechanism family | Tests transfer when no repair of the same mechanism is available |

Exclusions apply to the whole retrieval pool (all 188 cases), whether or not a case is behavioral, so they stay valid if non-behavioral repairs are added to the knowledge base.

## Facts the design accounts for

- **Exact-duplicate groups:** {'; '.join(dups)}. Cases 32/54 and the five-case IDS junit-platform group were not flagged in the earlier audit.
- **Group sizes:** the 56 behavioral cases form {len(groups)} project-dependency groups. The largest are sign-maven-plugin/slf4j (8), recheck/slf4j, pay-adminusers/slf4j and jasmine/slf4j (7 each), and pay-cardid/dropwizard-sentry (5).
- **Cases with no same-mechanism example left under L2:** {len(zero_l2)} ({', '.join(zero_l2)}). These are the one-off mechanisms, plus families confined to a single project-dependency group (dropwizard-sentry config, H2, json-smart). Retrieval can only help them through other mechanisms, so report them separately in RQ2.
- **Under L3,** the 36 SLF4J cases have no SLF4J example to retrieve. L3 is the cleanest test of whether retrieval generalises beyond near-copies.

## Grouped folds (`evaluation_folds.csv`)

Use these only if a method needs tuning, such as prompt or retrieval settings. Tune on two folds, evaluate on the third, and rotate. A project-dependency group never spans folds.

| Fold | Cases | Behavior categories |
|---|---:|---|
""" + "\n".join(f"| {k} | {len(v)} | " + ", ".join(f"{c} {n}" for c, n in fs[k].most_common()) + " |" for k, v in folds.items()) + """

The PROVIDER_OR_IMPLEMENTATION_SELECTION category (SLF4J) cannot be balanced across folds without splitting projects, because the groups are large. Report per-fold and pooled results.

## Reporting rules

1. Report every RQ2/RQ3 success rate for L2 (primary). Also report L1 and L3, so the effect of near-duplicate leakage is visible.
2. Report results per mechanism family as well as per behavior category, because SLF4J is 36 of 56 cases.
3. A repair counts as a success only if the required tests pass **with the updated dependency still resolved**. Record `mvn dependency:tree` for every successful repair; the Case 14 repair log lacks this.
"""
open(P("results", "evaluation_split_design.md"), "w", encoding="utf-8").write(md)
print("groups", len(groups), "folds", {k: len(v) for k, v in folds.items()}, "dups", dups)
print("zero same-mechanism under L2:", zero_l2)
print("L2 pool sizes min/max", min(e["behavioral_pool_remaining_L2"] for e in ex), max(e["behavioral_pool_remaining_L2"] for e in ex))
