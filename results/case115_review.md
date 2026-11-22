# Case 115 review

fscrawler updates poi-ooxml from 4.1.2 to 5.2.2. Only the root POM version changes among archived source/POM files and across all 21 POMs. Failed-run bootstrap events identify poi-ooxml/poi-ooxml-lite 5.2.2 with retained poi and poi-scratchpad 4.1.2.

Both original images were run. PRE succeeds with 89 reported randomized-runner tests including three ignored, zero failures and zero errors. BREAKING stops in the Tika module after 83 reported tests, two assertion failures, zero errors and one ignored test. Downstream modules are skipped. Counts come from original module summaries, not Surefire XML, which this runner does not produce. Four failed-run event/suite files are retained. Successful PRE events are deleted, so baseline artifact selection uses explicit PRE POM versions rather than a surviving PRE runner classpath.

TikaDocParserTest.testDocxWithEmbeddedBadPDF and testExtractFromDocx receive null text after the parser logs that POIXMLTextExtractor cannot implement POITextExtractor because the latter is not an interface. Actual JAR disassembly confirms old POIXMLTextExtractor is an abstract class extending POITextExtractor, but OOXML 5.2.2 changes it to an interface extending that type while retained POI 4.1.2 still defines an abstract class. This incompatible relationship establishes a binary incompatibility behind the assertions.

Protected-document processing also logs missing AgileEncryptionInfoBuilder. The class exists in the old OOXML JAR but is absent from the inspected updated OOXML/Lite and retained POI/Scratchpad JARs. This additional message is not counted as a third failing test; the runner reports only the two named assertion failures.

The evidence supports NON_BEHAVIORAL pending independent human review. Automated screening remains separate, with reviewer/final labels blank. Explicit Maven output establishes outcomes because the original tee pipeline masks Maven failures in Docker's exit code. No repair or substitution control was run.
