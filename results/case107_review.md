# Case 107 review

pgpverify-maven-plugin updates junit-jupiter-params from 5.9.1 to 5.9.2. The root POM version is the only changed archived source/POM. Fresh test classpaths show only the Params JAR changes; JUnit Jupiter API remains 5.9.1 and Platform Commons remains 1.9.1.

Both original images were run. PRE succeeds with 300 tests, no failures, errors or skips. BREAKING fails with 161 reported tests, zero failures, 15 errors and no skips. Maven totals agree with 28 fresh Surefire XML reports per phase. The smaller test count reflects parameter-source initialization failing before affected invocations can be generated; it is not a count of skipped or passing tests.

All 15 errors name NoSuchMethodError for ReflectionUtils.parseQualifiedMethodName(String), returning String[]. The first failing frame is MethodArgumentsProvider.getFactoryMethodBySimpleOrQualifiedName. Disassembly of the resolved Params 5.9.2 JAR confirms the static call, and disassembly of retained Platform Commons 1.9.1 confirms the method is absent. This is a JUnit module binary incompatibility, supporting a non-behavioral assessment despite the patch-level update.

Automated screening and the curated agent assessment remain separate. Independent human review is pending, with reviewer/final labels blank. Explicit Maven output and fresh XML establish the outcomes because the original tee pipeline masks Maven failure in the container exit code. No repair or substitution control was run.
