"""Option A (approved by the researcher 2026-11-20): correct Codex's label for 8 cases to NON_BEHAVIORAL
in results/behavioral_classification.csv, the matching append scripts and review files.
Labels in review_status / reviewer_* / final_label are not touched. Byte-level edits preserve line endings.
"""
import csv, io, json, os, sys, hashlib
ROOT = sys.argv[1]
P = lambda *a: os.path.join(ROOT, *a)
DATE = "2026-11-20"
TAG = f"[Label corrected {DATE}, approved by the researcher (Option A)]"
cands = [r["case_id"] for r in csv.DictReader(open(P("results", "test_failure_candidates.csv"), encoding="utf-8"))]
ANTLR = "Rule R8 (approved {d}): an ANTLR runtime rejecting serialized ATN data produced by an older generator is generator/runtime alignment, fixed by regenerating the parser with a matching tool. Mechanism unchanged and confirmed (lexer probes in cases 112, 127, 140, 188).".format(d=DATE)
WHY = {
    49: ANTLR, 67: ANTLR, 112: ANTLR, 127: ANTLR, 140: ANTLR, 188: ANTLR,
    69: (f"Rule R2 (approved {DATE}): version skew between two GraalJS artifacts. Control run: setting the retained org.graalvm.js:js 22.0.0 -> 22.1.0, "
         "with js-scriptengine 22.1.0 kept, gives 80 tests, 0 failures, 0 errors (audit_claude_review/reruns/case69_graaljs_alignment_control.log)."),
    109: (f"Rule R3 (approved {DATE}): javax->jakarta namespace migration, labelled NON_BEHAVIORAL consistently with cases 83, 93, 164 and 180. "
          "Mechanism unchanged: Guice 7 no longer recognises @javax.inject.Qualifier on Sisu @Parameters (AnnotationCompatibilityProbe)."),
}
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
log = {"date": DATE, "csv_sha256_before": sha(P("results", "behavioral_classification.csv")), "cases": {}}

# 1. classification CSV (line-level)
path = P("results", "behavioral_classification.csv")
raw = open(path, encoding="utf-8", newline="").read(); lines = raw.split("\r\n")
hdr = next(csv.reader([lines[0]])); ix = {h: i for i, h in enumerate(hdr)}
def ser(f):
    b = io.StringIO(newline=""); csv.writer(b, lineterminator="").writerow(f); return b.getvalue()
target = {cands[n - 1]: n for n in WHY}
changed = 0
for i, l in enumerate(lines[1:], 1):
    if not l: continue
    f = next(csv.reader([l]))
    if f[0] not in target: continue
    n = target[f[0]]
    if TAG in f[ix["notes"]]:
        print("already applied", n); continue
    assert ser(f) == l and f[ix["behavioral_status"]] == "PROVISIONAL_BEHAVIORAL", n
    old = {k: f[ix[k]] for k in ("behavioral_status", "behavior_change_type")}
    f[ix["behavioral_status"]] = "NON_BEHAVIORAL"
    f[ix["behavior_change_type"]] = ""
    f[ix["behavior_description"]] += f" {TAG} Originally recorded by Codex as PROVISIONAL_BEHAVIORAL/OTHER_BEHAVIORAL_CHANGE; reclassified NON_BEHAVIORAL. {WHY[n]}"
    f[ix["notes"]] += f" {TAG} behavioral_status PROVISIONAL_BEHAVIORAL -> NON_BEHAVIORAL; behavior_change_type OTHER_BEHAVIORAL_CHANGE -> (empty). See audit_claude_review/CHANGELOG.md."
    lines[i] = ser(f); changed += 1
    log["cases"][n] = {"case_id": f[0], "old": old, "new": {"behavioral_status": "NON_BEHAVIORAL", "behavior_change_type": ""}, "reason": WHY[n]}
new = "\r\n".join(lines)
diff = [i for i, (a, b) in enumerate(zip(raw.split("\r\n"), lines)) if a != b]
assert len(diff) == changed and all(next(csv.reader([raw.split("\r\n")[i]]))[0] in target for i in diff)
open(path, "w", encoding="utf-8", newline="").write(new)
log["csv_sha256_after"] = sha(path)

# 2. append scripts (keep CRLF)
for n in WHY:
    sp = P("scripts", f"append_case_{n}.py"); b = open(sp, "rb").read()
    if b"Label corrected" in b: continue
    b2 = b.replace(b"'behavioral_status': 'PROVISIONAL_BEHAVIORAL',", f"'behavioral_status': 'NON_BEHAVIORAL',  # {TAG} was PROVISIONAL_BEHAVIORAL".encode())
    b2 = b2.replace(b"'behavior_change_type': 'OTHER_BEHAVIORAL_CHANGE',", b"'behavior_change_type': '',  # was OTHER_BEHAVIORAL_CHANGE")
    assert b2.count(b"Label corrected") == 1 and b"was OTHER_BEHAVIORAL_CHANGE" in b2, n
    open(sp, "wb").write(b2)

# 3. review files: dated addendum, original text untouched
for n in WHY:
    rp = P("results", f"case{n}_review.md")
    if not os.path.exists(rp): continue
    b = open(rp, "rb").read()
    if b"Label correction (" in b: continue
    nl = "\r\n" if b"\r\n" in b else "\n"
    add = nl.join(["", "", f"## Label correction ({DATE})", "",
                   "This addendum was added after the AI second review and the researcher's rule decisions. The assessment above is Codex's original text and is unchanged.", "",
                   "- Previous label: PROVISIONAL_BEHAVIORAL (OTHER_BEHAVIORAL_CHANGE)",
                   "- Corrected label: **NON_BEHAVIORAL**",
                   f"- Reason: {WHY[n]}",
                   "- Records: `results/behavioral_classification.csv` (notes), `audit_claude_review/CHANGELOG.md`, `results/final_classification_rule_based.csv`.", ""])
    open(rp, "wb").write(b.rstrip(b"\r\n") + add.encode("utf-8"))
json.dump(log, open(P("audit_claude_review", "option_a_changes.json"), "w", encoding="utf-8"), indent=1)
print("rows changed:", changed)
