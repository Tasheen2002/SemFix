"""Evaluate retrieval before any LLM is used (handbook Phase 5.2).

Positives : the 56 KB cases, each queried with its own symptoms (leave-one-out, leakage level L2/L1/L3).
            A hit is a retrieved case with the same mechanism (SINGLETON never counts).
Negatives : kb/retrieval_negatives.json, hand-written breakages whose mechanism is NOT in the KB
            (7 hard, realistic Java ones + 3 easy). The gate should return nothing for them.
No-example: the positives whose mechanism has no example left after the exclusions (15 at L2). Ideally the gate
            returns nothing for them too, so the LLM is not shown a misleading fix.

Reports Hit@1, Hit@3 (of cases where a same-mechanism example exists), MRR, and for gated RRF a threshold sweep
with negative rejection and no-example rejection. Output: kb/retrieval_evaluation_v2.json
Usage: python -I eval_retrieval.py <research root>
"""
import itertools, json, os, sys

ROOT = os.path.abspath(sys.argv[1])
sys.path.insert(0, os.path.join(ROOT, "kb", "scripts"))
import retrieve  # noqa: E402

E = retrieve.load(ROOT)
IX = retrieve.Index(E, dense_model="sentence-transformers/all-MiniLM-L6-v2", root=ROOT)
NEG = json.load(open(os.path.join(ROOT, "kb", "retrieval_negatives.json"), encoding="utf-8"))


def as_query(n):
    g, a = n["dependency"].split(":")
    return dict(case_number=-1, leakage=dict(exclude_L1=[], exclude_L2=[], exclude_L3=[]),
                breakage=dict(dependency=n["dependency"], group_id=g, artifact_id=a, old_version=n["old_version"],
                              new_version=n["new_version"], version_update_type="", failing_test_classes=n["failing_test_classes"],
                              exception_types=n["exception_types"], error_lines=n["error_lines"], slf4j_console=[]))


def available(e, level, rw=True):
    ex = set(e["leakage"][f"exclude_{level}"]) | {e["case_number"]}
    return any(retrieve.same_mech(x["behavior"]["mechanism_family"], e["behavior"]["mechanism_family"])
               for x in E if x["case_number"] not in ex and (rw or x["fix"]["is_reference_answer"]))


def run(level, scorer, gate=None, rw=True, k=3):
    hit1 = hit3 = mrr = 0.0; n_avail = 0; noex_reject = n_noex = 0
    for e in E:
        top = IX.retrieve(e, level, 10, scorer, rw, True, gate)
        mech = [retrieve.same_mech(h["mechanism"], e["behavior"]["mechanism_family"]) for h in top]
        if available(e, level, rw):
            n_avail += 1
            hit1 += bool(mech[:1] and mech[0]); hit3 += any(mech[:k])
            mrr += next((1 / (r + 1) for r, m in enumerate(mech) if m), 0.0)
        else:
            n_noex += 1; noex_reject += (len(top) == 0)
    neg = [len(IX.retrieve(as_query(n), level, k, scorer, rw, True, gate)) == 0 for n in NEG]
    return dict(level=level, scorer=scorer, gate=gate, with_researcher_written=rw, cases=len(E), same_mechanism_available=n_avail,
                hit_at_1=round(hit1 / n_avail, 3) if n_avail else None, hit_at_3=round(hit3 / n_avail, 3) if n_avail else None,
                mrr=round(mrr / n_avail, 3) if n_avail else None,
                negative_rejection=round(sum(neg) / len(neg), 2), negative_rejection_hard=round(sum(x for x, n in zip(neg, NEG) if n["kind"] == "hard") / sum(1 for n in NEG if n["kind"] == "hard"), 2),
                no_example_cases=n_noex, no_example_rejection=round(noex_reject / n_noex, 2) if n_noex else None)


results = dict(scorers=[], gate_sweep=[])
print("Ungated scorers (L2, with researcher-written):")
for sc in ("bm25", "hybrid", "dense", "rrf"):
    r = run("L2", sc); results["scorers"].append(r)
    print(f"  {sc:7s} Hit@1 {r['hit_at_1']}  Hit@3 {r['hit_at_3']}  MRR {r['mrr']}  (of {r['same_mechanism_available']})  "
          f"neg-rejection {r['negative_rejection']}  no-example-rejection {r['no_example_rejection']}")

# What the dense / lexical scores look like for true matches vs. negatives (to choose gate thresholds from data)
pos_cos, pos_lex, neg_cos, neg_lex = [], [], [], []
for e in E:
    if available(e, "L2"):
        for h in IX.retrieve(e, "L2", 10, "rrf", True, True):
            if retrieve.same_mech(h["mechanism"], e["behavior"]["mechanism_family"]):
                pos_cos.append(h["cosine"]); pos_lex.append(h["lexical"]); break
for n in NEG:
    t = IX.retrieve(as_query(n), "L2", 1, "rrf", True, True)[0]
    neg_cos.append(t["cosine"]); neg_lex.append(t["lexical"])
results["score_ranges"] = dict(best_true_match_cosine=[min(pos_cos), max(pos_cos)], best_true_match_lexical=[min(pos_lex), max(pos_lex)],
                               top_negative_cosine=[min(neg_cos), max(neg_cos)], top_negative_lexical=[min(neg_lex), max(neg_lex)])
print("Score ranges:", json.dumps(results["score_ranges"]))

print("Gate sweep (RRF, L2): keep a candidate if cosine >= c OR lexical >= b")
for c, b in itertools.product([0.4, 0.5, 0.55, 0.6, 0.65, 0.7], [20, 30, 40, 50, 1e9]):
    r = run("L2", "rrf", dict(min_cosine=c, min_bm25=b)); results["gate_sweep"].append(r)
    print(f"  cos>={c:<5} lex>={'off' if b > 1e8 else b:<4}  Hit@3 {r['hit_at_3']}  MRR {r['mrr']}  neg-rej {r['negative_rejection']} "
          f"(hard {r['negative_rejection_hard']})  no-example-rej {r['no_example_rejection']}")
print(f"Chosen gate {retrieve.DEFAULT_GATE} (RRF) at every level, with / without researcher-written fixes:")
results["chosen_gate"] = []
for level in ("L1", "L2", "L3"):
    for rw in (True, False):
        r = run(level, "rrf", retrieve.DEFAULT_GATE, rw); results["chosen_gate"].append(r)
        print(f"  {level} rw={rw!s:5}  Hit@1 {r['hit_at_1']}  Hit@3 {r['hit_at_3']}  MRR {r['mrr']}  (of {r['same_mechanism_available']})  "
              f"neg-rej {r['negative_rejection']}  no-example-rej {r['no_example_rejection']} (of {r['no_example_cases']})")
json.dump(results, open(os.path.join(ROOT, "kb", "retrieval_evaluation_v2.json"), "w", encoding="utf-8"), indent=1)
