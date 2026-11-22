# Manual verification of cases

These scripts are for the human reviewer who wants to rerun cases personally rather than rely only on the recorded logs. They are optional: the labels do not depend on a rerun, because the original logs already record every outcome.

## One case

From PowerShell, in this folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\verify_case.ps1 -Case 69          # BREAKING run + summary + proposed label
powershell -ExecutionPolicy Bypass -File .\verify_case.ps1 -Case 69 -Pre     # also run PRE
powershell -ExecutionPolicy Bypass -File .\verify_case.ps1 -Case 69 -Tree    # also print the dependency tree (downloads the Maven dependency plugin)
powershell -ExecutionPolicy Bypass -File .\verify_case.ps1 -Case 69 -SummaryOnly   # re-read saved logs, no Docker
```

For each case the script:
- runs the original BUMP image in a fresh `--rm` container named `manual-case<N>-<phase>`, pulling the image if it is not present;
- saves the full log as UTF-8 to `logs\case<N>_<phase>.log`, with Maven's real exit code as `MAVEN_EXIT=`;
- prints the build result, test counts, reactor status, the first failing tests, the `Caused by` chain, linkage signals and any SLF4J console lines;
- shows the proposed label, its rule and the initiating cause, plus the three things to check.

Tested on Case 104 (2026-11-20). It reproduced the original BREAKING result (BUILD FAILURE, 5 tests, 1 error, `NoSuchMethodError checkDocumentPermissions`) in 34 seconds.

## All 47 sample cases

```powershell
powershell -ExecutionPolicy Bypass -File .\run_sample.ps1                  # all sample cases, resumable
powershell -ExecutionPolicy Bypass -File .\run_sample.ps1 -Cases 49,67,69  # a subset
```

Summaries go to `summaries\case<N>.txt`.
- **Time:** most cases take 1–5 minutes, but a few large builds take much longer, so expect several hours in total.
- **Disk:** images that are not on the machine are pulled at 0.5–1 GB each. Remove them afterwards with `docker rmi` if you need the space.

## Recording the result

Write your label in `..\verification_plan\human_sample.csv` (`human_label`, `human_confidence`, `human_notes`). `..\verification_plan\human_review_packet.md` has the recorded evidence for the same cases, if you want to compare.
