# Case 16: non-behavioural linkage incompatibility

Case ID: `1750bac074c30b06ae5cdff7a25db401a4f45de2`  
Project: `pac4j/dropwizard-pac4j`  
Update: `com.fasterxml.jackson.core:jackson-databind` **2.10.5.1 → 2.13.4**  
Automated triage: `AUTO_NON_BEHAVIORAL_CANDIDATE`  
Agent assessment: **NON_BEHAVIORAL**. Human review remains pending; reviewer labels and final label are empty.

| Environment | XML reports | Reported tests | Failures | Errors | Skipped | Maven result |
|---|---:|---:|---:|---:|---:|---|
| PRE | 4 | 16 | 0 | 0 | 0 | SUCCESS |
| BREAKING | 4 | 16 | 0 | 16 | 0 | FAILURE |

Both images use Linux AMD64, Java 11.0.19, and Maven 3.9.2. The image command is `mvn clean test -B | tee %s.log`. Because the pipeline does not propagate Maven's exit code, both containers exit 0. BREAKING is nevertheless a Maven failure, established by `BUILD FAILURE` and all sixteen Surefire errors. No second test run was needed. Version-only checks were run separately from the same images after the reproduction containers stopped.

The four test classes are `EndToEndServletTest` (3 tests), `EndToEndTest` (3), `DefaultConfigurationTest` (6), and `BundleFactoryTest` (4). All pass in PRE and all error in BREAKING.

The first meaningful BREAKING exception is:

```text
java.lang.NoClassDefFoundError: com/fasterxml/jackson/core/util/JacksonFeature
    at com.fasterxml.jackson.databind.ObjectMapper.<init>(ObjectMapper.java:673)
Caused by: java.lang.ClassNotFoundException: com.fasterxml.jackson.core.util.JacksonFeature
```

The test classpath resolves Jackson Core 2.10.5 and Annotations 2.10.5 in both environments. Databind alone changes from 2.10.5.1 to 2.13.4. The only POM change and the only classpath path difference are that Databind version. All 26 archived source/resource files match by SHA-256. Classpath path equality does not establish byte identity for every dependency JAR.

Direct inspection of the archived `jackson-core-2.10.5.jar` confirms that `com/fasterxml/jackson/core/util/JacksonFeature.class` is absent. The Databind JAR's embedded Maven metadata confirms version 2.13.4. Its `DeserializationContext` bytecode references the method descriptor `(Lcom/fasterxml/jackson/core/util/JacksonFeature;)Z`; this is an exact reference to the missing type. The error surfaces during ObjectMapper construction. ObjectMapper itself does not contain a direct reference to that class; an initial inspection recorded that distinction and the refined inspection locates the reference in DeserializationContext. Saved `javap` output supports the inspection.

This is a genuinely unavailable runtime type, rather than a secondary `Could not initialize class` message after a behavioural change. Successful source compilation does not make it a semantic breakage. The incompatible library combination prevents normal application setup before the intended behaviour can be compared.

Case 8 involves the same project and a different Databind target (2.14.1). Case 16 was reproduced independently; its versions and logs have not been copied from Case 8. Keep related cases grouped by project/family in future retrieval/evaluation splits.

No semantic repair was attempted. No patch or verified-repair entry has been created. The verified repair corpus still contains only Case 14.

Evidence paths relative to the workspace:

- `logs/batch_triage/1750bac0_pre.log` and `1750bac0_breaking.log`
- `logs/case16_evidence/pre/surefire-reports/` and `breaking/surefire-reports/`
- `logs/case16_evidence/pre/src/` and `breaking/src/`
- `logs/case16_evidence/source_comparison.json` and `dependency_update.diff`
- `logs/case16_evidence/jar_inspection_verified.json`
- `logs/case16_evidence/breaking/jackson-core-2.10.5.jar`
- `logs/case16_evidence/breaking/jackson-databind-2.13.4.jar`
- `logs/case16_evidence/breaking/ObjectMapper_javap.txt` and `DeserializationContext_javap.txt`
- `logs/case16_evidence/pre_environment.txt` and `breaking_environment.txt`
- `logs/case16_evidence/pre_container_state.json` and `breaking_container_state.json`
- `results/case16_assessment.json`
- `scripts/append_case_16.py`

PRE image digest: `sha256:833597a87c7d1fa3486b8c071d5546434fffb28ce698fdd255e0afc574031d48`  
BREAKING image digest: `sha256:a5e34cfe0b9be3562067de593223ca6955efc3139304c40dc3f4e95a11313444`

Pre-run backups are in `results/backups/before_case16_20261108_184650_132/`. Historical records and raw evidence are preserved. The agent assessment is saved in the classification CSV with `review_status=PENDING_HUMAN_REVIEW`; it is not an independently confirmed classification.
