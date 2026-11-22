# Case 84 review

dropwizard-pac4j updates Jetty Server 9.4.35.v20201120 to 9.4.47.v20220610. The sole archived source/POM change is the root POM version. The affected test classpath retains Jetty Util 9.4.35.v20201120.

PRE passes all 16 tests. BREAKING reports 16 tests and ten errors. Raw Surefire XML has six additional entries because six end-to-end tests record both an HTTP connection error and a teardown error. Counting each test once matches Maven.

Ten tests record a shutdown AbstractMethodError. The retained LifeCycle.Listener declares lifeCycleFailure as abstract. The newer AllowedResourceAliasCheckListener lacks that implementation, as confirmed by disassembly of both resolved JARs. This supports a non-behavioural binary incompatibility assessment pending independent review. Six tests also report an unexpected end of file from the server. The HTTP symptom was not isolated separately.

Both Maven runs, raw XML, unique-test counts and resolved JARs are archived. Explicit Maven output establishes failure because the image pipes Maven through tee.
