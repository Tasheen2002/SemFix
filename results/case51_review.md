# Case 51 review

The fscrawler POI Scratchpad upgrade from 4.1.2 to 5.1.0 is provisionally **non-behavioural**, pending human review.

PRE's randomized JUnit module summaries total 95 tests, including three ignored, with BUILD SUCCESS. BREAKING totals 89 tests, including one ignored and one assertion failure, with BUILD FAILURE in the Tika module. The affected test is TikaDocParserTest.testExtractFromDoc. The extraction result is null after the parser logs the missing method signature `IOUtils.toByteArray(InputStream, int, int)`.

The failed runner's events identify Scratchpad 5.1.0 together with POI 4.1.2. Disassembly shows HWPFDocumentCore in Scratchpad calling that three-argument int/int descriptor. IOUtils in the resolved POI JAR has the long/int descriptor and lacks the requested int/int method. The assertion is a consequence of failed binary method resolution during extraction.

Only the Scratchpad version changes in the archived project POM. These runs use the randomized runner and generate no Surefire XML. Failed-run events are archived; successful PRE retains no event files, so its Maven module summaries provide the test counts. The tee pipeline masks Maven's failing exit code. Automated triage flags the downstream assertion as a likely behavioural candidate, while JAR inspection identifies the linkage cause.

Logs have prefix `4507371b` under `logs/batch_triage/`. Source archives, runner events, resolved JARs and disassembly are under `logs/case51_evidence/`.
