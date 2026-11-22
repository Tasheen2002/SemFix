"""Apply evidence-backed corrections from the Claude AI second review to results/behavioral_classification.csv.

Only factual fields (test counts) and the notes column are edited. Labels, reviewer fields and
final_label are never changed. Each edited row gets an appended note beginning
"[AI second review (Claude), 2026-11-20]". Untouched lines are verified byte-identical.

Usage: python -I apply_corrections.py <workspace_root> [--dry-run]
"""
import csv, io, json, os, sys

ROOT = sys.argv[1]
DRY = "--dry-run" in sys.argv
PATH = os.path.join(ROOT, "results", "behavioral_classification.csv")
TAG = "[AI second review (Claude), 2026-11-20]"
AUDIT = "audit_claude_review/claude_audit.csv"

cands = [r["case_id"] for r in csv.DictReader(open(os.path.join(ROOT, "results", "test_failure_candidates.csv"), encoding="utf-8"))]
cid = lambda n: cands[n - 1]

# field corrections: case number -> {field: (expected_old, new)}
FIELD_FIX = {
    12: {"pre_tests": ("726", "757")},
    9: {"pre_tests": ("510", "1114")},
    10: {"pre_tests": ("12", "32"), "breaking_tests": ("12", "18")},
    14: {"pre_tests": ("32", "190"), "breaking_tests": ("32", "52")},
}
# text corrections inside notes: case -> [(old, new)]
NOTE_TEXT_FIX = {
    12: [("The complete PRE build runs 726 tests successfully.", "The complete PRE build runs 757 tests successfully.")],
}
NOTE_APPEND = {
    12: f"{TAG} Count correction: the original PRE log (logs/batch_triage/1266a8c8_pre.log line 423) reports 'Tests run: 757, Failures: 0, Errors: 0, Skipped: 0' with BUILD SUCCESS. pre_tests was recorded as 726 (the BREAKING count). Corrected to 757. BREAKING 726 is correct; class-initialisation failures hide 31 tests.",
    9: f"{TAG} Count scope: pre_tests 510 was the junit-quickcheck-core module only. The other rows record whole-build totals, so pre_tests is now 1114 (core 510 + generators 561 + guava 11 + examples 32, from the original PRE log). breaking_tests stays 510 because generators/guava/examples were SKIPPED after core failed.",
    10: f"{TAG} Count scope: 12/12 were the messaging module only. Whole-build totals from the original logs: PRE 32 tests across 8 modules; BREAKING 18 (core 6 + messaging 12), with clearinghouse/broker/vocol/paris/appstore SKIPPED. Failures 1 / errors 5 unchanged.",
    14: f"{TAG} Count scope: 32/32 were GeoStore - Core - Persistence only. Whole-build totals from the original logs: PRE 190 tests; BREAKING 52 (Model 9 + Security 11 + Persistence 32 per reactor order), with downstream modules SKIPPED. Errors 22 unchanged. The repair log logs/case14_clob_fixed.log shows a full-reactor BUILD SUCCESS with 190 tests run and 36 skipped.",
    17: f"{TAG} Provenance: pre_log/breaking_log and the counts (4104 / 11) come from diagnostic runs (fixed-date source control on PRE; BREAKING scoped to SourceInActivitiesTest), not the original BUMP runs. Original runs (logs/batch_triage/18102f7a_*.log): PRE BUILD FAILURE (exit 1; last module 116 tests, 1 date-sensitive failure); BREAKING stopped by the reviewer (exit 143, logs/case17_evidence/breaking_interruption.json) with no Maven summary. pre_build_status=SUCCESS describes only the control run. The label is unaffected (JacksonFeature linkage), but this row is not a clean original-baseline TEST_FAILURE.",
}
DISPUTE = {
    49: "ANTLR ATN v3 vs runtime 4.10.1", 67: "ANTLR ATN v3 vs runtime 4.10", 112: "ANTLR ATN v3 vs runtime 4.12.0",
    127: "ANTLR ATN v3 vs runtime 4.11.1", 140: "ANTLR ATN v3 vs runtime 4.10.1", 188: "ANTLR ATN v3 vs runtime 4.10",
    69: "GraalJS scriptengine 22.1.0 vs retained js 22.0.0 option skew",
    109: "Guice 7 javax.inject qualifier support removed",
}
for n, why in DISPUTE.items():
    NOTE_APPEND[n] = (f"{TAG} Label disputed: blind AI second review assigned NON_BEHAVIORAL ({why}); "
                      f"treated as a taxonomy-boundary case needing human adjudication. See {AUDIT}.")

raw = open(PATH, encoding="utf-8", newline="").read()
lines = raw.split("\r\n")
header = next(csv.reader([lines[0]]))
idx = {h: i for i, h in enumerate(header)}
targets = {cid(n): n for n in set(FIELD_FIX) | set(NOTE_APPEND) | set(NOTE_TEXT_FIX)}
changes, seen = [], set()


def ser(fields):
    b = io.StringIO(newline="")
    csv.writer(b, lineterminator="").writerow(fields)
    return b.getvalue()


for i, line in enumerate(lines):
    if not line or i == 0:
        continue
    f = next(csv.reader([line]))
    if f[0] not in targets:
        continue
    assert ser(f) == line, f"line {i} would not round-trip exactly"
    n = targets[f[0]]
    seen.add(n)
    rec = {"case": n, "case_id": f[0], "changes": []}
    for fld, (old, new) in FIELD_FIX.get(n, {}).items():
        assert f[idx[fld]] == old, (n, fld, f[idx[fld]], old)
        f[idx[fld]] = new
        rec["changes"].append({"field": fld, "old": old, "new": new})
    notes = f[idx["notes"]]
    if TAG in notes:
        print(f"case {n}: already corrected, skipping")
        seen.add(n)
        continue
    for old, new in NOTE_TEXT_FIX.get(n, []):
        assert old in notes, (n, old)
        notes = notes.replace(old, new)
        rec["changes"].append({"field": "notes(text)", "old": old, "new": new})
    if n in NOTE_APPEND:
        notes = (notes + " " if notes else "") + NOTE_APPEND[n]
        rec["changes"].append({"field": "notes(append)", "new": NOTE_APPEND[n]})
    f[idx["notes"]] = notes
    lines[i] = ser(f)
    changes.append(rec)

missing = set(targets.values()) - seen
assert not missing, f"rows not found: {missing}"
new = "\r\n".join(lines)
# verify: every line not targeted is byte-identical
old_lines, new_lines = raw.split("\r\n"), new.split("\r\n")
assert len(old_lines) == len(new_lines)
diff = [i for i, (a, b) in enumerate(zip(old_lines, new_lines)) if a != b]
assert all(next(csv.reader([old_lines[i]]))[0] in targets for i in diff)
print(f"{len(changes)} rows to change; {len(diff)} lines differ; all other lines byte-identical")
if not DRY:
    open(PATH, "w", encoding="utf-8", newline="").write(new)
    log = os.path.join(ROOT, "audit_claude_review", "corrections_applied.json")
    json.dump(changes, open(log, "w", encoding="utf-8"), indent=1)
    print("written; change log:", log)
