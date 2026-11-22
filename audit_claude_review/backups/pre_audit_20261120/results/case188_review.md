# Case 188 review

Refactoring-Bot updates antlr4-runtime from 4.7.2 to 4.10.

ANTLR 4.10 rejects version 3 of the serialized ATN embedded in the unchanged generated lexer. The same compiled lexer and probe initialize successfully with runtime 4.7.2. Both expose deserialize(char[]), and the updated method reaches format validation and expects version 4.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 62 | 0 | 0 | 0 |
| BREAKING | FAILURE | 62 | 0 | 1 | 0 |

Assessment is `PROVISIONAL_BEHAVIORAL`. Binary linkage flag is `NO`. Independent human review is pending.

Changed POMs in the original archives are pom.xml. Original logs and archived reports are indexed in the evidence manifest.
