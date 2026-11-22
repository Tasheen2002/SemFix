# Case 157 review

PRE: BUILD SUCCESS, 69 reported tests across the reactor, no failures/errors, 2 skipped. BREAKING: BUILD FAILURE, 57 reported tests in avans, 4 failures, 46 errors, 2 skipped. Later reactor modules do not run after avans fails; the absent later executions are not extra skipped or passing tests.

All 46 XML errors are NoClassDefFoundError for com.fasterxml.jackson.core.util.JacksonFeature, with ClassNotFoundException as the cause. ObjectMapper cannot initialize. Four HTTP assertions also fail while server-side traces show the same Jackson class-loading failure. The source uses Assert.assertEquals(actualResponse, expectedLiteral), reversing JUnit's conventional arguments: expected:<500> but was:<200> therefore means the actual response is 500 and the test requires 200. The comparison failure similarly displays the actual HTML error response as the 'expected' side. These messages do not establish a separate successful-response semantic change.

Both original Docker images were run. All archived client source hashes match; only avans/pom.xml changes jackson-databind 2.3.3 to 2.13.3. Actual avans test classpaths retain jackson-core 2.4.2 while jackson-annotations changes transitively from 2.3.0 to 2.13.3. JacksonFeature is absent from the resolved core-family JARs. Binary-reference scanning finds no reference in PRE Databind and four references in updated Databind, including DeserializationContext. JAR hashes and caller disassemblies are archived.

Agent assessment: NON_BEHAVIORAL, binary linkage flag YES. Evidence: logs/case157_evidence/ including missing_class_references.json; original logs logs/batch_triage/d3c95ff1_*.log. Independent human review pending; final label blank. No repair attempted.
