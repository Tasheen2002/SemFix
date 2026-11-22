# Case 70 review

geoserver-shell updates org.json from 20090211 to 20230227. The root POM version is the only archived source/POM change, and the affected test classpath changes only that JAR.

PRE passes all 205 tests. BREAKING runs 205 tests with two errors, zero failures and zero skips. Maven and fresh Surefire XML agree. ScriptCommandsTest.listSession and getSession fail when their unchanged application methods call JSONObject.getString("id") on numeric IDs 0 and 1. The updated library throws JSONException.

A minimal Java probe parses the same JSON in both runs. Both JARs represent the numeric ID as Integer. The old JAR returns its string representation through getString, while the new one throws the same JSONException seen in the project tests. The probe uses one BREAKING image environment and varies only the JSON JAR. The original reports, resolved JARs, probe source and output are archived.

The API still executes and its treatment of the numeric value changes. This is provisionally behavioural pending independent human review. The automated screen marks the runtime case for review. Explicit Maven output establishes the original outcome because the command pipes Maven through tee.
