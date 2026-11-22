# Case 67 review

scheduler upgrades ANTLR Runtime 4.9.3 to 4.10 in safeplace/pom.xml. This is the sole archived source/POM change. The generated lexer copied from each stopped container is byte-identical and identifies ANTLR 4.9.3 as its generator.

PRE passes 943 tests. BREAKING reports 903 tests and one failure with zero errors or skips, then skips downstream modules. Top-level Surefire XML agrees with Maven. The raw archive also contains nested TestNG per-class reports that repeat the same executions. Their totals are excluded. The nested XML calls the failed test an error, while the suite-level report and Maven count it as a failure.

SpecScannerTest.test fails during lexer initialization. Its generated lexer calls the existing ATNDeserializer.deserialize(char[]) API. ANTLR 4.10 executes that method and rejects serialized ATN format version 3 because it expects version 4. The runtime disassembly and generated lexer support a provisional behavioural assessment for changed format acceptance, pending independent human review. Case 49 shows a related mechanism.

The original logs, generated lexer sources, runtime JARs and reports are archived. The automated screen captures the safeplace module alone and marks the exception for review. Explicit Maven output establishes the outcome because the image pipes Maven through tee.

## Label correction (2026-11-20)

This addendum was added after the AI second review and the researcher's rule decisions. The assessment above is Codex's original text and is unchanged.

- Previous label: PROVISIONAL_BEHAVIORAL (OTHER_BEHAVIORAL_CHANGE)
- Corrected label: **NON_BEHAVIORAL**
- Reason: Rule R8 (approved 2026-11-20): an ANTLR runtime rejecting serialized ATN data produced by an older generator is generator/runtime alignment, fixed by regenerating the parser with a matching tool. Mechanism unchanged and confirmed (lexer probes in cases 112, 127, 140, 188).
- Records: `results/behavioral_classification.csv` (notes), `audit_claude_review/CHANGELOG.md`, `results/final_classification_rule_based.csv`.
