# Case 79 review

fscrawler updates POI 4.1.2 to 5.2.2. Only the version in the root POM changes among the archived files. The failed runner events show POI OOXML and Scratchpad 4.1.2 still present.

PRE succeeds with 89 reported tests including three ignored. BREAKING stops in the Tika module with 83 reported tests, four assertion failures and one ignored test. The counts come from randomized JUnit module summaries. Four event and suite files are retained from BREAKING. The runner generates no Surefire XML.

Two DOCX extractions fail because the old POIXMLTextExtractor extends POITextExtractor as a class, while POI 5.2.2 defines it as an interface. The other two extractions report WORKBOOK_DIR_ENTRY_NAMES. The upgraded POI field has a List descriptor, while the Tika 2.2.1 Microsoft parser JAR still has array-descriptor field references. The actual JARs and disassembly corroborate both binary incompatibilities. These cause downstream assertions and support a non-behavioural assessment pending independent human review.

Automated triage flags the assertions as potentially behavioural. Maven's explicit result establishes the outcome because the command pipes Maven through tee.
