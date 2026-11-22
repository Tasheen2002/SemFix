# Case 62 review

fscrawler updates POI Scratchpad 4.1.2 to 5.2.0. The root POM version is the only change among the archived source and POM files.

PRE succeeds with 95 reported tests, three ignored. BREAKING stops in the Tika module with 89 reported tests, one assertion failure and one ignored test. The remaining modules are skipped. These counts come from the randomized-runner module summaries. Neither run produces Surefire XML. Four event and suite files are retained from the failed run.

TikaDocParserTest.testExtractFromDoc receives null after the parser reports failure to resolve IOUtils.toByteArray(InputStream, int, int). The runner events identify Scratchpad 5.2.0 alongside POI 4.1.2. Disassembly of the resolved JARs shows HWPFDocumentCore invokes the int/int descriptor and the installed IOUtils supplies a long/int overload instead. This is a non-behavioural binary incompatibility, pending independent human review. Automated triage flags the downstream assertion as potentially behavioural.

The 51e103fc logs and case62_evidence directory retain both image runs, module counts, source/POM archives, failed-run events and resolved JARs. Explicit Maven output determines the result because the image's tee pipeline masks the exit status.
