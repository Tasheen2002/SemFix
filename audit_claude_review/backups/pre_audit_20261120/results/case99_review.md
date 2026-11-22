# Case 99 review

dropwizard-pac4j updates Jetty Server 9.4.35.v20201120 to 9.4.48.v20220622. Only the root POM changes among archived source and POM files. The affected test classpath retains Jetty Util 9.4.35.v20201120.

PRE passes all 16 tests. BREAKING reports ten errors across 16 tests. Raw Surefire XML contains six extra entries because six end-to-end tests record an HTTP error and a separate teardown error. Counting each test once matches Maven.

The affected tests record a shutdown AbstractMethodError. The retained LifeCycle.Listener declares lifeCycleFailure as abstract. Disassembly shows the upgraded AllowedResourceAliasCheckListener lacks the method. The binary incompatibility supports a non-behavioural assessment pending independent review. The HTTP connection errors were not isolated separately.
