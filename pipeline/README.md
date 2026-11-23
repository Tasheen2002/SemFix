# Automated repair pipeline (RAG + LLM + harness)

**Status (2026-11-23):** built and tested end to end **without an LLM**:
- the dry run builds the prompts;
- the oracle and retry tests run the full loop.

**Pending:** the researcher's decisions on the LLM model, the use of researcher-written fixes in retrieval, and the experiment definitions (A/B/C). No LLM has been called and nothing has been spent.

```
BREAKING build log ─► breakage reader ─► retrieval (kb/, leakage-safe) ─► prompt builder ─► LLM ─► patch
        ▲                                                                                        │
        └────────────── feedback (what failed, why) ◄── harness (5 checks, Docker) ◄──────────────┘
```

## Parts

| File | Role |
|---|---|
| `scripts/context.py` | **Breakage reader:** symptoms from the raw BREAKING log (failing tests, exceptions, error lines, project stack frames, SLF4J console). **Code context** (in priority order, within a budget of 60,000 characters): the POM(s) declaring the dependency (large POMs windowed around the dependency, the libraries in the error and the libraries the failing tests import), the failing tests, resource files that contain an identifier from the error or that the failing tests name, and the stack-trace classes. |
| `scripts/prompt.py` | Fixed system prompt (cacheable) with the rules: keep the update, don't weaken tests, output one unified diff. The user prompt holds the update, failure, retrieved examples (each labelled with its author), files and retry feedback. When a patch did not apply, the feedback shows only git's error. |
| `scripts/llm_claude.py` | Claude through the official `anthropic` SDK. Default `claude-opus-5-5`, effort `high`, adaptive thinking, server-side refusal fallback `fallbacks="default"`. The model that served each answer is recorded. The key comes from the environment and is never stored. |
| `scripts/llm_manual.py` | **No-key providers.** `ManualProvider` writes prompts to files and reads pasted answers (any chat LLM). `OracleProvider` and `OracleRetryProvider` are **pipeline tests only**: they return the frozen fix, with a broken first attempt in the retry variant. |
| `scripts/repair.py` | The loop: breakage → context → retrieval (`--condition rag|no_rag`, `--level L1|L2|L3`, `--k`, `--no-researcher-written`) → up to `--attempts` × (prompt → LLM → patch → `harness/scripts/evaluate_patch.py`) → `runs/<label>/case<N>.json`. Stops early on REPAIRED, and on INCONCLUSIVE (infrastructure). |
| `scripts/check_context_coverage.py` | Can the LLM see what the validated fix changes? Checks every edited file and removed line against the prompt. |

## Results so far (no LLM)

| Test | Result |
|---|---|
| Dry run, RAG, L2, all 56 | Prompts of 14k–75k characters, median about 37k (about 10.6k tokens). Builds in under 1 minute |
| Context coverage | **55/56 COVERED**: every file and line the validated fix changes is in the prompt. Case 171 is PARTIAL (a 15-file framework migration) |
| Oracle end to end (Cases 13, 28) | Both REPAIRED in 1 attempt: patch extracted from an LLM-style reply, the harness ran all 5 checks |
| Retry with feedback (Case 13) | Attempt 1 (broken patch) was rejected with `corrupt patch`; the feedback appeared in prompt 2; attempt 2 was REPAIRED |

**Bugs found by the dry run and fixed before any LLM use:**
- example explanations did not match the shown patch (derived fixes);
- large POMs crowded out the tests;
- 18 cases were missing the file their fix edits (config YAML, expected-output resources, test-logger POM lines);
- a stray control character from an edit script broke the package-name rule.

## Usage

```
# prompts only (free): inspect pipeline/runs/<label>/prompts/
python -I pipeline/scripts/repair.py <root> --cases all --condition rag --provider manual --label myrun --dry-run
python -I pipeline/scripts/check_context_coverage.py <root> --label myrun

# by hand with any chat LLM: run once (writes prompts), paste answers into runs/<label>/responses/, run again
python -I pipeline/scripts/repair.py <root> --cases 13 --provider manual --label manual1

# Claude API (after the model is chosen; needs ANTHROPIC_API_KEY or `ant auth login`)
python -I pipeline/scripts/repair.py <root> --cases all --condition rag --provider claude --model <id> --label expB
```

Every run records the retrieved cases, the prompt size, the model requested and served, the token usage, each patch and each harness verdict.
