# Case 123 review

IDS-Messaging-Services updates jackson-databind from 2.9.10.8 to 2.13.3 in core/pom.xml. This is the only changed archived source/POM. The effect propagates to messaging tests.

Both original images were run. PRE succeeds with 32 reactor tests, zero failures/errors/skips. BREAKING stops in messaging after 18 tests, with one assertion failure, five errors and zero skips. Maven and fresh Surefire XML agree. Five errors report missing com.fasterxml.jackson.annotation.JsonKey; IdsMessageUtilsTest.testUtils additionally fails an assert-does-not-throw check because it receives that same NoClassDefFoundError. This assertion is downstream of the binary failure, not separate evidence of semantic change.

The old test runner's original XML exposes only Maven's launcher classpath. Separate same-image diagnostics therefore add and select one standalone resource-origin test, leaving production source and dependency versions unchanged. Each diagnostic passes one test and identifies the Jackson resources visible to the messaging test classloader. PRE uses Databind 2.9.10.8 and Core 2.9.10. BREAKING uses Databind/Core 2.13.3. Both retain Annotations 2.11.2, and JsonKey is absent in both environments. The absence was harmless before the update; the new Databind introduces a reference to it.

Actual JAR inspection and JacksonAnnotationIntrospector disassembly corroborate that new reference and the missing annotation type. This supports NON_BEHAVIORAL with binary_linkage_incompatibility=YES. The diagnostic commands, image identities, states, source, captured resource URLs and fresh diagnostic reports are archived separately from original counts; a passing resource-inspection probe is not a repair of the failing tests.

Independent human review remains pending, with reviewer/final labels blank. Automated triage is not a final semantic verdict. Explicit Maven outcomes establish the original build results because the tee pipeline masks failure in Docker's exit code. No repair was attempted.
