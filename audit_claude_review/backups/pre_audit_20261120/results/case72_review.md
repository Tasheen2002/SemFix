# Case 72 review

dropwizard-pac4j updates Jackson Databind 2.10.5.1 to 2.14.2. Only the root POM changes in the archived source/POM files. The affected classpath retains Jackson Core and Jackson Annotations 2.10.5.

PRE passes all 16 tests. BREAKING reports 16 errors across all 16 tests. Each error names the missing com.fasterxml.jackson.core.util.JacksonFeature class during ObjectMapper construction. The resolved Databind JAR references the type, and the resolved Core JAR lacks it. This is a non-behavioural binary incompatibility, pending independent human review.

Maven and fresh Surefire XML agree. Both runs, classpaths, resolved JARs and class reference inspection are archived. The explicit Maven result establishes failure because the image pipes Maven through tee.
