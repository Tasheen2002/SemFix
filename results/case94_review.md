# Case 94 review

wsdoc updates Jackson Databind 2.4.2 to 2.12.6.1. The root POM version is the sole archived source/POM change. The affected test classpath retains Jackson Annotations 2.4.1 and Core 2.4.2.

PRE passes all 59 tests. BREAKING reports 59 tests with 33 failures. Maven agrees with the suite-level Surefire XML. The nested TestNG per-class XML duplicates those executions, so its entries are excluded from the aggregate totals.

The first failure wraps a NoClassDefFoundError for JsonMerge during ObjectMapper initialization. The other 32 wrap subsequent ObjectMapper initialization errors. The upgraded JacksonAnnotationIntrospector references JsonMerge, and the retained annotations JAR lacks it. This supports a non-behavioural binary incompatibility assessment pending independent review.

Both original Maven runs, reports and resolved JAR inspection are archived. The explicit Maven outcome determines failure because the image pipes Maven through tee.
