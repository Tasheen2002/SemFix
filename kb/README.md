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
  - `hybrid`: BM25 plus a boost for the same dependency group and the same artifact.

  `Index.score()` is the single place to plug in an embedding scorer later.
- **Leakage:** the target case and its L1/L2/L3 exclusions are always removed.
- **Researcher-written fixes:** retrievable only with `include_researcher_written=True`. Use `--no-researcher-written` on the command line to exclude them.
- **Diversified:** at most one result per project-dependency group, so the LLM sees k different fixes rather than one fix k times.

```
python -I kb/scripts/retrieve.py <root> --case 1 --level L2 --k 3
python -I kb/scripts/retrieve.py <root> --evaluate        # writes kb/retrieval_evaluation.json
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

## Not done yet (pending the researcher's decisions)

1. Download the library change content (release notes or diffs) into `library_change`.
2. An embedding scorer, if wanted.
3. The prompt builder and the LLM step, once the model is chosen.
4. The automated loop: retrieve → prompt → patch → `harness/scripts/evaluate_patch.py` → retry.
