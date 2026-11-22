# Case 36 review

The `fscrawler` upgrade of POI Scratchpad from 4.1.2 to 5.2.2 is a **non-behavioural binary linkage incompatibility**, pending human review.

The randomized JUnit runner reports 89 tests across PRE, with three ignored and a successful build. BREAKING reports 83 tests, one ignored and one assertion failure. Maven stops after the failing Tika module. These totals come from summing the runner's module summaries. The default Surefire archive contains no XML for this runner.

`TikaDocParserTest.testExtractFromDoc` receives null where it expects extracted text. Immediately beforehand the parser logs a failed extraction for `test.doc` and identifies the signature `IOUtils.toByteArray(InputStream, int, int)`. The retained runner events list Scratchpad 5.2.2 and POI 4.1.2. Disassembly shows `HWPFDocumentCore` in Scratchpad 5.2.2 invoking that exact signature. The resolved POI 4.1.2 has the `(InputStream, long, int)` overload and lacks `(InputStream, int, int)`. The observed test assertion follows the failed extraction, while the underlying cause is the unresolved binary method.

The archived source files match, and the project POM changes only the Scratchpad version. Both container commands pipe Maven through `tee`, masking the failing Maven exit code. The raw logs have prefix `30caf72b` under `logs/batch_triage/`. The archives, retained BREAKING runner events, JARs and disassembly are under `logs/case36_evidence/`.
