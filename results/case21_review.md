# Case 21 review

The `avans` upgrade of Jackson CBOR from 2.4.0 to 2.13.3 is a **non-behavioural binary linkage incompatibility**, pending human review.

| Run | Reported tests | Failures | Errors | Skipped |
|---|---:|---:|---:|---:|
| PRE | 69 | 0 | 0 | 2 |
| BREAKING | 69 | 1 | 3 | 2 |

The affected `avans-session-spymemcached` module reports four tests in each run. When `SpyMemcachedSessionStore` constructs a `CBORFactory` in its static initializer, the upgraded CBOR JAR requires `com.fasterxml.jackson.core.TSFBuilder`. The test classpath retains Jackson Core 2.4.2. Inspection of the resolved JARs shows that Core lacks the class and the upgraded CBOR factory references it. The original initialization error causes two later initialization errors. The integration test then receives HTTP 500 instead of 200 when the server tries to use the same failed class.

The changed POM is `avans-session-spymemcached/pom.xml`, and its only change is the CBOR version. The default archive helper omitted XML from the `avans` module because its name matches the checkout directory. I copied that module's reports separately from each retained container. Adding their 57 tests to the archived reports gives the reactor totals above, which match the Maven logs. The image pipeline masks Maven's failing exit code, so the build summary establishes the BREAKING result.

The logs have prefix `1c3529ea` under `logs/batch_triage/`. The reports, supplemental module reports and inspected JARs are under `logs/case21_evidence/`.
