"""Leakage-safe retrieval over the knowledge base (kb/entries.jsonl).

Query = only what a NEW breakage shows in its build log: dependency, versions, failing test classes, exception
types, error lines, SLF4J console lines. (No classification fields: a new case is not classified yet.)
Documents = the KB entries' retrieval_text (symptoms + behavior description; fix text is not indexed).

Scorers:
  bm25    : lexical BM25 (k1=1.2, b=0.75) over identifier-aware tokens
  hybrid  : bm25 + structured boosts for the same dependency group (+3) and the same artifact (+2)
Results are diversified by default: at most one entry per project-dependency group.
Evaluation: "same mechanism" never counts for the SINGLETON family (it groups unrelated one-off mechanisms).
  (an embedding scorer can be added later; `score()` is the single plug-in point)
Leakage: for target case T, entries in T's exclusion list at level L1/L2/L3 are removed, and T itself always.
Researcher-written fixes are retrievable only with include_researcher_written=True.

CLI:
  python -I retrieve.py <root> --case N [--level L2] [--k 3] [--scorer hybrid] [--no-researcher-written]
  python -I retrieve.py <root> --evaluate      (retrieval quality for all 56 cases, all levels/scorers)
"""
import argparse, json, math, os, re, sys
from collections import Counter

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."


def kb_fingerprint(root):
    """SHA-256 of kb/entries.jsonl (recorded with every experiment run)."""
    import hashlib
    return hashlib.sha256(open(os.path.join(root, "kb", "entries.jsonl"), "rb").read()).hexdigest()


def verify_frozen(root):
    """Return the frozen KB record; raise if the KB is frozen and entries.jsonl no longer matches it."""
    path = os.path.join(root, "kb", "FROZEN.json")
    if not os.path.exists(path):
        return None
    frozen = json.load(open(path, encoding="utf-8"))
    actual = kb_fingerprint(root)
    if actual != frozen["entries_sha256"]:
        raise RuntimeError(f"kb/entries.jsonl changed after the freeze ({frozen['version']}): "
                           f"expected {frozen['entries_sha256'][:16]}, found {actual[:16]}")
    return frozen


def load(root):
    verify_frozen(root)
    return [json.loads(l) for l in open(os.path.join(root, "kb", "entries.jsonl"), encoding="utf-8")]


def tokens(text):
    out = []
    for t in re.findall(r"[A-Za-z_][\w$.]*|\d+(?:\.\d+)*", text or ""):
        low = t.lower()
        out.append(low)
        if "." in t:                                        # org.slf4j.helpers.NOPLogger -> parts too
            out += [p.lower() for p in t.split(".") if p]
        out += [p.lower() for p in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])", t) if len(p) > 2]   # camelCase parts
    return out


def query_text(e):
    b = e["breakage"]
    return " ".join([b["dependency"], b["group_id"], b["artifact_id"], f"{b['old_version']} -> {b['new_version']}", b["version_update_type"],
                     " ".join(b["failing_test_classes"]), " ".join(b["exception_types"]), " ".join(b["error_lines"]), " ".join(b["slf4j_console"])])


class Index:
    def __init__(self, entries):
        self.entries = entries
        self.docs = [Counter(tokens(e["retrieval_text"])) for e in entries]
        self.len = [sum(d.values()) for d in self.docs]
        self.avg = sum(self.len) / len(self.len)
        df = Counter(t for d in self.docs for t in d)
        n = len(entries)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def bm25(self, q, i, k1=1.2, b=0.75):
        d, s = self.docs[i], 0.0
        for t in set(q):
            if t in d:
                tf = d[t]
                s += self.idf[t] * tf * (k1 + 1) / (tf + k1 * (1 - b + b * self.len[i] / self.avg))
        return s

    def score(self, query_entry, i, scorer):
        q = tokens(query_text(query_entry))
        s = self.bm25(q, i)
        if scorer == "hybrid":
            qb, db = query_entry["breakage"], self.entries[i]["breakage"]
            s += 3.0 * (qb["group_id"] == db["group_id"]) + 2.0 * (qb["artifact_id"] == db["artifact_id"])
        return s

    def retrieve(self, query_entry, level="L2", k=3, scorer="hybrid", include_researcher_written=True, diversify=True):
        t = query_entry["case_number"]
        excluded = set(query_entry["leakage"][f"exclude_{level}"]) | {t} if level != "NONE" else {t}
        cand = [i for i, e in enumerate(self.entries)
                if e["case_number"] not in excluded and (include_researcher_written or e["fix"]["is_reference_answer"])]
        ranked = sorted(cand, key=lambda i: -self.score(query_entry, i, scorer))
        if diversify:   # at most one entry per project-dependency group: k different fixes, not one fix k times
            seen, keep = set(), []
            for i in ranked:
                g = self.entries[i]["leakage"]["project_dependency_group"]
                if g not in seen:
                    seen.add(g); keep.append(i)
            ranked = keep
        ranked = ranked[:k]
        return [dict(rank=r + 1, kb_id=self.entries[i]["kb_id"], case_number=self.entries[i]["case_number"],
                     score=round(self.score(query_entry, i, scorer), 3), project=self.entries[i]["project"],
                     dependency=self.entries[i]["breakage"]["dependency"], mechanism=self.entries[i]["behavior"]["mechanism_family"],
                     category=self.entries[i]["behavior"]["category"], fix_type=self.entries[i]["fix"]["fix_type"],
                     fix_author=self.entries[i]["fix"]["author"]) for r, i in enumerate(ranked)]


def same_mech(a, b):
    return a == b and a != "SINGLETON"


def evaluate(root):
    E = load(root); ix = Index(E)
    by = {e["case_number"]: e for e in E}
    res = {}
    for level in ("L1", "L2", "L3"):
        for scorer in ("bm25", "hybrid"):
            for rw in (True, False):
                key = f"{level}/{scorer}/{'with' if rw else 'without'}_researcher_written"
                hits = {"mechanism@1": 0, "mechanism@3": 0, "category@1": 0, "category@3": 0}; mrr = 0.0; possible_mech = 0
                for e in E:
                    top = ix.retrieve(e, level, 10, scorer, rw)
                    pool = [x for x in E if x["case_number"] not in set(e["leakage"][f"exclude_{level}"]) | {e["case_number"]}
                            and (rw or x["fix"]["is_reference_answer"])]
                    has_mech = any(same_mech(x["behavior"]["mechanism_family"], e["behavior"]["mechanism_family"]) for x in pool)
                    possible_mech += has_mech
                    mech = [same_mech(x["mechanism"], e["behavior"]["mechanism_family"]) for x in top]
                    cat = [x["category"] == e["behavior"]["category"] for x in top]
                    hits["mechanism@1"] += mech[0] if mech else 0; hits["mechanism@3"] += any(mech[:3])
                    hits["category@1"] += cat[0] if cat else 0; hits["category@3"] += any(cat[:3])
                    mrr += next((1 / (r + 1) for r, m in enumerate(mech) if m), 0.0)
                n = len(E)
                res[key] = dict(cases=n, same_mechanism_available=possible_mech,
                                **{k: f"{v}/{n}" for k, v in hits.items()},
                                mechanism_recall_at3_when_available=f"{hits['mechanism@3']}/{possible_mech}", mechanism_MRR=round(mrr / n, 3))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root"); ap.add_argument("--case", type=int); ap.add_argument("--level", default="L2", choices=["NONE", "L1", "L2", "L3"])
    ap.add_argument("--k", type=int, default=3); ap.add_argument("--scorer", default="hybrid", choices=["bm25", "hybrid"])
    ap.add_argument("--no-researcher-written", action="store_true"); ap.add_argument("--evaluate", action="store_true")
    a = ap.parse_args()
    if a.evaluate:
        r = evaluate(a.root)
        json.dump(r, open(os.path.join(a.root, "kb", "retrieval_evaluation.json"), "w", encoding="utf-8"), indent=1)
        for k, v in r.items():
            print(f"{k:42s} mech@1 {v['mechanism@1']:>6}  mech@3 {v['mechanism@3']:>6} (of {v['same_mechanism_available']} possible)  "
                  f"cat@1 {v['category@1']:>6}  cat@3 {v['category@3']:>6}  MRR {v['mechanism_MRR']}")
    else:
        E = load(a.root); q = next(e for e in E if e["case_number"] == a.case)
        print(json.dumps(Index(E).retrieve(q, a.level, a.k, a.scorer, not a.no_researcher_written), indent=1))
