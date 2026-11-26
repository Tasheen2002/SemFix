"""Anti-leakage gate for the knowledge base and retrieval (handbook Phase 4.3, adapted to Protocol 2).

Run before every experiment:   .venv/Scripts/python -m pytest tests/test_no_leakage.py -v
A failure here means experiment results would be invalid: a case could see its own answer.

Our KB is built from the BUMP cases themselves (handbook "Protocol 2", project-level split), so leakage is
controlled at query time. These tests prove it for EVERY case, level and switch setting:
  R1  a case never retrieves itself
  R2  never its exact duplicates, nor any case from its own project (handbook rule R2)
  R3  at level L3, never a case with the same mechanism (except the SINGLETON bucket of unrelated one-offs)
  R4  the indexed retrieval text contains no fix information (patch lines, fix explanation, fix commit)
  R5  the query is built from symptoms only (no classification fields)
  R6  the KB still matches its frozen fingerprint (kb/FROZEN.json)
  R7  include_researcher_written=False really removes researcher-written fixes
"""
import csv, json, os, sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "kb", "scripts"))
import retrieve  # noqa: E402

E = retrieve.load(ROOT)
BY = {e["case_number"]: e for e in E}
IX = retrieve.Index(E)
LEVELS = ("L1", "L2", "L3")
DUP_GROUPS = [{4, 23, 60, 121, 177}, {32, 54}, {65, 169}, {123, 135}, {163, 168}]   # classification v1.0 (all 188)


def all_hits(e, level, rw):
    return IX.retrieve(e, level=level, k=len(E), include_researcher_written=rw, diversify=False)


@pytest.mark.parametrize("level", LEVELS)
@pytest.mark.parametrize("rw", [True, False])
def test_r1_never_retrieves_itself(level, rw):
    bad = [e["case_number"] for e in E if any(h["case_number"] == e["case_number"] for h in all_hits(e, level, rw))]
    assert not bad, f"R1 violated at {level}: cases retrieve themselves: {bad}"


@pytest.mark.parametrize("level", LEVELS)
def test_r2_no_duplicates_and_no_same_project(level):
    bad = []
    for e in E:
        n = e["case_number"]
        dups = set().union(*[g for g in DUP_GROUPS if n in g]) - {n}
        for h in all_hits(e, level, True):
            m = h["case_number"]
            if m in dups:
                bad.append((n, m, "duplicate"))
            if level in ("L2", "L3") and BY[m]["project"] == e["project"]:
                bad.append((n, m, "same project"))
    assert not bad, f"R2 violated at {level}: {bad[:10]}"


def test_r3_strict_level_excludes_same_mechanism():
    bad = [(e["case_number"], h["case_number"]) for e in E for h in all_hits(e, "L3", True)
           if h["mechanism"] == e["behavior"]["mechanism_family"] and h["mechanism"] != "SINGLETON"]
    assert not bad, f"R3 violated: same-mechanism cases retrieved at L3: {bad[:10]}"


def test_r4_retrieval_text_has_no_fix_information():
    bad = []
    for e in E:
        text = e["retrieval_text"]
        fx = e["fix"]
        added = [l[1:].strip() for l in fx["patch"].splitlines() if l.startswith("+") and not l.startswith("+++")]
        added = [l for l in added if len(l) >= 25]          # distinctive added lines only
        if any(l in text for l in added):
            bad.append((e["case_number"], "patch line"))
        if fx["explanation"] and fx["explanation"][:60] in text:
            bad.append((e["case_number"], "fix explanation"))
        if fx["developer_commit"] and fx["developer_commit"][:10] in text:
            bad.append((e["case_number"], "fix commit"))
    assert not bad, f"R4 violated: fix information is indexed: {bad[:10]}"


def test_r5_query_uses_symptoms_only():
    for e in E:
        q = retrieve.query_text(e)
        assert e["behavior"]["description"] not in q, f"case {e['case_number']}: behavior description in query"
        assert e["behavior"]["category"] not in q, f"case {e['case_number']}: category in query"
        assert e["fix"]["explanation"][:40] not in q, f"case {e['case_number']}: fix explanation in query"


def test_r6_kb_matches_frozen_fingerprint():
    frozen = retrieve.verify_frozen(ROOT)
    if frozen is None:
        pytest.skip("KB not frozen yet (run kb/scripts/freeze_kb.py before the experiments)")
    assert frozen["entries"] == len(E) == 56


def test_r7_switch_removes_researcher_written():
    rw_cases = {e["case_number"] for e in E if not e["fix"]["is_reference_answer"]}
    assert len(rw_cases) == 28
    bad = [(e["case_number"], h["case_number"]) for e in E for h in all_hits(e, "L1", False) if h["case_number"] in rw_cases]
    assert not bad, f"R7 violated: researcher-written fixes retrieved with the switch off: {bad[:10]}"


def test_exclusion_lists_match_frozen_split_files():
    rows = {int(r["case_number"]): r for r in csv.DictReader(open(os.path.join(
        ROOT, "results", "classification_v1.0", "retrieval_exclusions.csv"), encoding="utf-8"))}
    for e in E:
        r = rows[e["case_number"]]
        l2 = sorted({int(x) for x in (r["exclude_L1_duplicates"] + " " + r["exclude_L2_same_project_dependency"]).split()})
        assert e["leakage"]["exclude_L2"] == l2, f"case {e['case_number']}: L2 list differs from retrieval_exclusions.csv"
