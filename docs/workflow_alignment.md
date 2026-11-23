# Alignment with the Research Workflow handbook

**Reference:** "3. Research Workflow — Automated Repair of Semantic Breakages in Java Dependency Updates" (the researcher's handbook, received 2026-11-23).
**Compared with:** the work in this repository as of commit `de04bb3`.
**Purpose:** to show what already matches the handbook, what differs (with the reason), and what is still missing, before the experiments are built.

## 1. The experiment the handbook defines (this answers "what are A, B, C, D")

| Condition | RAG | Attempts | READ_FILE tool |
|---|---|---|---|
| **A** single, no RAG | no | 1 | no |
| **B** single + RAG | yes | 1 | no |
| **C** agentic, no RAG | no | ≤ 5 | yes |
| **D** agentic + RAG | yes | ≤ 5 | yes |

**Trials and decoding:** n = 3 trials per case and condition, at temperature 0.

**Metrics:**
- BSR, by majority over the trials;
- BSR any-pass;
- REF, the best no-regression attempt's fraction of the originally failing tests that it fixes;
- iterations and tokens;
- verified-correct BSR, from a blind patch audit.

**Statistics:** Cochran's Q, then McNemar exact (BSR) and Wilcoxon (REF) on 5 planned pairs (A–B, C–D, A–C, B–D, A–D), with Holm correction and effect sizes.

**Research questions:**

| RQ | Comparison |
|---|---|
| RQ2 (does RAG help?) | B vs A, D vs C |
| RQ3 (does iteration help, and at what cost?) | C vs A, D vs B |
| RQ4 (which categories, and why do repairs fail?) | Per category, with a failure analysis |

## 2. Phase-by-phase comparison

| Handbook phase | What we have | Status |
|---|---|---|
| **2. Reproduce and triage BUMP** | All 188 TEST_FAILURE cases reproduced and triaged; 47-case rerun sample | ✅ Done |
| **3. Classify (RQ1)** | 56 BEHAVIORAL / 132 NON_BEHAVIORAL. Codex vs Claude blind κ = 0.90; the researcher reviewed Cases 1–20 (20/20 agree); frozen v1.0 | ⚠️ Differs: the handbook wants **two blind human raters** with κ. Our second rater is an AI |
| **4. Knowledge base** | 56 entries built from the BUMP cases themselves, each labelled by author, with L1/L2/L3 exclusions | ⚠️ Differs: see §3.1 |
| **5. Hybrid RAG** | BM25 plus a dependency boost, diversified; leakage exclusions applied at query time; evaluated with mechanism@k and MRR | ⚠️ Partial: no dense embeddings, no RRF, no relevance gate, no negative-query test |
| **6. Tools and FSM agent** | Harness v2.2 (5 checks, Docker, PRE baseline, flaky and network handling); a plain-Python repair loop | ⚠️ Partial: no READ_FILE tool, no diagnosis node. The guards differ (see §3.2) |
| **7. Code Agent, single case** | Prompt builder, context selection (coverage 55/56), Claude plug-in; end-to-end test with the oracle provider | ⚠️ Not yet run with a real LLM (the "golden milestone") |
| **8. 2×2 experiment and statistics** | Nothing yet | ❌ To build: condition presets, n trials, REF, aggregation, blind audit, statistics, figures |
| **9. Paper** | Frozen datasets and READMEs; a GitHub repository | Later |

Where our method is stronger than the handbook's, we keep it and report it:
- **NO_REGRESSION against the PRE test baseline.** The handbook compares only against the BREAKING failure set.
- **UPDATE_KEPT.** It checks the resolved dependency version directly.
- **Validated fixes for all 56 cases**, including 21 developer fixes.
- **Network and flaky handling** in the checker.
- **A plain-Python loop instead of LangGraph.** The handbook explicitly allows this (§6.2, ⑩ "Plain-Python alternative").

## 3. Real differences that need the researcher's decision

### 3.1 Where the knowledge base comes from (handbook Protocol 1 vs Protocol 2)

- **Handbook default (Protocol 1):** external knowledge only, from migration guides, non-BUMP fix commits and Stack Overflow. Never from an evaluated client.
- **Handbook alternative (Protocol 2):** a project-level split. BUMP cases may be knowledge-base entries if their project is excluded when that project is evaluated.
- **What we built** is Protocol 2. Under L2, a target's whole project-dependency group is excluded; in our 56 cases each project has one dependency, so L2 equals the handbook's R2 "same project" rule.
- **Option:** add a small external knowledge base (Protocol 1) for the main mechanisms (SLF4J 2 providers, Mockito 5 mock maker, XStream security, commons-io, jsoup, h2, json-smart, dropwizard-sentry). With both, RAG can be reported with and without BUMP-internal knowledge.
- **The handbook's R3** bans `auto_repair` entries. Our 28 researcher-written fixes were written and validated by an AI. They are closer to `auto_repair` than to human-curated entries, which supports keeping them as a separate, switchable group (already implemented).

### 3.2 Guards: the handbook blocks pom.xml and test edits; most of our validated fixes need them

The handbook rejects any patch that touches `pom.xml` (`BUILD_FILE_BLOCKED`) or `src/test/**` (`TEST_CHEATING_BLOCKED`). On our data that would make most cases unrepairable *by construction*:

| Fix needs | Cases (reference fixes) | Why |
|---|---|---|
| A POM change | 2, 18, 132, 100, 148, 184 (logback); 12, 15, 27, 150, 159, 185, 186 (logback); 14, 114 (h2); 53 (plexus-io); 163, 168 (json-smart); 171 (Dropwizard) | 36 of 56 cases are SLF4J provider selection (rule R5). Their correct repair is a companion dependency upgrade |
| A test change | 20 (XStream `allowTypes` in the test), 158 (expected message), 181 (expected output) | The new library behavior is intended, so the developers updated the test |

The handbook's own reason for the POM guard is to stop "repair" by **downgrading** the dependency. Our UPDATE_KEPT check blocks exactly that: the self-test showed the revert is rejected even though every test passes. It does so without blocking legitimate companion upgrades. Our NO_REGRESSION check, which treats missing classes as failures, blocks deleted or skipped tests.

**Recommendation:**
- Keep POM edits allowed, under UPDATE_KEPT.
- Allow test edits, but flag them, and count them in the blind audit (Phase 8.2).
- Report how often patches touch tests, by condition.
- Optionally run a sensitivity analysis with the handbook's strict guards.

### 3.3 Taxonomy labels differ

| Handbook (§3.1) | Ours (classification v1.0) |
|---|---|
| null_handling_change | – (no such case) |
| exception_type_change | EXCEPTION_TYPE_OR_CONDITION (2) |
| default_value_change | DEFAULT_SETTING_OR_POLICY (6) |
| encoding_format_change | OUTPUT_FORMAT (2) |
| ordering_change | – (no such case) |
| side_effect_change | – |
| – | **PROVIDER_OR_IMPLEMENTATION_SELECTION (36)**, ACCEPTED_INPUT (9), RETURN_VALUE (1) |

Our labels were derived from the data with approved decision rules (R1–R13), and they are frozen. For RQ4 we would report our categories, with this mapping table in the paper. A possible mapping is ACCEPTED_INPUT → default_value_change (new limits). PROVIDER_OR_IMPLEMENTATION_SELECTION has no handbook equivalent and is itself a finding.

### 3.4 Human second rater for RQ1

The handbook expects two blind human raters on at least 30% of the cases, with κ. We have AI vs AI κ = 0.90, plus the researcher's own review of 20 cases. **Option:** a second human (a supervisor or lab mate) labels a blind random 30% (≈ 17 of the 56 BEHAVIORAL, or ≈ 57 of the 188). Our tooling can export the blind rating sheet.

## 4. Cost estimate for Phase 8 (handbook formula, our measured prompt size)

**Formula:** cases × trials × attempts × tokens. The inputs:
- 56 cases × 3 trials × (1 + 1 + ~3 + ~3) attempts ≈ **1,344 LLM calls**;
- median prompt ≈ 10.6k input tokens (measured in our dry run), and roughly 1.5k output tokens per call.

That totals ≈ 14.2 M input and 2.0 M output tokens. List prices, before any prompt caching:

| Model | Estimated cost |
|---|---:|
| claude-haiku-5-5 | ≈ $2.5 |
| claude-sonnet-5-5 | ≈ $49 |
| claude-opus-5-5 | ≈ $97 |

**A cheap pilot** (5 cases, 1 trial, A and D only) costs well under $2 on any of these.

## 5. Recommended order of work

1. **Decide §3.1–§3.4** (knowledge-base source, guards, labels, second rater) and the model.
2. **Fill the remaining gaps (no cost):**
   - condition presets A–D and n trials;
   - REF per attempt;
   - READ_FILE tool in C/D;
   - optional diagnosis step;
   - dense embeddings, RRF, gate and negative queries;
   - aggregation, blind audit export and statistics script.
3. **Golden milestone** (handbook Phase 7): run 1–3 real cases end to end with the chosen LLM.
4. **Pilot:** 5 cases, 1 trial, conditions A and D.
5. **Main run:** 56 cases × A–D × 3 trials; then the audit, statistics and figures.
