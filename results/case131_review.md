# Case 131 review

Both original FSCrawler images ran. PRE succeeded with 95 reported tests, including three ignored. BREAKING stopped in Tika with 89 tests, three assertion failures and one ignored. The counts come from the randomized JUnit module summaries. The runner produced no Surefire XML and retained four failed-run event and suite files.

The root POM changes only POI core from 4.1.2 to 5.0.0. The failed runner retains POI OOXML and Scratchpad 4.1.2. The two DOCX failures log that POIXMLTextExtractor expects POITextExtractor as a superclass. The old OOXML JAR extends it as a class, while POI 5.0.0 defines an interface. The DOC failure logs the missing LittleEndian.getByteArray(byte[], int, int, int) signature. Disassembly shows that signature exists in POI 4.1.2, is absent from POI 5.0.0, and is still invoked by retained Scratchpad classes. These two binary mismatches explain the downstream assertions. The encrypted-document message did not produce another reported failure.

The baseline JARs were selected using explicit POM versions because the successful runner deleted its event files. The updated artifacts came from retained runner classpaths. Independent human review remains pending.
