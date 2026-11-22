# Case 26 review

The `webapp` upgrade of Log4j Core from 2.16.0 to 2.19.0 is a **non-behavioural binary linkage incompatibility**, pending human review.

PRE reported 122 tests, including two skips, with zero failures or errors. BREAKING reported 103 tests, including one skip and 90 errors, with zero assertion failures.

Log4j API remains at 2.16.0. The updated Core JAR references `org.apache.logging.log4j.util.ServiceLoaderUtil`, which is absent from the resolved API JAR. The BREAKING reports show the missing class and the corresponding `ClassNotFoundException`. The failed logging initialization accounts for the subsequent initialization errors.

The archived sources match and the only POM change is the Log4j Core version. Maven summaries match the fresh reports. Both containers return zero because the image command pipes Maven output through `tee`. The build logs have prefix `20b27209` under `logs/batch_triage/`, and the reports and inspected JARs are under `logs/case26_evidence/`.
