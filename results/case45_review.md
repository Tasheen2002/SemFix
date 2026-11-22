# Case 45 review

The license-maven-plugin upgrade of Plexus Utils from 3.5.1 to 4.0.0 is provisionally **non-behavioural**, pending human review.

PRE passed all 343 tests. BREAKING reported 330 tests with 231 errors, zero assertion failures and zero skips. The license-maven-plugin module fails, and downstream modules are skipped by Maven. All 231 errors report NoClassDefFoundError for `org.codehaus.plexus.util.xml.pull.XmlPullParserException`, with ClassNotFoundException as the nested cause.

Direct inspection confirms that Plexus Utils 3.5.1 contains this class, while 4.0.0 lacks it. The affected test classpath paths differ only in Plexus Utils. The module POM changes only that version. This removes a required runtime type.

The archive helper originally flattened the license-maven-plugin module because its name matches the checkout directory. The helper was corrected to preserve the paths emitted by docker cp, and both stopped containers were re-archived. The initial archives and their summaries are retained with initial_path_mapping in their names. The corrected source comparison identifies license-maven-plugin/pom.xml as the only changed source/POM path. A direct POM copy also verifies the change. Both corrected report totals agree with Maven's module summaries.

The image command pipes Maven through tee, masking its failing exit code. Logs have prefix `3c0bc059` under `logs/batch_triage/`. Corrected source archives, fresh test reports, original archives, inspected JARs and copied module POMs are under `logs/case45_evidence/`.
