# Case 95 review

dropwizard-pac4j updates Jackson Databind 2.10.5.1 to 2.13.4.2. The root POM version is the sole archived source/POM change. The affected classpath retains Jackson Core and Annotations 2.10.5.

PRE passes all 16 tests. BREAKING reports 16 errors, each naming com.fasterxml.jackson.core.util.JacksonFeature. Maven and fresh Surefire XML agree. The updated Databind JAR contains references to that type, and the retained Core JAR lacks it. This supports a non-behavioural binary incompatibility assessment pending independent review.

Both original runs, reports and resolved JAR inspection are archived. The image pipes Maven through tee, so the explicit Maven result establishes failure.
