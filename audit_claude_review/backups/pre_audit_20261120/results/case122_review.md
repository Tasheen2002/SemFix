# Case 122 review

simplelocalize-cli updates jackson-databind from 2.9.10.5 to 2.12.6.1 in the root POM. This is the sole archived source/POM change and the only JAR change on the affected test classpath. Jackson Core remains at 2.9.8 and Jackson Annotations at 2.11.0.

Both original images were run. PRE succeeds with 48 tests, zero failures/errors/skips. BREAKING reports 40 tests, zero failures, seven errors and zero skips. Maven and 19 fresh Surefire XML reports per phase agree. Six errors name NoClassDefFoundError for com/fasterxml/jackson/core/util/JacksonFeature, with ClassNotFoundException underneath. One further error reports failed initialization of ClientBodyBuilders. The smaller reported test count is not labeled as skipped tests; Maven reports zero skips.

Inspection of the actual retained Core 2.9.8 JAR confirms JacksonFeature is absent. Updated Databind DeserializationContext bytecode invokes JacksonFeatureSet.isEnabled with a JacksonFeature parameter descriptor. The reference scan also finds related JacksonFeatureSet uses; its metadata distinguishes prefix matches from the confirmed exact JacksonFeature descriptor. The missing required Core type establishes a binary dependency incompatibility, supporting NON_BEHAVIORAL with binary_linkage_incompatibility=YES.

Independent human review remains pending, with reviewer/final labels blank. Automated triage is separate from this evidence-backed assessment. Source/POM snapshots, both original runs, fresh reports, JAR hashes and disassembly are preserved. Explicit Maven outcomes establish builds because the tee pipeline masks Maven failure in Docker's exit code. No repair or dependency substitution was attempted.
