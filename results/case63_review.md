# Case 63 review

JsonUnit updates surefire-junit4 from 3.0.0-M5 to 3.0.0-M6 in tests/test-junit4/pom.xml. The nested module POMs were copied separately because the archive helper only captures POMs at the top two levels. The copied POMs differ by the provider version. The other archived source/POM files match.

PRE reports 3,566 tests with 10 skips and succeeds. BREAKING reports 3,564 tests with nine skips and zero failures or errors in completed modules. The test-junit4 module fails in Surefire before it runs tests. Fresh XML and Maven reactor totals agree. The automated screen's last module summary is one test and does not represent the reactor total.

The Maven plugin stays at 3.0.0-M5 while the updated provider brings Surefire API 3.0.0-M6 into the plugin realm. The M5 AbstractSurefireMojo invokes the DirectoryScannerParameters constructor with a boolean argument. Disassembly shows the M6 API's public constructor omits that argument. Maven reports NoSuchMethodError for the older signature, supporting a non-behavioural test runner binary incompatibility assessment pending independent human review.

The 5275fc9e logs and case63_evidence directory contain both original runs, fresh reports, the nested POMs, resolved JARs and bytecode inspection. The tee pipeline masks Maven's exit status.
