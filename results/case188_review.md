# Case 188 review

Refactoring-Bot updates antlr4-runtime from 4.7.2 to 4.10.

ANTLR 4.10 rejects version 3 of the serialized ATN embedded in the unchanged generated lexer. The same compiled lexer and probe initialize successfully with runtime 4.7.2. Both expose deserialize(char[]), and the updated method reaches format validation and expects version 4.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 62 | 0 | 0 | 0 |
| BREAKING | FAILURE | 62 | 0 | 1 | 0 |

Assessment is `PROVISIONAL_BEHAVIORAL`. Binary linkage flag is `NO`. Independent human review is pending.

Changed POMs in the original archives are pom.xml. Original logs and archived reports are indexed in the evidence manifest.

## Label correction (2026-11-20)

This addendum was added after the AI second review and the researcher's rule decisions. The assessment above is Codex's original text and is unchanged.

- Previous label: PROVISIONAL_BEHAVIORAL (OTHER_BEHAVIORAL_CHANGE)
- Corrected label: **NON_BEHAVIORAL**
- Reason: Rule R8 (approved 2026-11-20): an ANTLR runtime rejecting serialized ATN data produced by an older generator is generator/runtime alignment, fixed by regenerating the parser with a matching tool. Mechanism unchanged and confirmed (lexer probes in cases 112, 127, 140, 188).
- Records: `results/behavioral_classification.csv` (notes), `audit_claude_review/CHANGELOG.md`, `results/final_classification_rule_based.csv`.
