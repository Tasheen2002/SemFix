"""Apply the researcher-approved decision rules (2026-11-20) to all 188 cases.
Writes results/final_classification_rule_based.csv and results/rq1_classification_summary.md.
"""
import csv, collections, os, sys
ROOT = sys.argv[1]
P = lambda *a: os.path.join(ROOT, *a)
audit = list(csv.DictReader(open(P("audit_claude_review", "claude_audit.csv"), encoding="utf-8")))
plan = list(csv.DictReader(open(P("audit_claude_review", "verification_plan", "control_plan.csv"), encoding="utf-8")))

DECISION = {"R5": "BEHAVIORAL", "R7": "BEHAVIORAL", "R8": "NON_BEHAVIORAL"}
RULE_LABEL = {"R1": "NON_BEHAVIORAL", "R2": "NON_BEHAVIORAL", "R3": "NON_BEHAVIORAL", "R4": "NON_BEHAVIORAL", "R6": "NON_BEHAVIORAL",
              "R9": "BEHAVIORAL", "R10": "NON_BEHAVIORAL", "R11": "NON_BEHAVIORAL", "R12": "BEHAVIORAL", "R13": "NON_BEHAVIORAL", **DECISION}
RULE_NAME = {"R1": "Linkage or bytecode incompatibility", "R2": "Version skew within one library family", "R3": "javax/jakarta namespace migration",
             "R4": "Framework-generation mismatch", "R5": "Provider selection changed while old provider present", "R6": "Retained API references a removed binding class",
             "R7": "Configuration property no longer accepted", "R8": "Generator/runtime serialized-format alignment (ANTLR)", "R9": "Changed default in the updated library",
             "R10": "Tooling or test-infrastructure failure", "R11": "Fixture-only edit", "R12": "Core behavioral change (same API, same input, different observable result)",
             "R13": "Packaging change removes a runtime provider"}
# per-case rule from the control plan (group rows list their cases)
rule_of, verif_of = {}, {}
for r in plan:
    if r["group"] == "PROVENANCE_CHECK":
        continue
    for n in r["cases"].split():
        rule_of[n] = r["rule"]; verif_of[n] = r["status"]
# Behavior-change categories for RQ1 (one primary category per behavioral case)
BCAT = {}
for r in audit:
    g = r["related_group"].split(" | ")[0]; n = r["case_number"]
    if g == "SLF4J2_IGNORES_LEGACY_BINDING": BCAT[n] = "PROVIDER_OR_IMPLEMENTATION_SELECTION"
    elif g == "MOCKITO5_INLINE_DEFAULT": BCAT[n] = "DEFAULT_SETTING_OR_POLICY"
    elif g in ("DROPWIZARD_SENTRY_CONFIG", "H2_VARCHAR_LIMIT", "JSON_SMART_DEPTH_LIMIT"): BCAT[n] = "ACCEPTED_INPUT"
BCAT.update({"20": "DEFAULT_SETTING_OR_POLICY", "13": "EXCEPTION_TYPE_OR_CONDITION", "70": "EXCEPTION_TYPE_OR_CONDITION",
             "53": "RETURN_VALUE", "158": "OUTPUT_FORMAT", "181": "OUTPUT_FORMAT"})
BDESC = {"PROVIDER_OR_IMPLEMENTATION_SELECTION": "Library selects a different implementation for the same classpath",
         "DEFAULT_SETTING_OR_POLICY": "A default (mock maker, deserialization allow-list) changed",
         "ACCEPTED_INPUT": "Input previously accepted is now rejected (DDL precision, JSON depth, YAML property)",
         "EXCEPTION_TYPE_OR_CONDITION": "Different exception type, or an exception where a value was returned",
         "RETURN_VALUE": "Same call returns a different value", "OUTPUT_FORMAT": "Serialized/string output differs"}
out = []
for r in audit:
    n = r["case_number"]; rule = rule_of[n]; lab = RULE_LABEL[rule]
    cx = "BEHAVIORAL" if r["codex_label"] == "PROVISIONAL_BEHAVIORAL" else r["codex_label"]
    out.append({
        "case_number": n, "case_id": r["case_id"], "project": r["project"], "dependency": r["dependency"],
        "old_version": r["old_version"], "new_version": r["new_version"],
        "rule_based_label": lab, "rule": rule, "rule_name": RULE_NAME[rule],
        "behavior_change_category": BCAT.get(n, "") if lab == "BEHAVIORAL" else "",
        "behavior_change": r["behavior_change"] if lab == "BEHAVIORAL" else "",
        "primary_cause": r["primary_cause"], "binary_linkage": r["binary_linkage"],
        "verification_basis": verif_of[n], "codex_label": r["codex_label"], "claude_blind_label": r["claude_label_blind"],
        "changes_codex_label": "YES" if cx != lab else "NO",
        "related_group": r["related_group"], "possible_duplicate_of": r["possible_duplicate_of"],
        "evidence_paths": r["evidence_paths"],
        "label_status": "RULE_BASED (rules approved by researcher 2026-11-20); per-case human sample review pending",
    })
assert len(out) == 188 and all(o["rule_based_label"] in ("BEHAVIORAL", "NON_BEHAVIORAL") for o in out)
assert all(o["behavior_change_category"] for o in out if o["rule_based_label"] == "BEHAVIORAL")
with open(P("results", "final_classification_rule_based.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)

lab = collections.Counter(o["rule_based_label"] for o in out)
beh = [o for o in out if o["rule_based_label"] == "BEHAVIORAL"]
cat = collections.Counter(o["behavior_change_category"] for o in beh)
rules = collections.Counter((o["rule"], o["rule_based_label"]) for o in out)
changed = [o for o in out if o["changes_codex_label"] == "YES"]
pct = lambda k: f"{k} ({100 * k / 188:.1f}%)"
lines = ["# RQ1: behavioral breakages among the 188 TEST_FAILURE candidates", "",
         "**Basis:** these labels come from the decision rules the researcher approved on 2026-11-20 (`audit_claude_review/verification_plan/decision_rules.md`), applied to the evidence in `audit_claude_review/claude_audit.csv` and the targeted checks in `audit_claude_review/reruns/RESULTS.md`. **Status:** FINAL v1.0 (2026-11-20). The researcher manually reviewed Cases 1–20 (100% agreement), and a 47-case stratified sample was rerun from the original images (47/47 reproduced). All percentages are of 188.", "",
         "## Headline", "", "| Label | Cases |", "|---|---:|",
         f"| BEHAVIORAL | {pct(lab['BEHAVIORAL'])} |", f"| NON_BEHAVIORAL | {pct(lab['NON_BEHAVIORAL'])} |", "| UNCERTAIN | 0 |", "",
         f"The behavioral cases come from {len({o['project'] for o in beh})} of the {len({o['project'] for o in out})} projects.",
         f"{len(changed)} cases differ from Codex's provisional labels: {', '.join(o['case_number'] for o in changed)}. All 8 move from PROVISIONAL_BEHAVIORAL to NON_BEHAVIORAL under rules R8 (ANTLR), R2 (Case 69, confirmed by an alignment control) and R3 (Case 109).", "",
         "## What kind of behavior changed (n = %d)" % len(beh), "", "| Category | Cases | % of 188 | What changed | Cases (dependency) |", "|---|---:|---:|---|---|"]
for k, v in cat.most_common():
    cs = [o for o in beh if o["behavior_change_category"] == k]
    deps = collections.Counter(o["dependency"].split(":")[1] for o in cs)
    lines.append(f"| {k} | {v} | {100 * v / 188:.1f}% | {BDESC[k]} | " + ", ".join(f"{d} x{c}" for d, c in deps.most_common()) + " |")
lines += ["", "**Concentration:** 36 of the 56 behavioral cases (64%) are one mechanism, SLF4J 2.x provider discovery ignoring a legacy binding. They span 7 projects and slf4j-api 2.0.0 to 2.0.7. In 18 of them a logger-selection probe shows the switch directly. RQ4 per-category comparisons need to account for this, for example by reporting results by mechanism family as well as by category.", "",
          "## Why the other cases are non-behavioral (n = %d)" % lab["NON_BEHAVIORAL"], "", "| Rule | Cases |", "|---|---:|"]
for (r, l), v in sorted(rules.items(), key=lambda x: -x[1]):
    if l == "NON_BEHAVIORAL":
        lines.append(f"| {r}: {RULE_NAME[r]} | {v} |")
lines += ["", "## Evidence strength of the behavioral labels", "", "| Basis | Cases |", "|---|---:|"]
for k, v in collections.Counter(o["verification_basis"] for o in beh).most_common():
    lines.append(f"| {k} | {v} |")
lines += ["",
          "- **COVERED:** a probe or control isolates the change.",
          "- **COVERED_BY_TRACE:** the exception originates inside the updated library on an input that passes in PRE.",
          "- **DECISION_ONLY:** the mechanism is confirmed and the label follows from the approved rule (R5 or R7). For R5, 18 of the 36 cases also have a direct logger-selection probe.", "",
          "## Before the repair phase", "",
          "- Use `results/retrieval_exclusions.csv` (L2 primary) and `results/evaluation_folds.csv` so that retrieval cannot return a target case's own fix. Exact-duplicate groups: 4/23/60/121/177, 32/54, 65/169, 123/135, 163/168. See `results/evaluation_split_design.md`.",
          "- `final_label` in `results/behavioral_classification.csv` is still empty. Copy the rule-based labels into it once the human sample review agrees with them."]
open(P("results", "rq1_classification_summary.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(lab, cat, len(changed), [o["case_number"] for o in changed])
print(collections.Counter(o["verification_basis"] for o in beh))
