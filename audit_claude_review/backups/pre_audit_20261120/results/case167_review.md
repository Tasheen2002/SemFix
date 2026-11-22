# Case 167 review

fscrawler updates poi-scratchpad from 4.1.2 to 5.0.0.

POI Scratchpad 5.0.0 expects IOUtils.toByteArray(InputStream, int, int). Retained POI 4.1.2 lacks the overload. Tika logs the failed DOC extraction and the test fails because the text is null. Counts come from the randomized JUnit runner.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 95 | 0 | 0 | 3 |
| BREAKING | FAILURE | 89 | 1 | 0 | 1 |

Recorded assessment is `NON_BEHAVIORAL`. Binary linkage flag is `YES`. Independent human review is pending.

Changed POMs in the image comparison are pom.xml. The affected report classpaths list no matching JAR path in PRE and no matching JAR path in BREAKING.

Original logs and archived reports are indexed in the evidence manifest.
