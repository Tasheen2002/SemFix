# Case 33 review

The `avans` upgrade of Jackson Core from 2.4.2 to 2.13.3 is a **non-behavioural binary linkage incompatibility**, pending human review.

PRE reported 69 tests, two skipped and zero failures or errors. BREAKING reported 69 tests, two skipped, two errors and one assertion failure. In `SpyMemcachedSessionStoreTest`, CBOR 2.4.0 attempts to invoke `getOutputContext()` with the return type `JsonWriteContext`. That signature is available through `GeneratorBase` in Core 2.4.2. The resolved Core 2.13.3 has the `JsonStreamContext` return signature, so the old CBOR call fails with `NoSuchMethodError`. The HTTP integration assertion receives 500 instead of 200 after the same serialization error.

The JAR disassembly confirms the old call descriptor and the two Core versions' method signatures. The affected report's classpath changes only the Jackson Core path. The copied `avans/pom.xml` changes only the Core version. The archive helper flattens the `avans` module path because it matches the checkout directory name. I copied its POM and reports directly from both containers. Adding the 57 supplemental test records per phase to the default archives gives the reactor totals above, which match the Maven logs.

Both container commands pipe Maven through `tee`, masking the Maven exit code. The logs have prefix `2cc9522c` under `logs/batch_triage/`. The archives, supplemental POMs and reports, resolved JARs and disassembly are under `logs/case33_evidence/`.
