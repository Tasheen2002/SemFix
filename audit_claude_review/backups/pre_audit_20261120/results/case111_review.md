# Case 111 review

fscrawler updates poi-scratchpad from 4.1.2 to 5.2.1. The root POM version is the only changed archived source/POM. The failing runner bootstrap events identify Scratchpad 5.2.1 with retained POI 4.1.2.

Both original images were run. PRE succeeds with 88 reported randomized-runner tests, including three ignored tests, zero failures and zero errors. BREAKING stops in the Tika module after 82 reported tests, with one assertion failure, zero errors and one ignored test. Downstream modules are skipped. Original module summaries establish these totals; neither phase produces Surefire XML. Four event/suite files survive from the failed run. The successful runner deletes its events, so baseline artifact selection is reconstructed from explicit PRE POM versions rather than a surviving PRE runner classpath.

TikaDocParserTest.testExtractFromDoc receives null text immediately after the parser logs failure to resolve byte[] IOUtils.toByteArray(InputStream, int, int). Disassembly of the actual Scratchpad 5.2.1 JAR shows HWPFDocumentCore invokes the (InputStream;II)[B descriptor. Retained POI 4.1.2 instead exposes the three-argument overload with long/int, not int/int. This binary missing-method incompatibility causes the downstream assertion and supports a non-behavioral assessment.

Automated screening and the curated agent assessment remain separate. Independent human review remains pending, with reviewer/final labels blank. Explicit Maven outcomes determine success/failure because the original tee pipeline masks Maven failures in Docker's exit code. No repair or substitution control was run.
