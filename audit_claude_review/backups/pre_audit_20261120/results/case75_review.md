# Case 75 review

dropwizard-pac4j updates Jetty Server 9.4.35.v20201120 to 9.4.50.v20221201. The root POM version is the only archived source/POM change. The affected test classpath retains Jetty Util 9.4.35.v20201120.

PRE passes all 16 tests. BREAKING runs the same 16 tests with ten errors and zero failures or skips in Maven's aggregate result. Raw Surefire XML reports 22 entries and 16 errors because each of six end-to-end tests has an HTTP connection error and a separate teardown error. Counting each test once reconciles the XML with Maven. Both forms are archived.

All ten errored tests record a teardown AbstractMethodError through Dropwizard's shutdown path. Disassembly shows that the resolved Jetty Util interface LifeCycle.Listener declares lifeCycleFailure as abstract. The newer Jetty Server's AllowedResourceAliasCheckListener implements lifeCycleStarted but omits lifeCycleFailure. The runtime fails dispatch to that missing implementation. The end-to-end tests also report unexpected end of file from the server. The confirmed linkage failure supports a non-behavioural classification pending independent review. The HTTP symptom was not isolated separately.

Both original runs, source, reports and resolved JARs are archived. Explicit Maven output establishes failure because the image pipes Maven through tee.
