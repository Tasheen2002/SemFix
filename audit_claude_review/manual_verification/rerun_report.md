# Rerun verification of the 47 sample cases

**Run:** manual_verification/verify_case.ps1 against the original BREAKING images. Fresh `--rm` containers, Maven exit code captured directly. **Compared with:** the original BUMP BREAKING logs. **Date:** 2026-11-20. **Source:** AI verification (Claude), not a human review.

| Verdict | Cases |
|---|---:|
| REPRODUCED | 46 |
| MISMATCH (automatic) → REPRODUCED after manual check | 1 |

- **REPRODUCED:** same build result, test counts, linkage signals and exception types.
- **REPRODUCED_WITH_COUNT_DIFFERENCE:** same failure mechanism, but the counts differ (for example a flaky or time-dependent test).
- **MISMATCH:** the mechanism differs; the case needs a human look before its label is accepted.

## Cases needing attention

- **Case 4** (NON_BEHAVIORAL, R10): flagged MISMATCH automatically; **manually confirmed REPRODUCED**. The same module (paris) fails with the same surefire API incompatibility and identical counts. The differing exception comes from a passing test calling an external staging host (ConnectException vs EOFException): network noise.

## All cases

| Case | Proposed | Rule | Verdict | Rerun build / exit | Rerun t/f/e |
|---|---|---|---|---|---|
| 1 | BEHAVIORAL | R5 | REPRODUCED | FAILURE / 1 | 737/0/30 |
| 2 | BEHAVIORAL | R5 | REPRODUCED | FAILURE / 1 | 94/0/3 |
| 3 | NON_BEHAVIORAL | R1 | REPRODUCED | FAILURE / 1 | 59/33/0 |
| 4 | NON_BEHAVIORAL | R10 | MISMATCH | FAILURE / 1 | 26/0/0 |
| 6 | NON_BEHAVIORAL | R1 | REPRODUCED | FAILURE / 1 | 89/2/0 |
| 7 | NON_BEHAVIORAL | R1 | REPRODUCED | FAILURE / 1 | 80/0/79 |
| 8 | NON_BEHAVIORAL | R1 | REPRODUCED | FAILURE / 1 | 16/0/16 |
| 9 | BEHAVIORAL | R9 | REPRODUCED | FAILURE / 1 | 510/1/0 |
| 11 | NON_BEHAVIORAL | R1 | REPRODUCED | FAILURE / 1 | 22/0/16 |
| 13 | BEHAVIORAL | R12 | REPRODUCED | FAILURE / 1 | 345/0/1 |
| 14 | BEHAVIORAL | R12 | REPRODUCED | FAILURE / 1 | 52/0/22 |
| 19 | NON_BEHAVIORAL | R1 | REPRODUCED | FAILURE / 1 | 161/0/15 |
| 20 | BEHAVIORAL | R12 | REPRODUCED | FAILURE / 1 | 5/0/1 |
| 25 | NON_BEHAVIORAL | R1 | REPRODUCED | FAILURE / 1 | 61/0/48 |
| 28 | BEHAVIORAL | R7 | REPRODUCED | FAILURE / 1 | 34/0/1 |
| 30 | NON_BEHAVIORAL | R13 | REPRODUCED | FAILURE / 1 | 737/0/15 |
| 32 | NON_BEHAVIORAL | R1 | REPRODUCED | FAILURE / 1 | 5/0/2 |
| 34 | NON_BEHAVIORAL | R1 | REPRODUCED | FAILURE / 1 | 686/0/10 |
| 37 | NON_BEHAVIORAL | R1 | REPRODUCED | FAILURE / 1 | 18/0/5 |
| 42 | NON_BEHAVIORAL | R3 | REPRODUCED | FAILURE / 1 | 42/0/16 |
| 44 | NON_BEHAVIORAL | R1 | REPRODUCED | FAILURE / 1 | 16/0/10 |
| 46 | NON_BEHAVIORAL | R6 | REPRODUCED | FAILURE / 1 | 12/2/0 |
| 49 | NON_BEHAVIORAL | R8 | REPRODUCED | FAILURE / 1 | 62/0/1 |
| 53 | BEHAVIORAL | R12 | REPRODUCED | FAILURE / 1 | 177/0/22 |
| 64 | NON_BEHAVIORAL | R10 | REPRODUCED | FAILURE / 1 | 49/1/0 |
| 67 | NON_BEHAVIORAL | R8 | REPRODUCED | FAILURE / 1 | 903/1/0 |
| 69 | NON_BEHAVIORAL | R2 | REPRODUCED | FAILURE / 1 | 80/3/9 |
| 70 | BEHAVIORAL | R12 | REPRODUCED | FAILURE / 1 | 205/0/2 |
| 71 | NON_BEHAVIORAL | R1 | REPRODUCED | FAILURE / 1 | 331/0/123 |
| 87 | NON_BEHAVIORAL | R4 | REPRODUCED | FAILURE / 1 | 37/0/1 |
| 91 | NON_BEHAVIORAL | R1 | REPRODUCED | FAILURE / 1 | 111/0/2 |
| 104 | NON_BEHAVIORAL | R1 | REPRODUCED | FAILURE / 1 | 5/0/1 |
| 105 | NON_BEHAVIORAL | R1 | REPRODUCED | FAILURE / 1 | 309/6/4 |
| 108 | NON_BEHAVIORAL | R1 | REPRODUCED | FAILURE / 1 | 5/0/3 |
| 109 | NON_BEHAVIORAL | R3 | REPRODUCED | FAILURE / 1 | 223/0/54 |
| 112 | NON_BEHAVIORAL | R8 | REPRODUCED | FAILURE / 1 | 62/0/1 |
| 116 | NON_BEHAVIORAL | R10 | REPRODUCED | FAILURE / 1 | 0/0/0 |
| 127 | NON_BEHAVIORAL | R8 | REPRODUCED | FAILURE / 1 | 62/0/1 |
| 138 | NON_BEHAVIORAL | R1 | REPRODUCED | FAILURE / 1 | 59/20/0 |
| 140 | NON_BEHAVIORAL | R8 | REPRODUCED | FAILURE / 1 | 904/1/0 |
| 158 | BEHAVIORAL | R12 | REPRODUCED | FAILURE / 1 | 26/1/0 |
| 161 | NON_BEHAVIORAL | R11 | REPRODUCED | FAILURE / 1 | 302/1/0 |
| 163 | BEHAVIORAL | R12 | REPRODUCED | FAILURE / 1 | 617/2/0 |
| 178 | NON_BEHAVIORAL | R1 | REPRODUCED | FAILURE / 1 | 1/0/1 |
| 181 | BEHAVIORAL | R12 | REPRODUCED | FAILURE / 1 | 57/2/0 |
| 183 | NON_BEHAVIORAL | R1 | REPRODUCED | FAILURE / 1 | 19/0/1 |
| 188 | NON_BEHAVIORAL | R8 | REPRODUCED | FAILURE / 1 | 62/0/1 |
