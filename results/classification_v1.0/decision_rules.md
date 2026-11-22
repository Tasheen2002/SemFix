# Decision rules for classifying the 188 candidates

**Purpose:** Codex and Claude agree on what happened in all 188 cases; they disagree only on which category some mechanisms belong in. This sheet fixes the categories as explicit rules. Once a human approves the rules, every case is labelled by rule plus evidence rather than by reviewer judgment.

**How to use it:**
1. Approve, amend or reject each rule in the sign-off column.
2. Run the checks marked `NEEDS_RUN` in `control_plan.csv`.
3. Review the 47 cases in `human_sample.csv` against the approved rules.
4. If the sample agrees with the rule-based labels, apply the rules to all 188 and record the outcome in `final_label`.

## Order of application

Apply the rules top to bottom and stop at the first one that matches the **initiating** failure: the first error in the BREAKING log, not a follow-on such as "Could not initialize class" or an assertion that runs on null output.

| # | Rule | Label | Cases | Status | Sign-off |
|---|---|---|---:|---|---|
| R11 | **Fixture-only edit.** Only test resources changed and the effective test classpath is identical. | NON_BEHAVIORAL | 1 (161) | Covered | ☐ |
| R1 | **Linkage or bytecode.** The initiating error is `NoClassDefFoundError`, `ClassNotFoundException` for a class the code links to, `NoSuchMethodError`, `NoSuchFieldError`, `AbstractMethodError`, `IncompatibleClassChangeError`, `VerifyError`, `IllegalAccessError` or `UnsupportedClassVersionError`. This applies even if the visible test failure is an assertion. | NON_BEHAVIORAL | 92 | Covered or static evidence | ☐ |
| R6 | **Retained API references a removed binding class.** For example, slf4j-api 1.7 looks up a `StaticLoggerBinder` that logback 1.4 removed and silently falls back to NOP. | NON_BEHAVIORAL | 6 | Covered | ☐ |
| R10 | **Tooling or test-infrastructure failure.** For example, a Surefire provider or plugin mismatch, an ArchUnit rule scanning new dependency code, or a test engine refusing a JUnit version. | NON_BEHAVIORAL | 9 | **Done (116):** Vintage rejects JUnit 3.8.1 | ☐ |
| R4 | **Framework-generation mismatch.** The updated artifact targets a newer major version of its host framework (dropwizard-sentry 4.x on Dropwizard 2). | NON_BEHAVIORAL | 3 | Covered | ☐ |
| R13 | **Packaging change removes a runtime provider.** For example, a transitive dependency moves to test scope (MOXy 4 drops its ASM service). | NON_BEHAVIORAL | 1 (30) | **Done:** adding the ASM provider → 737 tests, 0 errors | ☐ |
| R3 | **javax↔jakarta namespace migration.** A javax class is missing, a javax API finds no provider, or javax annotations are no longer recognised. | NON_BEHAVIORAL | 13, including 109 | Covered by trace. **Decided: NON_BEHAVIORAL including 109** (researcher, 2026-11-20) | ☑ |
| R2 | **Version skew inside one library family, without a JVM linkage error.** The same library ships as several artifacts and only one was updated, so the failure appears as an ordinary exception, such as an unknown option. | NON_BEHAVIORAL | 1 (69) | **Done:** aligning `js` to 22.1.0 → 80/80 tests pass | ☐ |
| R9 | **Changed default in the updated library.** For example, Mockito 5's default mock maker. It counts only if the test passes on the updated version once the old default is restored. | BEHAVIORAL | 5 | Covered (4 controls) | ☐ |
| R5 | **Provider selection changed while the old provider is still present.** SLF4J 2.x ignores a 1.7-style binding that is on the classpath and selects NOP. | BEHAVIORAL (brief's rule) or NON_BEHAVIORAL | 36 | **Decided: BEHAVIORAL** (researcher, 2026-11-20) | ☑ BEH ☐ NON |
| R7 | **A configuration property is no longer accepted.** The updated factory rejects a YAML field the client still sets. | BEHAVIORAL (accepted input changed) or NON_BEHAVIORAL (API removal) | 5 | **Decided: BEHAVIORAL** (researcher, 2026-11-20) | ☑ BEH ☐ NON |
| R8 | **A serialized artifact produced by an older generator is rejected.** ANTLR 4.10+ rejects ATN v3 through the same `deserialize(char[])` API. | BEHAVIORAL (accepted input changed) or NON_BEHAVIORAL (generator/runtime alignment) | 6 | **Decided: NON_BEHAVIORAL** (researcher, 2026-11-20) | ☐ BEH ☑ NON |
| R12 | **Core behavioral change.** Same API, same input, and a different return value, exception type, message format, accepted input, default policy or output format, with no linkage error on the path. It needs a probe, or a stack trace that originates inside the updated library. | BEHAVIORAL | 10 (13, 14, 20, 53, 70, 114, 158, 163, 168, 181) | Covered | ☐ |

R1 to R13 together cover all 188 cases. Each case's rule is listed in `control_plan.csv` (by group) and in `claude_audit.csv`.

## Effect of the three open decisions on RQ1 (n = 188)

The table assumes R1–R4, R6 and R9–R13 are approved as proposed.

| R5 (SLF4J, 36) | R7 (config, 5) | R8 (ANTLR, 6) | BEHAVIORAL | % of 188 |
|---|---|---|---:|---:|
| BEH | BEH | BEH | 62 | 33.0% |
| BEH | BEH | NON | 56 | 29.8% |
| BEH | NON | NON | 51 | 27.1% |
| NON | BEH | BEH | 26 | 13.8% |
| NON | BEH | NON | 20 | 10.6% |
| NON | NON | NON | 15 | 8.0% |

Codex's current count (64) equals the first row plus Cases 69 and 109, which these rules place under R2 and R3. If R3 is approved, Codex's label for 109 is inconsistent with its own labels for the hibernate-validator cases 83, 93, 164 and 180.

## Points for the adjudicator to weigh

- **R5.** The brief's rule treats this as behavioral because the old binding still exists and the new API picks a different implementation. The probe in Case 150 confirms that: with the same jars, PRE selects logback and BREAKING selects NOP. The counter-argument is that the SLF4J project documents this as a provider-compatibility change, and the repair is a dependency alignment (moving to a logback 1.3+/1.4 provider), not a client code change. Ideally, decide R5 and R8 by the same principle: either the outcome counts (behavioral), or the kind of repair counts (non-behavioral).
- **R7.** In the `stacktraceAppPackages` cases, the property has no replacement under the same name, so the client must edit its configuration. That supports BEHAVIORAL.
- **R8.** Repair requires regenerating the lexer with a matching ANTLR tool, which is a build change, not a client source change. That supports NON_BEHAVIORAL.

## Sign-off

| Reviewer | Date | Rules approved | Rules amended (describe) |
|---|---|---|---|
| Researcher (via Claude Code chat) | 2026-11-20 | R5 = BEHAVIORAL, R7 = BEHAVIORAL, R8 = NON_BEHAVIORAL, R3 = NON_BEHAVIORAL including Case 109. The other rules were accepted as written when the researcher asked to finish the classification. | none |

## Outcome under the decisions

BEHAVIORAL 56 (29.8%) and NON_BEHAVIORAL 132 (70.2%) of 188, with 0 uncertain. See `results/final_classification_rule_based.csv` and `results/rq1_classification_summary.md`. Per-case human review of the 47-case sample (`human_sample.csv`) is still recommended as a check on how the rules were applied.
