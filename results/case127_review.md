# Case 127 review

Both original Refactoring-Bot images ran. PRE passed all 62 tests. BREAKING reported 62 tests with one error in GrammarServiceTest.testCheckComment. Maven and fresh Surefire XML agree. The archived client sources match and the root POM changes only the ANTLR runtime version. The affected classpath replaces 4.7.2 with 4.11.1.

The generated lexer identifies ANTLR 4.7.1 as its generator. Its static initialization calls ATNDeserializer.deserialize(char[]). Disassembly confirms the method exists in both runtime JARs. The same generated lexer and probe bytecode initialized successfully with 4.7.2. With 4.11.1, the same method resolved and rejected the serialized grammar data with 'version 3 (expected 4)'. The resulting UnsupportedOperationException and InvalidClassException are wrapped by ExceptionInInitializerError.

The change in accepted input supports PROVISIONAL_BEHAVIORAL with no binary linkage failure. The generated-data compatibility boundary remains pending independent human review. The probe runs are archived separately from the original test counts.

## Label correction (2026-11-20)

This addendum was added after the AI second review and the researcher's rule decisions. The assessment above is Codex's original text and is unchanged.

- Previous label: PROVISIONAL_BEHAVIORAL (OTHER_BEHAVIORAL_CHANGE)
- Corrected label: **NON_BEHAVIORAL**
- Reason: Rule R8 (approved 2026-11-20): an ANTLR runtime rejecting serialized ATN data produced by an older generator is generator/runtime alignment, fixed by regenerating the parser with a matching tool. Mechanism unchanged and confirmed (lexer probes in cases 112, 127, 140, 188).
- Records: `results/behavioral_classification.csv` (notes), `audit_claude_review/CHANGELOG.md`, `results/final_classification_rule_based.csv`.
