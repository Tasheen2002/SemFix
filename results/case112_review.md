# Case 112 review

Refactoring-Bot updates antlr4-runtime from 4.7.2 to 4.12.0. Only the root POM runtime version changes among archived source/POM files, and the affected test classpath changes only this JAR.

Both original images were run. PRE succeeds with 62 tests and no failures, errors or skips. BREAKING reports 62 tests, zero failures, one error and no skips. Maven and 12 fresh Surefire XML reports per phase agree. GrammarServiceTest.testCheckComment fails with ExceptionInInitializerError wrapping UnsupportedOperationException and InvalidClassException: Could not deserialize ATN with version 3 (expected 4).

The unchanged BotOperationsLexer and BotOperationsParser headers identify ANTLR 4.7.1 as their generator. The generated code stores serialized grammar data and calls ATNDeserializer.deserialize(char[]) during static initialization. Actual runtime JAR inspection and disassembly confirm that this public method exists in both versions. The newer runtime rejects input previously accepted by the older runtime; the InvalidClassException concerns serialized ATN data, not JVM class-file loading.

A focused diagnostic copies the byte-identical original lexer source, compiles it once against the PRE runtime to Java 11 bytecode, and runs the same compiled lexer/probe classes against each original image's runtime JAR. Both runs locate the existing deserialize(char[]) method. PRE initializes the lexer successfully (exit 0); BREAKING enters deserialization and throws the same version-3/expected-4 format rejection (exit 1). Source hashes, compiled-class hashes, commands, image identities and full output are archived. This supports a changed accepted-input contract, with binary_linkage_incompatibility=NO.

The assessment is PROVISIONAL_BEHAVIORAL pending independent human review. Reviewers should adjudicate the taxonomy boundary for generated-code/serialized-data compatibility. Automated screening is not a final semantic verdict; reviewer/final labels remain blank. Explicit Maven outcomes establish results because the original tee pipeline masks build failure in the container exit code. No repair or dependency substitution was attempted.

## Label correction (2026-11-20)

This addendum was added after the AI second review and the researcher's rule decisions. The assessment above is Codex's original text and is unchanged.

- Previous label: PROVISIONAL_BEHAVIORAL (OTHER_BEHAVIORAL_CHANGE)
- Corrected label: **NON_BEHAVIORAL**
- Reason: Rule R8 (approved 2026-11-20): an ANTLR runtime rejecting serialized ATN data produced by an older generator is generator/runtime alignment, fixed by regenerating the parser with a matching tool. Mechanism unchanged and confirmed (lexer probes in cases 112, 127, 140, 188).
- Records: `results/behavioral_classification.csv` (notes), `audit_claude_review/CHANGELOG.md`, `results/final_classification_rule_based.csv`.
