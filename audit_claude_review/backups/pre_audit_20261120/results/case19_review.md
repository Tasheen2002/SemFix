# Case 19 review

The `pgpverify-maven-plugin` upgrade of `junit-jupiter-params` from 5.9.3 to 5.10.0 causes a **non-behavioural binary linkage incompatibility**, pending human review. Automated triage recorded `AUTO_NON_BEHAVIORAL_CANDIDATE`.

| Run | Reported tests | Failures | Errors | Skipped | Maven result |
|---|---:|---:|---:|---:|---|
| PRE | 300 | 0 | 0 | 0 | BUILD SUCCESS |
| BREAKING | 161 | 0 | 15 | 0 | BUILD FAILURE |

The fresh Surefire reports match the Maven totals. All 15 errors, across nine test classes, occur while JUnit's `MethodArgumentsProvider` resolves a parameter source. It calls `ClassLoaderUtils.getClassLoader(Class)` and the JVM throws `NoSuchMethodError`. Errors during argument resolution prevent affected parameterized invocations from being generated, so the two reported totals cover different numbers of invocations.

The test classpath retains JUnit Jupiter API 5.9.3 and JUnit Platform Commons 1.9.3. Disassembly of the resolved Params 5.10.0 JAR shows the call to `getClassLoader(Class)`. Disassembly of `ClassLoaderUtils` from the resolved Platform Commons 1.9.3 JAR shows that the method is absent. The only content change across 346 archived source and POM files is the Params version in the root POM.

The image commands pipe Maven through `tee`, and both containers exited 0. Maven's build summaries and Surefire reports establish the outcomes. The original logs are under `logs/batch_triage/` with prefix `19249139`. Fresh reports, source archives, the resolved JARs and disassembly are under `logs/case19_evidence/`.
