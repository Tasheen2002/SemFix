# Case 44 review

The dropwizard-pac4j upgrade of Jersey Server from 2.32 to 2.36 is provisionally **non-behavioural**, pending human review.

PRE passed all 16 tests. BREAKING reported 16 tests with 10 errors and zero assertion failures or skips. Jersey ApplicationHandler initialization fails with NoClassDefFoundError for `org.glassfish.jersey.internal.DynamicFeatureConfigurator`, caused by ClassNotFoundException.

The affected classpath resolves Jersey Server 2.36 with Jersey Common 2.32 and other Jersey modules at 2.32. The actual Common JAR lacks the requested class, and Server's ApplicationHandler references it. The only archived project POM change is the Jersey Server version. The resolved classpath also loses jersey-media-jaxb 2.32 as a transitive effect.

Fresh Surefire totals agree with Maven. The image command pipes Maven through tee, masking its failing exit code. Logs have prefix `3b7f524a` under `logs/batch_triage/`. The source archives, reports, image provenance and inspected JARs are under `logs/case44_evidence/`.
