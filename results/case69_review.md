# Case 69 review

The a messaging CLI updates GraalJS ScriptEngine 22.0.0 to 22.1.0. The archived root POM version is the sole source/POM change. Both classpaths use GraalJS language runtime, Truffle and Graal SDK 22.0.0.

PRE reports 80 tests with one skip and succeeds. BREAKING reports 80 tests with three failures, nine errors and one skip. The same four tests fail across the AMQP, OpenWire and Artemis JMS suites. Copy and move tests report IllegalArgumentException for the unknown js.charset option. The logs show the same rejection interrupting dump-file creation and batch processing, leading to missing files and failed queue assertions.

Disassembly shows ScriptEngine 22.1.0 adds js.charset=UTF-8 to its default context options. The retained runtime rejects that option during context creation. A minimal Java probe evaluates 1 + 1 using the same language runtime and support JARs in the BREAKING image, with only the copied ScriptEngine JAR swapped. Version 22.0.0 evaluates to 2. Version 22.1.0 fails with the same unknown-option exception. The probe source, classpath commands and output are archived.

This is provisionally behavioural under the existing criterion for changed inputs to an API that still executes. The incompatible configuration is introduced internally by the newer ScriptEngine in the observed mixed-version stack. Independent review remains pending.

Maven and fresh Surefire reports agree on the totals. The original image pipes Maven through tee, so the explicit Maven result establishes the outcome.

## Label correction (2026-11-20)

This addendum was added after the AI second review and the researcher's rule decisions. The assessment above is Codex's original text and is unchanged.

- Previous label: PROVISIONAL_BEHAVIORAL (OTHER_BEHAVIORAL_CHANGE)
- Corrected label: **NON_BEHAVIORAL**
- Reason: Rule R2 (approved 2026-11-20): version skew between two GraalJS artifacts. Control run: setting the retained org.graalvm.js:js 22.0.0 -> 22.1.0, with js-scriptengine 22.1.0 kept, gives 80 tests, 0 failures, 0 errors (audit_claude_review/reruns/case69_graaljs_alignment_control.log).
- Records: `results/behavioral_classification.csv` (notes), `audit_claude_review/CHANGELOG.md`, `results/final_classification_rule_based.csv`.
