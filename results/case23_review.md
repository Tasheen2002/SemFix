# Case 23 review

The `IDS-Messaging-Services` upgrade of `junit-platform-surefire-provider` from 1.0.3 to 1.3.2 is a **non-behavioural binary linkage incompatibility**, pending human review.

PRE passed 32 tests across the reactor. BREAKING passed 20 tests in earlier modules and then failed in the `broker` module before running its tests. Surefire therefore reports zero test errors in completed test reports, while Maven reports a build failure.

The sole archived source or POM difference is the provider version in `broker/pom.xml`. Maven still uses Surefire Plugin 2.19.1. Its reported plugin classpath includes the upgraded JUnit provider 1.3.2, `common-java5` 2.22.0 and `surefire-api` 2.19.1. The test runner encounters `NoSuchMethodError` for `StringUtils.requireNonNull(Object)`. Disassembly of the resolved `common-java5` 2.22.0 JAR confirms that its `StringUtils` lacks that method.

A separate candidate for the same project has the analogous failure in `paris`. Case 23 changes the dependency in `broker`, which fails earlier in the reactor. Both image commands pipe Maven through `tee`, and the containers exit zero. Maven's build summaries and the fresh Surefire reports establish the outcomes.

The logs have prefix `1cd22b76` under `logs/batch_triage/`, and the source, reports, resolved JAR and disassembly are under `logs/case23_evidence/`.
