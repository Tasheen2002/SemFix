# Case 126 review

Both original tamtam-bot-api images ran. The baseline succeeded with 108 tests and one skip. The updated run reported 108 tests, 46 errors, and one skip. Maven and 43 fresh Surefire reports per phase agree.

The only archived source/POM change is the Databind version in the root POM. The effective classpath also upgrades Jackson Core to 2.12.6 while retaining Jackson Annotations 2.9.9. The updated JacksonAnnotationIntrospector directly references JsonKey. The retained Annotations JAR lacks that type. Serializer tests record the missing class directly. The embedded HTTP server also logs the same linkage error while serializing responses, and client tests report HTTP 400/500 errors and exception mismatches. The missing annotation establishes binary incompatibility. The individual HTTP responses were not all traced separately.

The evidence supports NON_BEHAVIORAL pending independent human review. Maven's explicit build result establishes the outcome because the image command pipes Maven output through tee.
