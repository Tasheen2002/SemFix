# Case 106 review

fscrawler updates poi-ooxml from 4.1.2 to 5.2.0. The root POM version is the only changed archived source/POM. Failed-run bootstrap events identify poi-ooxml and poi-ooxml-lite 5.2.0 together with poi and poi-scratchpad 4.1.2.

Both original images were run. PRE succeeds with 95 reported randomized-runner tests, including three ignored tests, no failures and no errors. BREAKING fails in the Tika module after 89 reported tests, including one ignored test, two failures and no errors; downstream modules are skipped. These totals come from the original randomized-runner module summaries. There is no Surefire XML. Successful PRE events are deleted by the runner, while four failed-run event/suite files are retained. The baseline JAR selection is reconstructed from explicit PRE POM dependency versions, not from a surviving PRE runner classpath.

TikaDocParserTest.testExtractFromDocx and testDocxWithEmbeddedBadPDF receive null extracted text. Immediately before these assertions, the parser logs that POIXMLTextExtractor cannot implement POITextExtractor because it is not an interface. Disassembly of the actual container artifacts confirms updated POIXMLTextExtractor is an interface extending POITextExtractor, while retained POI 4.1.2 defines POITextExtractor as an abstract class. In the old OOXML JAR, POIXMLTextExtractor is an abstract class extending that class. This incompatible type relationship explains the two failing assertions and supports a non-behavioral binary-compatibility assessment.

Protected-DOCX handling also logs ClassNotFoundException for AgileEncryptionInfoBuilder. That class exists in the old OOXML JAR but is absent from the inspected updated OOXML/Lite and retained POI/Scratchpad JARs. This additional message is not counted as a third test failure: only the two named tests fail.

Automated screening and this evidence-backed agent assessment are kept separate. Independent human review remains pending, and reviewer/final labels are blank. Maven output establishes success/failure because the original tee pipeline masks failures in the Docker exit code. No repair or substitution control was run.
