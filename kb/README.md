# Knowledge base and retrieval (RAG, retrieval part)

**Built:** 2026-11-22. **Sources (frozen only):** `results/classification_v1.0`, `fix_mining/fixes_v1.0`, and the BUMP benchmark records (`bump/`, commit 324d551).
**Status:** knowledge base and leakage-safe retrieval are done. The LLM step is not connected yet: the model, the inclusion of researcher-written fixes and the experiment design are still to be decided.

## Knowledge base (`entries.jsonl`, 56 entries)

Each entry has one section per kind of information:

| Section | Contents |
|---|---|
| `breakage` | Dependency, old → new version, update type, failing test classes, exception types, first error lines, SLF4J console lines |
| `behavior` | Rule, category, description, primary cause, mechanism family (classification v1.0) |
| `library_change` | GitHub compare link (47/56) and Maven source-jar links. The library diffs are not yet downloaded |
| `fix` | Validated patch, fix type, explanation, changed files, validation counts. **`author`** is developer (21), derived (7) or researcher-written (28), and **`is_reference_answer`** is false for researcher-written |
| `leakage` | Exclusion lists L1/L2/L3 from `retrieval_exclusions.csv`, and the fold |
| `retrieval_text` | The indexed text: symptoms and the behavior description. The fix text is not indexed |

Rebuild with `python -I kb/scripts/build_kb.py <root>`. `kb_manifest.json` holds the counts and the SHA-256 of `entries.jsonl`.

## Retrieval (`scripts/retrieve.py`)

- **Query:** only what a new breakage shows in its build log (dependency, versions, failing tests, exceptions, error lines). A new case has no classification yet.
- **Scorers:**
  - `bm25`: identifier-aware tokens (dotted names and camelCase are split);
  - `hybrid`: BM25 plus a boost for the same dependency group and the same artifact;
  - `dense`: cosine similarity of `all-MiniLM-L6-v2` embeddings (`scripts/dense.py`; document vectors cached in `index/`, tied to the model and the KB fingerprint);
  - `rrf`: Reciprocal Rank Fusion of the dense rank (weight 0.6) and the hybrid rank, k = 60 (handbook 5.1). **This is the scorer for the experiments.**
- **Relevance gate** (`DEFAULT_GATE`): a candidate is shown to the LLM only if cosine ≥ 0.5 **or** lexical ≥ 50. If nothing passes, no example is shown. See "Gate" below for how the values were chosen.
- **Leakage:** the target case and its L1/L2/L3 exclusions are always removed.
- **Researcher-written fixes:** retrievable only with `include_researcher_written=True`. Use `--no-researcher-written` on the command line to exclude them.
- **Diversified:** at most one result per project-dependency group, so the LLM sees k different fixes rather than one fix k times.

```
python -I kb/scripts/retrieve.py <root> --case 1 --level L2 --k 3
python -I kb/scripts/retrieve.py <root> --case 1 --scorer rrf --gate
python -I kb/scripts/retrieve.py <root> --evaluate        # lexical scorers only -> kb/retrieval_evaluation.json
python -I kb/scripts/eval_retrieval.py <root>             # all scorers, negatives, gate sweep -> kb/retrieval_evaluation_v2.json
```

## Retrieval quality (hybrid, diversified, all 56 cases as queries)

**Mechanism hit** means a top-k entry has the same mechanism family as the target. SINGLETON, a bucket of unrelated one-off mechanisms, never counts as a match.

| Level | Researcher-written | Same mechanism available | Mechanism hit @1 | Category hit @3 | MRR |
|---|---|---:|---:|---:|---:|
| L1 | with | 48 | 48/56 | 49/56 | 0.857 |
| L1 | without | 43 | 43/56 | 44/56 | 0.768 |
| **L2 (primary)** | **with** | **41** | **41/56** | **46/56** | **0.732** |
| L2 | without | 36 | 36/56 | 41/56 | 0.643 |
| L3 | with / without | 0 | 0/56 | 5/56 | 0.0 |

**Reading:**
- **Under L2, retrieval is perfect when an answer exists.** Whenever a same-mechanism example is in the pool, it is ranked first (41/41).
- **The other 15 L2 cases are one-off mechanisms.** No similar past fix exists for them, so retrieval cannot help much.
- **Under L3** same-mechanism examples are excluded by design, so L3 measures transfer from *different* mechanisms.
- **Researcher-written fixes matter:** including them gives 5 more L2 cases a same-mechanism example. This is evidence for the pending decision.
- **The hybrid boost changed no ranking compared with plain BM25:** the dependency name already dominates the lexical score.

## Dense, RRF and the relevance gate (`eval_retrieval.py`, `retrieval_evaluation_v2.json`)

**Negatives** (`retrieval_negatives.json`): 10 hand-written breakages whose mechanism is not in the KB. Seven are hard (realistic Java: Guava ordering, Jackson limits, Joda-Time, Hibernate, OkHttp, Commons Lang, Netty) and three are easy (non-Java or nonsense). The gate should return nothing for them.

**Ungated (L2):** all four scorers reach Hit@1 = Hit@3 = MRR = 1.0 on the 41 cases that have a same-mechanism example. But they also return something for every negative, because ranking alone never says "nothing fits".

**Score ranges (L2, RRF):**

| | cosine | lexical |
|---|---|---|
| best true match of each positive | 0.558 – 0.923 | 27.3 – 59.4 |
| top result for a negative | 0.080 – 0.458 | 1.5 – 23.4 |

**Gate:** we chose cosine ≥ 0.5 OR lexical ≥ 50 from a sweep (cosine 0.4–0.7 × lexical 20–50/off). This is the least strict setting that keeps Hit@3 = 1.0 and rejects all negatives. The values were fixed before any LLM run and are not tuned on experiment results.

| Level | Researcher-written | Hit@3 (of available) | Negatives rejected | "No example" cases given nothing |
|---|---|---:|---:|---:|
| L1 | with / without | 1.0 (48) / 1.0 (43) | 10/10 | 0.88 (8) / 0.92 (13) |
| **L2** | **with** / without | **1.0 (41)** / 1.0 (36) | **10/10** | **0.93 (15)** / 0.95 (20) |
| L3 | with / without | n/a (0) | 10/10 | 0.34 (56) |

**Limits (report these):**
- **The negatives are few and hand-written,** and the thresholds come from the same data. With so few examples, the gap between 0.458 and 0.558 may be optimistic.
- **The gate filters *unrelated* examples, not *look-alike* ones.** At L3, two in three cases still get an example from a different mechanism, mostly logging cases that read alike. So the L3 condition really tests "misleading-but-similar" examples, which is what L3 is meant to measure.

## Not done yet (pending the researcher's decisions)

1. Download the library change content (release notes or diffs) into `library_change`.
2. The LLM step, once the model is chosen (the prompt builder and loop are in `pipeline/`).
