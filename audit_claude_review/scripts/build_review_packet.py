"""Build verification_plan/human_review_packet.md: one self-contained section per sampled case."""
import csv, os, subprocess, sys
ROOT = sys.argv[1]
A = lambda *a: os.path.join(ROOT, "audit_claude_review", *a)
sample = list(csv.DictReader(open(A("verification_plan", "human_sample.csv"), encoding="utf-8")))
final = {r["case_number"]: r for r in csv.DictReader(open(os.path.join(ROOT, "results", "final_classification_rule_based.csv"), encoding="utf-8"))}
audit = {r["case_number"]: r for r in csv.DictReader(open(A("claude_audit.csv"), encoding="utf-8"))}
plan = {}
for r in csv.DictReader(open(A("verification_plan", "control_plan.csv"), encoding="utf-8")):
    for n in r["cases"].split():
        plan.setdefault(n, r)

def condensed(n):
    out = subprocess.run([sys.executable, "-I", A("scripts", "condense.py"), A("digests"), n, n, "2200"], capture_output=True, text=True, encoding="utf-8").stdout
    keep = [l for l in out.splitlines() if l.startswith(("BRK ", "PRE status", "PRE agg", " CB ", " SF ", " ERR ", "   +", "   -", "DIFF", "archived"))]
    return "\n".join(l[:300] for l in keep[:22])

L = ["# Human review packet: 47 sample cases", "",
     "**For:** the human reviewer adjudicating the BUMP classification. **Time:** about 5–10 minutes per case.", "",
     "**What you're checking:** whether the proposed label follows from the evidence under the approved rules (`decision_rules.md`). You are not re-deciding the rules.", "",
     "**How:** read the evidence excerpt for each case and tick the checklist. Write your label in `human_sample.csv` (`human_label`, `human_confidence`, `human_notes`). Open the raw log only if the excerpt isn't enough; paths are listed for each case.", "",
     "**When you finish:** if you agree with every case, or the disagreements are resolved, ask Claude to copy the rule-based labels into `final_label`. If a disagreement exposes a wrong rule application, the whole group in `related_group` needs rechecking.", "",
     "## Contents", ""]
for s in sample:
    L.append(f"- [Case {s['case_number']}](#case-{s['case_number']}): {s['dependency']}, proposed **{final[s['case_number']]['rule_based_label']}**, {s['selected_because']}")
L.append("")
for s in sample:
    n = s["case_number"]; f = final[n]; a = audit[n]; p = plan.get(n, {})
    L += [f"---", "", f"## Case {n}", "",
          f"- **Project / update:** {s['project']} · `{s['dependency']}`",
          f"- **Why sampled:** {s['selected_because']}",
          f"- **Proposed label:** **{f['rule_based_label']}** by rule **{f['rule']}** ({f['rule_name']})" + (f", category {f['behavior_change_category']}" if f['behavior_change_category'] else ""),
          f"- **Codex label:** {f['codex_label']} · **Claude blind label:** {f['claude_blind_label']} · **Changes Codex's label:** {f['changes_codex_label']}",
          f"- **Baseline:** {a['baseline_outcome']}",
          f"- **Updated:** {a['updated_outcome']}", "",
          f"**Initiating cause (Claude):** {f['primary_cause']}", ""]
    if f["behavior_change"]:
        L += [f"**What changed:** {f['behavior_change']}", ""]
    if p:
        L += [f"**Group evidence ({p.get('status','')}):** {p.get('existing_evidence','')[:700]}", ""]
    if a["root_cause_comparison"] and not a["root_cause_comparison"].startswith("Agree"):
        L += [f"**Codex comparison:** {a['root_cause_comparison'][:700]}", ""]
    L += ["**Evidence excerpt** (from the original logs and archives):", "", "```", condensed(n), "```", "",
          f"**Paths:** {a['evidence_paths']}", "",
          "**Checklist**", "",
          "- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on (\"Could not initialize class\", an assertion on null output).",
          "- [ ] 2. Test counts match the Maven summary.",
          "- [ ] 3. Only the dependency version changed, or what else changed is noted.",
          "- [ ] 4. The control, probe or trace supports the label under the approved rule.",
          "- [ ] 5. Label recorded in `human_sample.csv`.", ""]
open(A("verification_plan", "human_review_packet.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print(len(sample), "cases;", sum(len(x) for x in L), "chars")
