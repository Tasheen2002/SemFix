# Case 17: inconclusive reproduction

Case ID: `18102f7a87e7ab8308a86208d47696c060110d0c`  
Project: `ORCID/ORCID-Source`  
Update: Jackson Databind **2.10.0 → 2.12.6.1**  
Automated triage: `AUTO_BASELINE_PROBLEM`  
Recorded assessment: **UNCERTAIN**, pending baseline resolution and human review. Reviewer 1, Reviewer 2, and final labels remain empty.

The observed update failure is a **non-behavioural linkage candidate**, but the complete case does not meet the passing-PRE criterion. It must not be counted as a confirmed semantic or nonsemantic case in evaluation.

| Environment | Fresh XML reports | Reported tests | Failures | Errors | Skipped | Outcome |
|---|---:|---:|---:|---:|---:|---|
| PRE | 385 | 4104 | 1 | 0 | 0 | Full Maven BUILD FAILURE; container exit 1 |
| BREAKING | 39 | 222 | 0 | 13 | 0 | Deliberately interrupted; container exit 143; counts are partial |

Both images use AMD64 Linux, Java 11.0.19, Maven 3.9.2, and `mvn clean test -B` from `/ORCID-Source`. PRE ran for about 21 minutes through all fourteen reactor modules. Its last module, `orcid-message-listener`, failed; earlier reactor modules passed. BREAKING was stopped after repeated missing-class errors during Spring initialization in `orcid-core`, because the full baseline was already invalid and continuing would repeat the same startup failure. No full BREAKING Maven outcome is claimed.

The PRE failure is `org.orcid.listener.converter.OrcidRecordToSolrDocumentTest.convertTest:62`: expected five current affiliation names, observed two. The converter's `setAffiliationNames()` calls `LocalDate.now()` at line 816. The test loads `record_3.0/samples/read_samples/record-3.0.xml` from ORCID Model 3.0.9. Three affiliations expected to be current (employment, invited position, and qualification) end in 2025. At the run date, 8 November 2026, those are past affiliations; only membership and service have no end date. This statically explains the observed count of two. No clock-controlled rerun or test modification was performed, so the explanation is recorded as evidence-backed analysis rather than a verified baseline correction.

The BREAKING errors are rooted in:

```text
java.lang.NoClassDefFoundError: com/fasterxml/jackson/core/util/JacksonFeature
Caused by: java.lang.ClassNotFoundException: com.fasterxml.jackson.core.util.JacksonFeature
```

Spring reports bean-construction failures around `bibtexManagerV3`; the nested missing-class exception is the relevant library incompatibility, not a behavioural Spring change. The completed `SourceInActivitiesTest` report has eleven errors in BREAKING and eleven passing tests in PRE. Other completed core reports account for the remaining two reported errors. Utility and persistence tests account for 209 completed, error-free tests before core. Further tests were running or aborted when the container stopped; they are not included in the completed-report total.

For the compared core test, the runtime classpath retains Jackson Core 2.10.1 and Annotations 2.9.5; only the Databind path changes to 2.12.6.1. Direct JAR inspection confirms that Core 2.10.1 lacks `JacksonFeature.class` and Databind's `DeserializationContext` references the missing type in a method descriptor. All 4,574 archived source/POM files match except the root POM, whose single diff changes Databind's version. Path comparisons do not establish byte identity of every dependency. BREAKING also requested snapshot metadata, and invalid-repository-metadata warnings remain in the raw log.

The image contains inherited Surefire reports in modules not reached by BREAKING. `scripts/archive_bump_evidence.py` includes reports only where the current log explicitly records deletion of that module's target directory. It streams the container archive without extracting its paths. PRE's fresh XML totals were independently matched to the sum of Maven module aggregate lines. BREAKING's completed utility and persistence report totals match their module aggregates; core reports are partial because the run was interrupted. The batch triage script's last-summary fields (PRE 116; BREAKING 200) are not full reactor totals and are annotated accordingly in its new Case 17 row.

Saved artifacts:

- `logs/batch_triage/18102f7a_pre.log` and `18102f7a_breaking.log`
- `logs/case17_evidence/pre/artifacts.tar` and `breaking/artifacts.tar`: sources, POMs, and fresh test reports
- `logs/case17_evidence/pre/archive_summary.json` and `breaking/archive_summary.json`: provenance, per-class reports, classpaths, source hashes, image IDs/digests, container states
- `logs/case17_evidence/pre/archive_verification.json`: PRE count cross-check
- `logs/case17_evidence/breaking_interruption.json`: explicit stop reason and time
- `logs/case17_evidence/baseline_fixture_analysis.json`, `pre/record-3.0.xml`, and `pre/orcid-model-3.0.9.jar`
- `logs/case17_evidence/source_comparison.json`, `dependency_update.diff`, and `jar_inspection.json`
- `logs/case17_evidence/breaking/jackson-core-2.10.1.jar` and `jackson-databind-2.12.6.1.jar`
- `results/case17_assessment.json`, `scripts/append_case_17.py`, and `repairs/case17_status.md`

No source patch, test change, dependency rollback, clock change, or verified repair was made. Preserve these unmodified runs. The next step for resolving this case is an isolated historical-clock baseline, or an explicitly documented deterministic fixture adjustment, followed by scoped reproduction and human adjudication. A baseline workaround must be distinguished from a repair of the dependency update.

Pre-run backups: `results/backups/before_case17_20261108_185957_531/`. Cases 1–16 and Case 14's verified repair are preserved. The new classification row is an agent assessment with `review_status=PENDING_HUMAN_REVIEW`, not a human-confirmed label.
