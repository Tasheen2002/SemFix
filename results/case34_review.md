# Case 34 review

The `directory-scimple` upgrade of Java EE API from 7.0 to 8.0.1 is a **non-behavioural binary linkage incompatibility**, pending human review.

PRE reported 717 tests, including 17 skips, with zero failures or errors. BREAKING reported 686 tests, including 15 skips and 10 errors, with zero assertion failures. The `scim-server-common` module fails and Maven skips the downstream modules. The reactor totals come from both the Maven summaries and fresh Surefire reports.

Nine errors are `AbstractMethodError` for `Response.ResponseBuilder.status(int, String)`. Disassembly shows that Java EE API 8.0.1 adds this abstract overload to the class used at runtime. The resolved RESTEasy 3.0.11.Final `ResponseBuilderImpl` only implements `status(int)`. The tenth error is Mockito's `UnfinishedStubbingException`, which points to the same test line as one of the abstract method errors.

The project POM changes only the Java EE API version. The affected classpath also changes the transitive JavaMail version, and RESTEasy stays at 3.0.11.Final. The image command pipes Maven through `tee`, which masks the failing Maven exit code. Logs have prefix `2f9d75d4` under `logs/batch_triage/`, and the archives, JARs and disassembly are under `logs/case34_evidence/`.
