# Case 181 review

sparql.anything updates jsoup from 1.14.2 to 1.15.3.

jsoup 1.15.3 trims whitespace in Element.html() for the existing Microdata1 fixture. SPARQL Anything stores that string as an innerHTML RDF literal, so the output graph no longer matches the expected graph. The isolated probe used identical compiled code and fixture bytes in both images. Text extraction produced identical output, and the HTML serialization check reproduced the changed whitespace.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 240 | 0 | 0 | 14 |
| BREAKING | FAILURE | 57 | 2 | 0 | 4 |

Assessment is `PROVISIONAL_BEHAVIORAL`. Binary linkage flag is `NO`. Independent human review is pending.

Changed POMs in the original archives are pom.xml. Original logs and archived reports are indexed in the evidence manifest.
