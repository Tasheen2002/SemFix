# Case 154 review

PRE: BUILD SUCCESS, 16 tests, no failures/errors/skips. BREAKING: BUILD FAILURE, 16 tests, 16 NoClassDefFoundError errors, no failures/skips. Errors name com.fasterxml.jackson.core.util.JacksonFeature, with ClassNotFoundException as the cause; initialization fails through ObjectMapper and Dropwizard bootstrap before the intended assertions.

Both original Docker images were run. All archived client source hashes match; only pom.xml changes jackson-databind 2.10.5.1 to 2.12.7.1. The actual test classpath retains jackson-core and jackson-annotations 2.10.5. Direct inspection confirms JacksonFeature is absent from the three resolved Jackson core-family JARs. Binary-reference scanning finds no reference in PRE Databind, but finds references in updated DeserializationContext, TreeTraversingParser, TokenBuffer$Parser and TokenBuffer. Their disassemblies and JAR hashes are archived by scripts/inspect_case_154_missing_class_reference.py.

Agent assessment: NON_BEHAVIORAL, binary linkage flag YES. This is a missing runtime class in mismatched Jackson components, rather than a confirmed change to the behavior of a successfully linked API call.

Evidence: logs/case154_evidence/ including missing_class_references.json and original logs logs/batch_triage/cd1b75ae_*.log. Independent human review pending; final label blank. No repair attempted.
