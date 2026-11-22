# Case 49 review

The Refactoring-Bot ANTLR Runtime upgrade from 4.7.2 to 4.10.1 is provisionally **behavioural**, pending human review.

PRE passed all 62 tests. BREAKING reported 62 tests and one error with zero assertion failures or skips. GrammarServiceTest.testCheckComment fails while initializing the generated lexer. ExceptionInInitializerError wraps UnsupportedOperationException and InvalidClassException with the message `Could not deserialize ATN with version 3 (expected 4)`.

The unchanged BotOperationsLexer and BotOperationsParser source headers identify ANTLR 4.7.1 as their generator. Each holds serialized ATN data and invokes ATNDeserializer.deserialize(char[]) during static initialization. Disassembly confirms that both resolved runtime versions still expose that method signature. The newer runtime rejects the serialized format previously accepted by 4.7.2, changing the accepted input contract of the deserialization call.

Human review should adjudicate the taxonomy boundary for generated-code serialized-data compatibility. The recorded binary linkage flag is NO because the invoked class and method exist and execution reaches the runtime's format validation. The nested InvalidClassException reports this serialized ATN version rejection.

Only the ANTLR runtime version changes in the archived POM and affected classpath paths. Maven and fresh Surefire summaries agree. Both image commands pipe Maven through tee, masking its failing exit code. Logs have prefix `448ff013` under `logs/batch_triage/`. Source archives, reports, runtime JARs and disassembly are under `logs/case49_evidence/`.

## Label correction (2026-11-20)

This addendum was added after the AI second review and the researcher's rule decisions. The assessment above is Codex's original text and is unchanged.

- Previous label: PROVISIONAL_BEHAVIORAL (OTHER_BEHAVIORAL_CHANGE)
- Corrected label: **NON_BEHAVIORAL**
- Reason: Rule R8 (approved 2026-11-20): an ANTLR runtime rejecting serialized ATN data produced by an older generator is generator/runtime alignment, fixed by regenerating the parser with a matching tool. Mechanism unchanged and confirmed (lexer probes in cases 112, 127, 140, 188).
- Records: `results/behavioral_classification.csv` (notes), `audit_claude_review/CHANGELOG.md`, `results/final_classification_rule_based.csv`.
