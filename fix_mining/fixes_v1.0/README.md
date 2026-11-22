# Fix dataset v1.0 (frozen 2026-11-21)

This is a validated fix for every one of the 56 BEHAVIORAL cases in classification v1.0, each tested on its original BUMP BREAKING image. **Do not edit these files.** A later change should produce v1.1 with a change note.

| Reference group | Cases | Author | How a repair tool is judged |
|---|---:|---|---|
| DEVELOPER_FIX | 21 | The project's developers (minimal backport, or replayed commit for Case 171) | Compare with this fix, plus tests |
| DERIVED_MINIMAL_FIX | 7 | Derived from the developer fix (pay-adminusers: logback 1.3.5 instead of the Dropwizard 3 migration) | Compare with this fix, plus tests |
| RESEARCHER_WRITTEN_ONLY | 28 | Researcher-written (Claude). **Not a reference answer**; it only shows the case can be fixed. | Tests only: failing tests pass and nothing else breaks |

## Validation rule (all 56 pass)

Each fix was checked as follows:
- **Image:** a fresh `--rm` container of the original BREAKING image; the workspace was never mounted.
- **Apply:** `git apply --check`, then `git apply`.
- **Build:** `mvn clean test -B`. For btrplace (Cases 163, 168) only the `json` module and the modules it needs were built (`-pl json -am`).

A fix passes only if:
- the patch applies;
- at least one test runs, and every originally failing test class runs;
- BUILD SUCCESS with 0 failures, 0 errors, and `MAVEN_EXIT=0`.

This was an AI validation (Claude), not a human review.

## Known limitations

- **Failing-class names are missing for Cases 14, 114, 163 and 168** (h2 and TestNG `TestSuite` logs). For these, "target tests ran" rests on the whole suite passing.
- **"Nothing else breaks" was judged against the BREAKING run, not yet against the PRE test list.** The repair harness (next step) adds the PRE comparison.
- **Case 171's reference fix has two adjustments:** slf4j-api kept at 2.0.0, and the jax-rs-pac4j SNAPSHOT replaced by the 6.0.0 release.
- **Some fixes download artifacts** from Maven Central when run (new library versions not cached in the images).

## Files

| Path | Contents |
|---|---|
| `fix_index.csv` | **Start here.** One row per case: group, author, frozen patch path and SHA-256, validation counts, log |
| `reference_fixes/` | 28 patches (21 developer + 7 derived) |
| `researcher_written_fixes/` | 28 patches (not reference answers) |
| `developer_original_commits/` | The developers' full original commits as diffs, plus the Case 171 replay source |
| `failed_attempts/` | Superseded attempts kept as a record (Case 181 attempts 1–2, Case 171 derived and researcher-written attempts 1–7) |
| `validation/` | Recipes, final results and superseded results for both groups |
| `logs/` | The final validation log for every case |
| `developer_fixes.csv`, `fix_summary.json`, `version_trace.json`, `pr_meta.json`, `cases.json`, `failing_tests.json` | Mining data |
| `repo_snapshot.json` | The default-branch commit of each of the 18 mined repositories, to reproduce the mining |
| `scripts/` | Every script used (mining, validation, re-check, catalogue, this freeze) |
| `SHA256SUMS.txt` | Hashes of every frozen file |
