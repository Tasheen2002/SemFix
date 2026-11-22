# Case 50 review

The fscrawler POI upgrade from 4.1.2 to 5.2.1 is provisionally **non-behavioural**, pending human review.

The randomized JUnit runner reports 88 tests in PRE, including three ignored, with BUILD SUCCESS. BREAKING reports 82 tests, including one ignored and four failures, with BUILD FAILURE in the Tika module. Maven skips the downstream modules. Totals are sums of the runner's per-module Tests summary lines. These runs generate no Surefire XML. The retained BREAKING runner events identify POI 5.2.1 together with POI OOXML 4.1.2 and Scratchpad 4.1.2.

Two failed DOCX extractions log that POIXMLTextExtractor has interface POITextExtractor as its superclass. Disassembly confirms that POITextExtractor changes from an abstract class in POI 4.1.2 to an interface in 5.2.1, while the old OOXML extractor still extends it as a class. The JVM cannot link that mixed type hierarchy, and extraction returns null.

The DOC and protected-document failures log WORKBOOK_DIR_ENTRY_NAMES. Disassembly also shows that InternalWorkbook's public field changes its descriptor from String[] to List<String>. The legacy extraction stack references the old array descriptor. These binary incompatibilities cause extraction failures followed by assertions on null text or content type.

The archived sources match and only the POI version changes in the POM. The randomized runner events remain in the failed module and were copied. The successful PRE run retains no runner event files, so its original Maven log supplies the run totals. The image pipeline masks the failing Maven exit code.

Logs have prefix `44a15fa5` under `logs/batch_triage/`. Source archives, summaries, BREAKING runner events, resolved JARs and both type and field disassemblies are under `logs/case50_evidence/`. Automated triage suggests a behavioural candidate because it sees the downstream assertions; the binary inspection supports the non-behavioural assessment.
