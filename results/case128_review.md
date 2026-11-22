# Case 128 review

Both original IDS-Messaging-Services images ran. PRE passed 32 tests. BREAKING stopped in messaging with 18 tests, one failure and five errors. The assertion in IdsMessageUtilsTest wraps the same missing JsonKey type as the five direct errors. Maven totals agree with 19 and 15 fresh reports respectively. The sole archived source/POM change is the Databind version in core/pom.xml.

The original messaging XML shows the Maven launcher classpath. Separate resource-origin tests in the original images identify the module's Jackson JARs. Databind changes from 2.9.10.8 to 2.13.2.1 and Core from 2.9.10 to 2.13.2. Jackson Annotations stays at 2.11.2. The resource loader cannot find JsonKey in either diagnostic, and the updated Databind bytecode directly references the missing class. The original error and artifact inspection establish binary incompatibility.

The diagnostic passes one resource-inspection test in each image and its results are archived separately. The assessment is NON_BEHAVIORAL pending independent human review.
