# Case 135 review

Both original IDS-Messaging-Services images ran. PRE passed 32 tests. BREAKING stopped in messaging with 18 tests, one assertion failure and five errors. The IdsMessageUtilsTest assertion wraps the same missing JsonKey type as the five direct errors. Maven totals agree with 19 and 15 fresh reports respectively. The sole archived source/POM change is the Databind version in core/pom.xml.

The original messaging XML reports only the Maven launcher classpath. A separate resource-origin test in each original image confirms the module's selected dependencies. Databind changes from 2.9.10.8 to 2.13.3 and Core from 2.9.10 to 2.13.3. Annotations remains at 2.11.2. The resource loader cannot find JsonKey, and the actual updated JacksonAnnotationIntrospector bytecode directly references it. This establishes a binary compatibility failure. The diagnostic passed one resource-inspection test in each image, recorded separately from original counts.

Case 123 has the same source/POM snapshot hashes in both phases and the same mechanism and dependency versions. Case 135 has a different BUMP identifier, update PR and image pair. Both remain separate candidate records. This assessment is NON_BEHAVIORAL pending independent human review.
