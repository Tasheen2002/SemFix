# Repair harness (the checker)

The checker decides whether a candidate patch **repairs** a BUMP BEHAVIORAL case. Every repair experiment uses it, and it is the same strict judge for every case, condition and model.

**Version:** v2.2 (2026-11-23). This was an AI evaluation (Claude), not a human review.

## How a patch is judged

A fresh `--rm` container of the case's original BUMP BREAKING image is started, the patch is applied and the original test command is run. The workspace is never mounted. A patch is **REPAIRED** only if all five checks pass:

| Check | Requirement | What it stops |
|---|---|---|
| APPLIES | `git apply --check`, then `git apply` | Malformed patches |
| BUILD | BUILD SUCCESS and `MAVEN_EXIT=0` | Broken builds |
| TARGET_FIXED | Every originally failing test class runs and passes | Patches that don't fix the breakage |
| NO_REGRESSION | Every test class that passed in **PRE** (`baselines/pre_tests.json`: 3,304 classes; totals match the recorded PRE counts for 56/56) runs and passes. A missing class fails | **Deleting or skipping tests** |
| UPDATE_KEPT | `dependency:tree` resolves the updated dependency at the new version or higher | **Reverting the update** |

**Verdicts:**
- **REPAIRED**, or **NOT_REPAIRED**;
- **INCONCLUSIVE**: infrastructure, never the patch's fault. Either the network was unreachable, or the dependency tree was unavailable twice.

**Robustness rules, each added after a real incident:**

| Version | Rule | Incident |
|---|---|---|
| v2 | `dependency:tree` runs as `test-compile dependency:tree`, retried once with the pinned plugin 3.6.1 | Multi-module builds (btrplace, sparql-anything) could not see sibling modules; a plugin 2.8 download failed (Case 78) |
| v2 | One fresh re-run for test-only failures; a pass on attempt 2 is recorded as `flaky` | Timing test `delay` measured 0 ms (Case 148) |
| v2.1 | Network errors in Maven's or Docker's own lines → INCONCLUSIVE. A version that does not exist (`Could not find artifact`) stays the patch's fault, and network errors printed by *tests* are ignored | An internet outage (22 Nov, 22:05–22:12) turned 23 good fixes into "failures" |
| v2.2 | The flaky re-run is also allowed when a random failure stopped the reactor (later modules did not run), but never after a compile error | A junit-quickcheck random property test failed once (Case 89) |

## Validation of the checker

- **Self-test** (`scripts/run_selftest.sh`, `selftest/expected.json`): **4/4 PASS**.

| Patch | Expected | Caught by |
|---|---|---|
| Reference fix (Case 2) | REPAIRED | – |
| No-op | NOT_REPAIRED | TARGET_FIXED |
| Revert slf4j 2.0.4 → 1.7.36 | NOT_REPAIRED | **Only UPDATE_KEPT**: the build and all tests passed |
| Delete the failing test (Case 13) | NOT_REPAIRED | TARGET_FIXED and NO_REGRESSION: the build passed with 320 tests |

- **All 56 frozen fixes** (`runs/frozen_fixes_v2/`): **56/56 REPAIRED** (21 developer, 7 derived, 28 researcher-written). Case 148 was flaky and passed on attempt 2. So no validated fix breaks a PRE-passing test.
  - The results were produced under v2, v2.1 and v2.2, which differ only in how infrastructure and flakiness are handled.
  - `scripts/reevaluate_logs.py` re-judged every saved log with the v2.2 rules: 56 REPAIRED, 0 changed (`runs/frozen_fixes_v2/reevaluation_v2.2.json`).
  - The outage runs are kept in `runs/frozen_fixes_v2/network_outage_2026-11-22/`, and the superseded Case 89 run in `superseded/`.

## Known limitations

- **Class-level baseline:** Surefire names test methods only when they fail.
- **Case 15's image is ARM-only** (`image_architectures.json`; the other 55 are amd64), so it runs under emulation: slower, and timing tests can be flakier.
- **Btrplace (Cases 163, 168)** is checked with `-pl json -am`; the full build takes hours.
- **Missing failing-class names:** Cases 14, 114, 163 and 168 have none recorded, so TARGET_FIXED uses the whole run.
- **Network access:** new dependency versions are downloaded from Maven Central during a run.

## Files

| Path | Contents |
|---|---|
| `scripts/evaluate_patch.py` | The checker (one case, one patch) |
| `scripts/run_batch.py` | Many cases, resumable; re-runs INCONCLUSIVE cases once; writes `summary.json`/`summary.csv` |
| `scripts/build_pre_baselines.py` | Builds `baselines/pre_tests.json` from the PRE logs |
| `scripts/reevaluate_logs.py` | Re-judges saved logs with the current rules, without Docker |
| `scripts/make_selftest_patches.py`, `scripts/run_selftest.sh` | The adversarial self-test |
| `runs/<label>/` | One JSON and one log per case per run |
