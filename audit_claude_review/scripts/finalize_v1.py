"""Finalize the classification as version 1.0 (approved by the researcher 2026-11-20).
- results/behavioral_classification.csv: final_label for all 188 rows; reviewer_1_label for 15-20 (researcher's
  statement that they reviewed and agree); review_status=FINAL_V1; tagged note. reviewer_2_label left empty
  (the second review was by AI, recorded in audit_claude_review/, not as a human reviewer).
- results/final_classification_rule_based.csv: human_reviewed + label_status columns.
- results/classification_v1.0/: frozen copies, SHA-256 manifest, agreement statistics, README.
"""
import csv, hashlib, io, json, os, shutil, sys
ROOT = sys.argv[1]; DATE = "2026-11-20"
P = lambda *a: os.path.join(ROOT, *a)
TAG = f"[FINAL v1.0, {DATE}]"
cands = [r["case_id"] for r in csv.DictReader(open(P("results", "test_failure_candidates.csv"), encoding="utf-8"))]
num = {c: i + 1 for i, c in enumerate(cands)}
fin_rows = list(csv.DictReader(open(P("results", "final_classification_rule_based.csv"), encoding="utf-8")))
fin = {r["case_id"]: r for r in fin_rows}
HUMAN_RECORDED = set(range(1, 15)); HUMAN_STATED = set(range(15, 21))

# 1. classification CSV, line-level
path = P("results", "behavioral_classification.csv")
raw = open(path, encoding="utf-8", newline="").read(); lines = raw.split("\r\n")
hdr = next(csv.reader([lines[0]])); ix = {h: i for i, h in enumerate(hdr)}
def ser(f):
    b = io.StringIO(newline=""); csv.writer(b, lineterminator="").writerow(f); return b.getvalue()
human = {}
done = 0
for i, l in enumerate(lines[1:], 1):
    if not l: continue
    f = next(csv.reader([l])); assert ser(f) == l
    if TAG in f[ix["notes"]]: done += 1; continue
    n = num[f[0]]; lab = fin[f[0]]["rule_based_label"]; rule = fin[f[0]]["rule"]
    norm = lambda s: "BEHAVIORAL" if s in ("PROVISIONAL_BEHAVIORAL", "BEHAVIORAL") else s
    if n in HUMAN_RECORDED:
        human[n] = norm(f[ix["reviewer_1_label"]]); basis = "researcher's manual review (recorded reviewer_1_label)"
    elif n in HUMAN_STATED:
        assert not f[ix["reviewer_1_label"]]
        f[ix["reviewer_1_label"]] = lab; human[n] = lab
        basis = f"researcher's manual review (reviewer_1_label recorded {DATE} from the researcher's statement that cases 15-20 were reviewed and agree)"
    else:
        basis = "approved decision rules + evidence; AI second review; 47-case rerun sample verified"
    f[ix["final_label"]] = lab
    f[ix["review_status"]] = "FINAL_V1"
    f[ix["notes"]] += f" {TAG} final_label={lab} by rule {rule}; basis: {basis}. reviewer_2_label left empty: the second review was an AI review (audit_claude_review/)."
    lines[i] = ser(f); done += 1
assert done == 188
open(path, "w", encoding="utf-8", newline="").write("\r\n".join(lines))
rows = list(csv.DictReader(open(path, encoding="utf-8")))
assert all(r["final_label"] in ("BEHAVIORAL", "NON_BEHAVIORAL") for r in rows) and len(rows) == 188
assert all(r["final_label"] == fin[r["case_id"]]["rule_based_label"] for r in rows)

# 2. final_classification_rule_based.csv: provenance columns
for r in fin_rows:
    n = int(r["case_number"])
    r["human_reviewed"] = "YES (recorded)" if n in HUMAN_RECORDED else ("YES (researcher statement)" if n in HUMAN_STATED else "NO")
    r["label_status"] = f"FINAL v1.0 ({DATE}): rules approved by researcher; " + ("human-reviewed" if n <= 20 else "rule-based, AI-verified")
with open(P("results", "final_classification_rule_based.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(fin_rows[0])); w.writeheader(); w.writerows(fin_rows)

# 3. agreement statistics
audit = {r["case_number"]: r for r in csv.DictReader(open(P("audit_claude_review", "claude_audit.csv"), encoding="utf-8"))}
norm = lambda s: "BEHAVIORAL" if s in ("PROVISIONAL_BEHAVIORAL", "BEHAVIORAL") else s
def kappa(a, b):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
    cats = set(a) | set(b); pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return po, (po - pe) / (1 - pe) if pe < 1 else 1.0
ks = [str(i) for i in range(1, 189)]
codex = [norm(audit[k]["codex_label"]) for k in ks]; blind = [audit[k]["claude_label_blind"] for k in ks]
final = [fin[cands[int(k) - 1]]["rule_based_label"] for k in ks]
hk = [str(k) for k in sorted(human)]
stats = {
    "n": 188,
    "final_counts": {l: final.count(l) for l in ("BEHAVIORAL", "NON_BEHAVIORAL")},
    "codex_original_counts": {l: codex.count(l) for l in ("BEHAVIORAL", "NON_BEHAVIORAL")},
    "claude_blind_counts": {l: blind.count(l) for l in ("BEHAVIORAL", "NON_BEHAVIORAL")},
    "codex_original_vs_claude_blind": dict(zip(("agreement", "cohen_kappa"), kappa(codex, blind))),
    "codex_original_vs_final": dict(zip(("agreement", "cohen_kappa"), kappa(codex, final))),
    "claude_blind_vs_final": dict(zip(("agreement", "cohen_kappa"), kappa(blind, final))),
    "human_cases": [int(k) for k in hk],
    "human_vs_final_agreement": sum(human[int(k)] == final[int(k) - 1] for k in hk) / len(hk),
    "human_vs_codex_original_agreement": sum(human[int(k)] == codex[int(k) - 1] for k in hk) / len(hk),
    "human_vs_claude_blind_agreement": sum(human[int(k)] == blind[int(k) - 1] for k in hk) / len(hk),
    "note": "Use codex_original (64/124) for inter-rater statistics; the corrected file no longer shows Codex's original labels. Human labels: cases 1-14 recorded in the pilot; 15-20 recorded from the researcher's statement. All 8 disputed cases fall outside the human-reviewed set and were decided by researcher-approved rules (R8, R2, R3).",
}

# 4. freeze
out = P("results", "classification_v1.0"); os.makedirs(out, exist_ok=True)
for fn in ("behavioral_classification.csv", "final_classification_rule_based.csv", "rq1_classification_summary.md",
           "retrieval_exclusions.csv", "evaluation_folds.csv", "evaluation_split_design.md", "test_failure_candidates.csv"):
    shutil.copy2(P("results", fn), os.path.join(out, fn))
shutil.copy2(P("audit_claude_review", "verification_plan", "decision_rules.md"), os.path.join(out, "decision_rules.md"))
json.dump(stats, open(os.path.join(out, "agreement_statistics.json"), "w", encoding="utf-8"), indent=1)
f3 = lambda d: f"{d['agreement']*100:.1f}% (κ = {d['cohen_kappa']:.3f})"
readme = f"""# Classification v1.0 (frozen {DATE})

This is the final classification of the 188 BUMP TEST_FAILURE candidates. Do not edit these files; later changes should produce v1.1 or later with a change note.

| Label | Cases | % of 188 |
|---|---:|---:|
| BEHAVIORAL | {stats['final_counts']['BEHAVIORAL']} | {stats['final_counts']['BEHAVIORAL']/1.88:.1f}% |
| NON_BEHAVIORAL | {stats['final_counts']['NON_BEHAVIORAL']} | {stats['final_counts']['NON_BEHAVIORAL']/1.88:.1f}% |

## How the labels were established

1. **Codex first review:** provisional labels, 64 BEHAVIORAL and 124 NON_BEHAVIORAL.
2. **Claude AI second review:** blind, evidence-only pass. 56 BEHAVIORAL and 132 NON_BEHAVIORAL; labels frozen and hashed before comparison.
3. **Factual corrections:** Cases 9, 10, 12, 14 and 17 (counts and provenance), plus 11 targeted checks. Two of the checks were single-change controls (Cases 30 and 69).
4. **Rules approved by the researcher** (`decision_rules.md`): R5 SLF4J provider selection = BEHAVIORAL; R7 rejected configuration property = BEHAVIORAL; R8 ANTLR format alignment = NON_BEHAVIORAL; R3 javax/jakarta (including Case 109) = NON_BEHAVIORAL.
5. **Rerun verification:** the 47-case stratified sample, rerun from the original images; 47/47 reproduced.
6. **Human review:** the researcher manually reviewed Cases 1–20. All 20 agree with the final labels.

## Agreement (n = 188 unless stated)

| Pair | Agreement |
|---|---|
| Codex original vs Claude blind | {f3(stats['codex_original_vs_claude_blind'])} |
| Codex original vs final | {f3(stats['codex_original_vs_final'])} |
| Claude blind vs final | {f3(stats['claude_blind_vs_final'])} |
| Human (Cases 1–20) vs final | {stats['human_vs_final_agreement']*100:.0f}% |
| Human (Cases 1–20) vs Codex original | {stats['human_vs_codex_original_agreement']*100:.0f}% |

## Limitations to report

- The human review covers Cases 1–20. Cases 1–14 were recorded during the pilot; Cases 15–20 were recorded on {DATE} from the researcher's statement.
- The 8 cases where Codex and Claude disagreed (49, 67, 69, 109, 112, 127, 140, 188) were settled by researcher-approved rules, not by per-case human review. Case 69 is also backed by a control run.
- The second review was done by an AI. `reviewer_2_label` is therefore empty, and the AI evidence is in `audit_claude_review/`.

## Files

| File | Contents |
|---|---|
| `behavioral_classification.csv` | Master file; `final_label` filled, `review_status=FINAL_V1` |
| `final_classification_rule_based.csv` | Per-case rule, behavior category, evidence basis, human-review flag, related group, duplicates |
| `decision_rules.md` | The approved rules |
| `rq1_classification_summary.md` | RQ1 results |
| `retrieval_exclusions.csv`, `evaluation_folds.csv`, `evaluation_split_design.md` | Leakage-safe splits for RQ2–RQ4 |
| `agreement_statistics.json` | Agreement statistics |
| `SHA256SUMS.txt` | Hashes of every frozen file |
"""
open(os.path.join(out, "README.md"), "w", encoding="utf-8").write(readme)
with open(os.path.join(out, "SHA256SUMS.txt"), "w", encoding="utf-8", newline="\n") as fh:   # LF, so `sha256sum -c` works
    for fn in sorted(os.listdir(out)):
        if fn != "SHA256SUMS.txt":
            fh.write(f"{hashlib.sha256(open(os.path.join(out, fn), 'rb').read()).hexdigest()}  {fn}\n")
print(json.dumps({k: v for k, v in stats.items() if k != "human_cases"}, indent=1))
