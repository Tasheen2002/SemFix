# Human review packet: 47 sample cases

**For:** the human reviewer adjudicating the BUMP classification. **Time:** about 5–10 minutes per case.

**What you're checking:** whether the proposed label follows from the evidence under the approved rules (`decision_rules.md`). You are not re-deciding the rules.

**How:** read the evidence excerpt for each case and tick the checklist. Write your label in `human_sample.csv` (`human_label`, `human_confidence`, `human_notes`). Open the raw log only if the excerpt isn't enough; paths are listed for each case.

**When you finish:** if you agree with every case, or the disagreements are resolved, ask Claude to copy the rule-based labels into `final_label`. If a disagreement exposes a wrong rule application, the whole group in `related_group` needs rechecking.

## Contents

- [Case 1](#case-1): org.slf4j:slf4j-api 1.7.36 -> 2.0.3, proposed **BEHAVIORAL**, representative of SLF4J2_IGNORES_LEGACY_BINDING (36 cases)
- [Case 2](#case-2): org.slf4j:slf4j-api 1.7.36 -> 2.0.4, proposed **BEHAVIORAL**, representative of SLF4J2_IGNORES_LEGACY_BINDING (36 cases)
- [Case 3](#case-3): com.fasterxml.jackson.core:jackson-databind 2.4.2 -> 2.9.10.8, proposed **NON_BEHAVIORAL**, representative of JACKSON_MODULE_SKEW (25 cases)
- [Case 4](#case-4): org.junit.platform:junit-platform-surefire-provider 1.0.3 -> 1.3.2, proposed **NON_BEHAVIORAL**, representative of SUREFIRE_PROVIDER_TOOLING (7 cases)
- [Case 6](#case-6): org.apache.poi:poi-ooxml 4.1.2 -> 5.1.0, proposed **NON_BEHAVIORAL**, representative of POI_MODULE_MIX (13 cases)
- [Case 7](#case-7): org.graalvm.js:js-scriptengine 22.3.2 -> 23.0.1, proposed **NON_BEHAVIORAL**, representative of JAVA17_BYTECODE_ON_JAVA11 (11 cases)
- [Case 8](#case-8): com.fasterxml.jackson.core:jackson-databind 2.10.5.1 -> 2.14.1, proposed **NON_BEHAVIORAL**, representative of JACKSON_MODULE_SKEW (25 cases)
- [Case 9](#case-9): org.mockito:mockito-core 4.11.0 -> 5.1.1, proposed **BEHAVIORAL**, representative of MOCKITO5_INLINE_DEFAULT (5 cases)
- [Case 11](#case-11): org.codehaus.plexus:plexus-utils 3.5.1 -> 4.0.0, proposed **NON_BEHAVIORAL**, representative of PLEXUS_UTILS_4_REMOVALS (3 cases)
- [Case 13](#case-13): commons-io:commons-io 2.7 -> 2.11.0, proposed **BEHAVIORAL**, singleton mechanism
- [Case 14](#case-14): com.h2database:h2 1.3.175 -> 2.0.206, proposed **BEHAVIORAL**, representative of H2_VARCHAR_LIMIT (2 cases)
- [Case 19](#case-19): org.junit.jupiter:junit-jupiter-params 5.9.3 -> 5.10.0, proposed **NON_BEHAVIORAL**, representative of JUNIT_PLATFORM_SKEW (3 cases)
- [Case 20](#case-20): com.thoughtworks.xstream:xstream 1.4.17 -> 1.4.19, proposed **BEHAVIORAL**, singleton mechanism
- [Case 25](#case-25): org.apache.logging.log4j:log4j-api 2.16.0 -> 2.18.0, proposed **NON_BEHAVIORAL**, representative of LOG4J_API_CORE_SKEW (11 cases)
- [Case 28](#case-28): org.dhatim:dropwizard-sentry 2.0.22 -> 2.0.28-8, proposed **BEHAVIORAL**, representative of DROPWIZARD_SENTRY_CONFIG (5 cases)
- [Case 30](#case-30): org.eclipse.persistence:org.eclipse.persistence.moxy 3.0.2 -> 4.0.1, proposed **NON_BEHAVIORAL**, singleton mechanism
- [Case 32](#case-32): ch.qos.logback:logback-classic 1.2.11 -> 1.4.0, proposed **NON_BEHAVIORAL**, representative of LOGBACK_CLASSIC_CORE_SKEW (5 cases)
- [Case 34](#case-34): javax:javaee-api 7.0 -> 8.0.1, proposed **NON_BEHAVIORAL**, singleton mechanism
- [Case 37](#case-37): org.springframework:spring-tx 5.3.24 -> 6.0.4, proposed **NON_BEHAVIORAL**, representative of JAVA17_BYTECODE_ON_JAVA11 (11 cases)
- [Case 42](#case-42): jakarta.xml.bind:jakarta.xml.bind-api 2.3.2 -> 4.0.0, proposed **NON_BEHAVIORAL**, representative of JAVAX_JAKARTA_NAMESPACE (13 cases)
- [Case 44](#case-44): org.glassfish.jersey.core:jersey-server 2.32 -> 2.36, proposed **NON_BEHAVIORAL**, representative of JERSEY_JETTY_SKEW (11 cases)
- [Case 46](#case-46): ch.qos.logback:logback-classic 1.2.11 -> 1.4.3, proposed **NON_BEHAVIORAL**, representative of SLF4J17_REMOVED_STATICLOGGERBINDER (6 cases)
- [Case 49](#case-49): org.antlr:antlr4-runtime 4.7.2 -> 4.10.1, proposed **NON_BEHAVIORAL**, disputed label; representative of ANTLR_ATN_FORMAT (6 cases)
- [Case 53](#case-53): org.codehaus.plexus:plexus-io 3.2.0 -> 3.3.0, proposed **BEHAVIORAL**, singleton mechanism
- [Case 64](#case-64): org.jenkins-ci.plugins:github-api 1.117 -> 1.303-400.v35c2d8258028, proposed **NON_BEHAVIORAL**, singleton mechanism
- [Case 67](#case-67): org.antlr:antlr4-runtime 4.9.3 -> 4.10, proposed **NON_BEHAVIORAL**, disputed label
- [Case 69](#case-69): org.graalvm.js:js-scriptengine 22.0.0 -> 22.1.0, proposed **NON_BEHAVIORAL**, disputed label; representative of GRAALJS (1 cases)
- [Case 70](#case-70): org.json:json 20090211 -> 20230227, proposed **BEHAVIORAL**, singleton mechanism
- [Case 71](#case-71): com.google.flogger:google-extensions 0.6 -> 0.7.1, proposed **NON_BEHAVIORAL**, singleton mechanism
- [Case 87](#case-87): org.dhatim:dropwizard-sentry 2.1.2-4 -> 4.0.1-2, proposed **NON_BEHAVIORAL**, representative of DROPWIZARD_SENTRY_DW4 (3 cases)
- [Case 91](#case-91): com.squareup.okhttp3:okhttp 3.3.1 -> 3.14.9, proposed **NON_BEHAVIORAL**, singleton mechanism
- [Case 104](#case-104): eu.europa.ec.joinup.sd-dss:dss-pades-pdfbox 5.9 -> 5.10.2, proposed **NON_BEHAVIORAL**, singleton mechanism
- [Case 105](#case-105): org.apache.logging.log4j:log4j-core 2.11.1 -> 2.16.0, proposed **NON_BEHAVIORAL**, representative of LOG4J_API_CORE_SKEW (11 cases)
- [Case 108](#case-108): org.apache.sshd:sshd-common 2.9.2 -> 2.10.0, proposed **NON_BEHAVIORAL**, representative of SSHD_SKEW (2 cases)
- [Case 109](#case-109): com.google.inject:guice 5.1.0 -> 7.0.0, proposed **NON_BEHAVIORAL**, disputed label; representative of JAVAX_JAKARTA_NAMESPACE (13 cases)
- [Case 112](#case-112): org.antlr:antlr4-runtime 4.7.2 -> 4.12.0, proposed **NON_BEHAVIORAL**, disputed label
- [Case 116](#case-116): org.codehaus.mojo:versions-maven-plugin 2.15.0 -> 2.16.0, proposed **NON_BEHAVIORAL**, singleton mechanism
- [Case 127](#case-127): org.antlr:antlr4-runtime 4.7.2 -> 4.11.1, proposed **NON_BEHAVIORAL**, disputed label
- [Case 138](#case-138): org.yaml:snakeyaml 1.13 -> 1.32, proposed **NON_BEHAVIORAL**, representative of SNAKEYAML_RAML_SKEW (2 cases)
- [Case 140](#case-140): org.antlr:antlr4-runtime 4.9.3 -> 4.10.1, proposed **NON_BEHAVIORAL**, disputed label
- [Case 158](#case-158): org.apache.httpcomponents:httpclient 4.5.1 -> 4.5.13, proposed **BEHAVIORAL**, singleton mechanism
- [Case 161](#case-161): org.jetbrains.kotlin:kotlin-stdlib 1.3.31 -> 1.6.0, proposed **NON_BEHAVIORAL**, singleton mechanism
- [Case 163](#case-163): net.minidev:json-smart 2.4.8 -> 2.4.9, proposed **BEHAVIORAL**, representative of JSON_SMART_DEPTH_LIMIT (2 cases)
- [Case 178](#case-178): org.springframework:spring-webmvc 4.1.6.RELEASE -> 5.3.18, proposed **NON_BEHAVIORAL**, singleton mechanism
- [Case 181](#case-181): org.jsoup:jsoup 1.14.2 -> 1.15.3, proposed **BEHAVIORAL**, singleton mechanism
- [Case 183](#case-183): io.quarkiverse.googlecloudservices:quarkus-google-cloud-common-grpc 1.4.0 -> 2.2.0, proposed **NON_BEHAVIORAL**, singleton mechanism
- [Case 188](#case-188): org.antlr:antlr4-runtime 4.7.2 -> 4.10, proposed **NON_BEHAVIORAL**, disputed label

---

## Case 1

- **Project / update:** retest/recheck · `org.slf4j:slf4j-api 1.7.36 -> 2.0.3`
- **Why sampled:** representative of SLF4J2_IGNORES_LEGACY_BINDING (36 cases)
- **Proposed label:** **BEHAVIORAL** by rule **R5** (Provider selection changed while old provider present), category PROVIDER_OR_IMPLEMENTATION_SELECTION
- **Codex label:** PROVISIONAL_BEHAVIORAL · **Claude blind label:** BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=737 failures=0 errors=0 skipped=4
- **Updated:** BUILD FAILURE; surefire tests=737 failures=0 errors=30 skipped=4

**Initiating cause (Claude):** slf4j-api 2.0.3 provider discovery (ServiceLoader) ignores the logback-classic 1.2.11 StaticLoggerBinder still on the test classpath and falls back to NOPLogger; logunit LogbackLogProvider casts the logger to ch.qos.logback.classic.Logger -> ClassCastException

**What changed:** Logger implementation returned by LoggerFactory changed from logback Logger to NOPLogger (provider-selection policy change; old binding present and explicitly ignored per SLF4J console)

**Group evidence (DECISION_ONLY):** LoggerSelectionProbe in 18 cases (117,132,134,142,144,145,147,148,150,151,153,155,156,159,171,184,185,186): PRE selects the binding's logger, BREAKING selects NOP with the same jars. All 36 logs print 'Ignoring binding found at ...'.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 737, Failures: 0, Errors: 0, Skipped: 4
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 737, Failures: 0, Errors: 30, Skipped: 4
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0-M6:test (default-test) on project recheck:
BRK sigs:  30x java.lang.ClassCastException: class org.slf4j.helpers.NOPLogger cannot be cast to class ch.qos.logback.classic.Logger (o
BRK console: SLF4J: No SLF4J providers were found. | SLF4J: Defaulting to no-operation (NOP) logger implementation | SLF4J: See https://www.slf4j.org/codes.html#noProviders for further details. | SLF4J: Class path contains SLF4J bindings targeting slf4j-api versions 1.7.x or earlier. | SLF4J: Ignori
```

**Paths:** logs/02363207_pre.log; logs/02363207_breaking.log; audit_claude_review/digests/case001.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 2

- **Project / update:** feedzai/pdb · `org.slf4j:slf4j-api 1.7.36 -> 2.0.4`
- **Why sampled:** representative of SLF4J2_IGNORES_LEGACY_BINDING (36 cases)
- **Proposed label:** **BEHAVIORAL** by rule **R5** (Provider selection changed while old provider present), category PROVIDER_OR_IMPLEMENTATION_SELECTION
- **Codex label:** PROVISIONAL_BEHAVIORAL · **Claude blind label:** BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=291 failures=0 errors=0 skipped=13
- **Updated:** BUILD FAILURE; surefire tests=94 failures=0 errors=3 skipped=10

**Initiating cause (Claude):** slf4j-api 2.0.4 ignores logback-classic 1.2.11 binding, NOP fallback; class-level setup in BatchUpdateTest/EngineGeneralTest/EngineCloseTest casts to logback Logger -> ClassCastException

**What changed:** LoggerFactory returns NOPLogger instead of logback Logger

**Group evidence (DECISION_ONLY):** LoggerSelectionProbe in 18 cases (117,132,134,142,144,145,147,148,150,151,153,155,156,159,171,184,185,186): PRE selects the binding's logger, BREAKING selects NOP with the same jars. All 36 logs print 'Ignoring binding found at ...'.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 291, Failures: 0, Errors: 0, Skipped: 13
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 94, Failures: 0, Errors: 3, Skipped: 10
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.22.2:test (default-test) on project pdb: There are test failures.
BRK sigs:  3x java.lang.ClassCastException: class org.slf4j.helpers.NOPLogger cannot be cast to class ch.qos.logback.classic.Logger (o
BRK console: SLF4J: No SLF4J providers were found. | SLF4J: Defaulting to no-operation (NOP) logger implementation | SLF4J: See https://www.slf4j.org/codes.html#noProviders for further details. | SLF4J: Class path contains SLF4J bindings targeting slf4j-api versions 1.7.x or earlier. | SLF4J: Ignori
```

**Paths:** logs/04c07b06_pre.log; logs/04c07b06_breaking.log; audit_claude_review/digests/case002.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 3

- **Project / update:** versly/wsdoc · `com.fasterxml.jackson.core:jackson-databind 2.4.2 -> 2.9.10.8`
- **Why sampled:** representative of JACKSON_MODULE_SKEW (25 cases)
- **Proposed label:** **NON_BEHAVIORAL** by rule **R1** (Linkage or bytecode incompatibility)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=59 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=59 failures=33 errors=0 skipped=0

**Initiating cause (Claude):** jackson-databind 2.9.10.8 requires com.fasterxml.jackson.annotation.JsonMerge (jackson-annotations >=2.9) but an older annotations jar is resolved; first error NoClassDefFoundError JsonMerge, then 32x 'Could not initialize class ObjectMapper'

**Group evidence (STATIC_EVIDENCE):** NoClassDefFoundError/NoSuchMethodError on JacksonFeature/JsonKey/JsonMerge/StreamConstraintsException; archived jars show the class absent in the retained core/annotations (most cases from 15 on); class_origins in 123, 128, 135, 170.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 59, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 59, Failures: 33, Errors: 0, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0:test (default-test) on project versly-wsdoc: There are test failures.
 CB Caused by: java.lang.NoClassDefFoundError: com/fasterxml/jackson/annotation/JsonMerge
 CB Caused by: java.lang.ClassNotFoundException: com.fasterxml.jackson.annotation.JsonMerge
 CB Caused by: java.lang.NoClassDefFoundError: Could not initialize class com.fasterxml.jackson.databind.ObjectMapper
BRK sigs:  1x java.lang.RuntimeException: java.lang.NoClassDefFoundError: com/fasterxml/jackson/annotation/JsonMerge || 32x java.lang.RuntimeException: java.lang.NoClassDefFoundError: Could not initialize class com.fasterxml.jackson.databind.Ob
BRK console: log4j:WARN No appenders could be found for logger (freemarker.cache). | log4j:WARN Please initialize the log4j system properly. | log4j:WARN See http://logging.apache.org/log4j/1.2/faq.html#noconfig for more info.
BRK link: ClassNotFoundException, NoClassDefFoundError
```

**Paths:** logs/063cf862_pre.log; logs/063cf862_breaking.log; audit_claude_review/digests/case003.txt; audit_claude_review/reruns/RESULTS.md

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 4

- **Project / update:** International-Data-Spaces-Association/IDS-Messaging-Services · `org.junit.platform:junit-platform-surefire-provider 1.0.3 -> 1.3.2`
- **Why sampled:** representative of SUREFIRE_PROVIDER_TOOLING (7 cases)
- **Proposed label:** **NON_BEHAVIORAL** by rule **R10** (Tooling or test-infrastructure failure)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=32 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=26 failures=0 errors=0 skipped=0

**Initiating cause (Claude):** junit-platform-surefire-provider 1.3.2 incompatible with maven-surefire-plugin 2.19.1 (API incompatibility / NoSuchMethodError) in module paris; appstore SKIPPED

**Group evidence (COVERED):** 'An API incompatibility was encountered' with NoSuchMethodError in the plugin realm; directoryscanner_javap (63, 86). Five IDS images fail in different modules.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 6, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 12, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 2, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 6, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 3, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 3, Failures: 0, Err
BRK status: [INFO] BUILD FAILURE
BRK reactor: messaging-services   SUCCESS [  1.916 s]; core   SUCCESS [ 24.485 s]; messaging   SUCCESS [ 12.823 s]; clearinghouse   SUCCESS [  5.874 s]; broker   SUCCESS [  5.907 s]; vocol   SUCCESS [  0.608 s]; paris   FAILURE [  1.192 s]; appstore   SKIPPED; BUILD FAILURE
BRK agg: Tests run: 6, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 12, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 2, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 6, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 0, Failures: 0, Errors: 0, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.19.1:test (default-test) on project paris: Execution default-test of goal org.apache.maven.plugins:maven-surefire-plugin:2.19.1:test failed: An API incompatibility was encountered
BRK console: SLF4J: No SLF4J providers were found. | SLF4J: Defaulting to no-operation (NOP) logger implementation | SLF4J: See http://www.slf4j.org/codes.html#noProviders for further details. | SLF4J: Class path contains SLF4J bindings targeting sl ...[cut]
```

**Paths:** logs/0671a30e_pre.log; logs/0671a30e_breaking.log; audit_claude_review/digests/case004.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 6

- **Project / update:** dadoonet/fscrawler · `org.apache.poi:poi-ooxml 4.1.2 -> 5.1.0`
- **Why sampled:** representative of POI_MODULE_MIX (13 cases)
- **Proposed label:** **NON_BEHAVIORAL** by rule **R1** (Linkage or bytecode incompatibility)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=0 failures=0 errors=0 skipped=0; randomized-runner tests=95 failures=0 errors=0 ignored=3
- **Updated:** BUILD FAILURE; surefire tests=0 failures=0 errors=0 skipped=0; randomized-runner tests=89 failures=2 errors=0 ignored=1

**Initiating cause (Claude):** poi-ooxml 5.1.0 mixed with an older poi core on the classpath: IncompatibleClassChangeError 'POIXMLTextExtractor can not implement POITextExtractor, because it is not an interface' plus ClassNotFoundException AgileEncryptionInfoBuilder; Tika swallows these and tests fail on assertions

**Group evidence (STATIC_EVIDENCE):** Tika logs NoSuchMethodError/IncompatibleClassChangeError/NoSuchFieldError before each null-text assertion; archived mixed-version POI jars.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
BRK status: [INFO] BUILD FAILURE
BRK reactor: FSCrawler   SUCCESS [  0.152 s]; FSCrawler Test Framework   SUCCESS [  4.501 s]; FSCrawler Framework   SUCCESS [  1.174 s]; FSCrawler Settings   SUCCESS [  4.139 s]; FSCrawler Test Documents   SUCCESS [  0.073 s]; FSCrawler Beans   SUCCESS [  1.929 s]; FSCrawler 3rd Party libraries   SU
BRK link: ClassNotFoundException
```

**Paths:** logs/097d93fb_pre.log; logs/097d93fb_breaking.log; audit_claude_review/digests/case006.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 7

- **Project / update:** fmtn/a · `org.graalvm.js:js-scriptengine 22.3.2 -> 23.0.1`
- **Why sampled:** representative of JAVA17_BYTECODE_ON_JAVA11 (11 cases)
- **Proposed label:** **NON_BEHAVIORAL** by rule **R1** (Linkage or bytecode incompatibility)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=80 failures=0 errors=0 skipped=1
- **Updated:** BUILD FAILURE; surefire tests=80 failures=0 errors=79 skipped=1

**Initiating cause (Claude):** js-scriptengine 23.0.1 compiled for a newer Java than the image's Java 11: UnsupportedClassVersionError GraalJSEngineFactory

**Group evidence (COVERED):** UnsupportedClassVersionError naming class file 61.0 vs maximum 55.0.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 80, Failures: 0, Errors: 0, Skipped: 1
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 80, Failures: 0, Errors: 79, Skipped: 1
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0:test (default-test) on project a:
BRK sigs:  79x java.lang.UnsupportedClassVersionError: com/oracle/truffle/js/scriptengine/GraalJSEngineFactory has been compiled by a m
BRK link: UnsupportedClassVersionError, class file version
```

**Paths:** logs/0c088ff4_pre.log; logs/0c088ff4_breaking.log; audit_claude_review/digests/case007.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 8

- **Project / update:** pac4j/dropwizard-pac4j · `com.fasterxml.jackson.core:jackson-databind 2.10.5.1 -> 2.14.1`
- **Why sampled:** representative of JACKSON_MODULE_SKEW (25 cases)
- **Proposed label:** **NON_BEHAVIORAL** by rule **R1** (Linkage or bytecode incompatibility)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=16 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=16 failures=0 errors=16 skipped=0

**Initiating cause (Claude):** jackson-databind 2.14.1 needs com.fasterxml.jackson.core.util.JacksonFeature (jackson-core >=2.12); older jackson-core resolved -> NoClassDefFoundError

**Group evidence (STATIC_EVIDENCE):** NoClassDefFoundError/NoSuchMethodError on JacksonFeature/JsonKey/JsonMerge/StreamConstraintsException; archived jars show the class absent in the retained core/annotations (most cases from 15 on); class_origins in 123, 128, 135, 170.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 16, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 16, Failures: 0, Errors: 16, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0:test (default-test) on project dropwizard-pac4j:
 CB Caused by: java.lang.ClassNotFoundException: com.fasterxml.jackson.core.util.JacksonFeature
BRK sigs:  16x java.lang.NoClassDefFoundError: com/fasterxml/jackson/core/util/JacksonFeature
BRK link: ClassNotFoundException, NoClassDefFoundError
```

**Paths:** logs/0c748afc_pre.log; logs/0c748afc_breaking.log; audit_claude_review/digests/case008.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 9

- **Project / update:** pholser/junit-quickcheck · `org.mockito:mockito-core 4.11.0 -> 5.1.1`
- **Why sampled:** representative of MOCKITO5_INLINE_DEFAULT (5 cases)
- **Proposed label:** **BEHAVIORAL** by rule **R9** (Changed default in the updated library), category DEFAULT_SETTING_OR_POLICY
- **Codex label:** PROVISIONAL_BEHAVIORAL · **Claude blind label:** BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=1114 failures=0 errors=0 skipped=19
- **Updated:** BUILD FAILURE; surefire tests=510 failures=1 errors=0 skipped=18

**Initiating cause (Claude):** mockito-core 5.x switched the default mock maker from subclass to inline; CompositeGeneratorTest.shrinkingChoosesAComponentCapableOfShrinkingTheValue gets an empty shrink list (expected [3, 6] but was []) from mocked generators; no linkage/compile signal

**What changed:** Mocked collaborator behaviour changed under the new default mock maker (inline mocks intercept methods that previously ran real code); observable as an empty shrink result

**Group evidence (COVERED):** subclass_control passes in 52, 89, 98 (CompositeGeneratorTest) and 113 (OpencensusTracerFactoryTest); updated Mockito retained.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 510, Failures: 0, Errors: 0, Skipped: 18 || Tests run: 561, Failures: 0, Errors: 0, Skipped: 1 || Tests run: 11, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 32, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK reactor: junit-quickcheck   SUCCESS [  0.485 s]; junit-quickcheck-core   FAILURE [ 12.416 s]; junit-quickcheck-generators   SKIPPED; junit-quickcheck-guava   SKIPPED; junit-quickcheck-examples   SKIPPED; BUILD FAILURE
BRK agg: Tests run: 510, Failures: 1, Errors: 0, Skipped: 18
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0-M8:test (default-test) on project junit-quickcheck-core: There are test failures.
BRK sigs:  1x java.lang.AssertionError: expected:<[3, 6]> but was:<[]>
```

**Paths:** logs/0ee8b937_pre.log; logs/0ee8b937_breaking.log; audit_claude_review/digests/case009.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 11

- **Project / update:** leonardehrenfried/jspc-maven-plugin · `org.codehaus.plexus:plexus-utils 3.5.1 -> 4.0.0`
- **Why sampled:** representative of PLEXUS_UTILS_4_REMOVALS (3 cases)
- **Proposed label:** **NON_BEHAVIORAL** by rule **R1** (Linkage or bytecode incompatibility)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=22 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=22 failures=0 errors=16 skipped=0

**Initiating cause (Claude):** plexus-utils 4.0.0 removed org.codehaus.plexus.util.xml.XmlStreamReader (moved to plexus-xml) -> NoClassDefFoundError

**Group evidence (COVERED):** NoClassDefFoundError XmlStreamReader / XmlPullParserException; archived plexus-utils-4.0.0.jar.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 22, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 22, Failures: 0, Errors: 16, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0:test (default-test) on project jspc-maven-plugin:
 CB Caused by: java.lang.ClassNotFoundException: org.codehaus.plexus.util.xml.XmlStreamReader
BRK sigs:  16x java.lang.NoClassDefFoundError: org/codehaus/plexus/util/xml/XmlStreamReader
BRK link: ClassNotFoundException, NoClassDefFoundError
```

**Paths:** logs/test_failure_evidence/125f1253_pre.log; logs/test_failure_evidence/125f1253_breaking.log; audit_claude_review/digests/case011.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 13

- **Project / update:** damianszczepanik/cucumber-reporting · `commons-io:commons-io 2.7 -> 2.11.0`
- **Why sampled:** singleton mechanism
- **Proposed label:** **BEHAVIORAL** by rule **R12** (Core behavioral change (same API, same input, different observable result)), category EXCEPTION_TYPE_OR_CONDITION
- **Codex label:** PROVISIONAL_BEHAVIORAL · **Claude blind label:** BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=345 failures=0 errors=0 skipped=2
- **Updated:** BUILD FAILURE; surefire tests=345 failures=0 errors=1 skipped=2

**Initiating cause (Claude):** commons-io 2.11.0 FileUtils.copyFile now validates srcFile via requireFile and throws IllegalArgumentException for a directory; ReportBuilderTest.copyCustomResources_OnDirAsFile_ThrowsIOException expects IOException

**What changed:** Exception type for a directory passed as srcFile changed IOException -> IllegalArgumentException (input validation / exception contract)

**Group evidence (COVERED_BY_TRACE):** Trace shows FileUtils.requireFile throwing IllegalArgumentException where the test expects IOException.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 345, Failures: 0, Errors: 0, Skipped: 2
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 345, Failures: 0, Errors: 1, Skipped: 2
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.18.1:test (default-test) on project cucumber-reporting: There are test failures.
BRK sigs:  1x java.lang.IllegalArgumentException: Parameter 'srcFile' is not a file: src/test/resources/js
BRK console: SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder". | SLF4J: Defaulting to no-operation (NOP) logger implementation | SLF4J: See http://www.slf4j.org/codes.html#StaticLoggerBinder for further details. | WARNING: An illegal reflective access operation has occurred
```

**Paths:** logs/batch_triage/12684ee6_pre.log; logs/batch_triage/12684ee6_breaking.log; audit_claude_review/digests/case013.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 14

- **Project / update:** geosolutions-it/geostore · `com.h2database:h2 1.3.175 -> 2.0.206`
- **Why sampled:** representative of H2_VARCHAR_LIMIT (2 cases)
- **Proposed label:** **BEHAVIORAL** by rule **R12** (Core behavioral change (same API, same input, different observable result)), category ACCEPTED_INPUT
- **Codex label:** PROVISIONAL_BEHAVIORAL · **Claude blind label:** BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=190 failures=0 errors=0 skipped=36
- **Updated:** BUILD FAILURE; surefire tests=52 failures=0 errors=22 skipped=0

**Initiating cause (Claude):** H2 2.0.206 rejects DDL with VARCHAR(10000000) (exceeds new max length) during schema creation in GeoStore - Core - Persistence

**What changed:** Accepted SQL input changed: column length 10000000 for VARCHAR no longer accepted by H2 2.x

**Group evidence (COVERED):** H2PrecisionProbe (114): CREATE TABLE ... VARCHAR(10000000) accepted on 1.3.175, rejected on 2.1.210. Case 14 has a verified CLOB repair.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 9, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 11, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 32, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 4, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 41, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 5, Failures: 0, E
BRK status: [INFO] BUILD FAILURE
BRK reactor: Master GeoStore POM   SUCCESS [  0.262 s]; GeoStore - 0 Server Root   SUCCESS [  0.064 s]; GeoStore - Core   SUCCESS [  0.005 s]; GeoStore - Core - Model   SUCCESS [  7.515 s]; GeoStore - Core - Security   SUCCESS [  7.370 s]; GeoStore - Core - Persistence   FAILURE [ 15.638 s]; GeoStor
BRK agg: Tests run: 9, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 11, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 32, Failures: 0, Errors: 22, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.4.2:test (default-test) on project geostore-persistence: There are test failures.
BRK console: WARNING: An illegal reflective access operation has occurred | log4j:WARN No appenders could be found for logger (org.springframework.security.ldap.userdetails.LdapUserDetailsMapper). | log4j:WARN Please initialize the log4j system properly. | log4j:WARN See http://logging.apache.org/lo
```

**Paths:** logs/batch_triage/12e23771_pre.log; logs/batch_triage/12e23771_breaking.log; audit_claude_review/digests/case014.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 19

- **Project / update:** s4u/pgpverify-maven-plugin · `org.junit.jupiter:junit-jupiter-params 5.9.3 -> 5.10.0`
- **Why sampled:** representative of JUNIT_PLATFORM_SKEW (3 cases)
- **Proposed label:** **NON_BEHAVIORAL** by rule **R1** (Linkage or bytecode incompatibility)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=300 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=161 failures=0 errors=15 skipped=0

**Initiating cause (Claude):** junit-jupiter-params 5.10.0 run against junit-platform-commons 1.9.3 (archived jar) -> NoSuchMethodError ClassLoaderUtils.getClassLoader(Class)

**Group evidence (STATIC_EVIDENCE):** NoSuchMethodError ClassLoaderUtils.getClassLoader / parseQualifiedMethodName / getAncestors; archived jars.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 300, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 161, Failures: 0, Errors: 15, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0-M7:test (default-test) on project pgpverify-maven-plugin:
BRK sigs:  15x java.lang.NoSuchMethodError: 'java.lang.ClassLoader org.junit.platform.commons.util.ClassLoaderUtils.getClassLoader(java
BRK link: NoSuchMethodError
archived non-report files: pre=346 breaking=346 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -                <version>5.9.3</version>
   +                <version>5.10.0</version>
 SF ERROR org.simplify4u.plugins.ArtifactResolverTest#testEnablingValidatingPluginDependenciesEnablesPlugins(boolean, boolean, boolean, boolean) type=java.lang.NoSuchMethodError msg='java.lang.ClassLoader org.junit.platform.commons.util.ClassLoaderUtils.getClassLoader(java.lang.Class)'
 SF ERROR org.simplify4u.plugins.ShowMojoTest#shouldThrowExceptionForInvalidArtifact(String) type=java.lang.NoSuchMethodError msg='java.lang.ClassLoader org.junit.platform.commons.util.ClassLoaderUtils.getClassLoader(java.lang.Class)'
```

**Paths:** logs/batch_triage/19249139_pre.log; logs/batch_triage/19249139_breaking.log; logs/case19_evidence/; results/case19_review.md; audit_claude_review/digests/case019.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 20

- **Project / update:** apache/logging-chainsaw · `com.thoughtworks.xstream:xstream 1.4.17 -> 1.4.19`
- **Why sampled:** singleton mechanism
- **Proposed label:** **BEHAVIORAL** by rule **R12** (Core behavioral change (same API, same input, different observable result)), category DEFAULT_SETTING_OR_POLICY
- **Codex label:** PROVISIONAL_BEHAVIORAL · **Claude blind label:** BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=5 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=5 failures=0 errors=1 skipped=0

**Initiating cause (Claude):** XStream 1.4.19 (security framework default allow-list since 1.4.18) refuses to deserialize org.apache.log4j.chainsaw.LogPanelPreferenceModel -> ForbiddenClassException

**What changed:** Default deserialization security policy changed: types not explicitly allowed are now rejected

**Group evidence (COVERED_BY_TRACE):** ForbiddenClassException raised by XStream's security layer on the same round trip that passes in PRE.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 5, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 5, Failures: 0, Errors: 1, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.22.2:test (default-test) on project apache-chainsaw: There are test failures.
BRK sigs:  1x com.thoughtworks.xstream.security.ForbiddenClassException: org.apache.log4j.chainsaw.LogPanelPreferenceModel
archived non-report files: pre=317 breaking=317 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -      <version>1.4.17</version>
   +      <version>1.4.19</version>
 SF ERROR org.apache.log4j.chainsaw.LogPanelPreferenceModelTest#testLogPanelPreferenceModelSerialization type=com.thoughtworks.xstream.security.ForbiddenClassException msg=org.apache.log4j.chainsaw.LogPanelPreferenceModel
```

**Paths:** logs/batch_triage/19e20b0d_pre.log; logs/batch_triage/19e20b0d_breaking.log; logs/case20_evidence/; results/case20_review.md; audit_claude_review/digests/case020.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 25

- **Project / update:** elimu-ai/webapp · `org.apache.logging.log4j:log4j-api 2.16.0 -> 2.18.0`
- **Why sampled:** representative of LOG4J_API_CORE_SKEW (11 cases)
- **Proposed label:** **NON_BEHAVIORAL** by rule **R1** (Linkage or bytecode incompatibility)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=67 failures=0 errors=0 skipped=2
- **Updated:** BUILD FAILURE; surefire tests=61 failures=0 errors=48 skipped=1

**Initiating cause (Claude):** log4j-api 2.18.0 with log4j-core 2.16.0 (both archived) -> NoSuchMethodError LoaderUtil.getClassLoaders(); then 'Could not initialize class LoggerContext/SpringJUnit4ClassRunner/SyllableHelper' follow-ons

**Group evidence (STATIC_EVIDENCE):** NoSuchMethodError/NoClassDefFoundError/NoSuchFieldError from core into api; archived api/core jars; Case129LoggerProbe.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 67, Failures: 0, Errors: 0, Skipped: 2
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 61, Failures: 0, Errors: 48, Skipped: 1
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.22.2:test (default-test) on project webapp: There are test failures.
BRK sigs:  1x java.lang.NoSuchMethodError: 'java.lang.ClassLoader[] org.apache.logging.log4j.util.LoaderUtil.getClassLoaders()' || 38x java.lang.NoClassDefFoundError: Could not initialize class org.apache.logging.log4j.core.LoggerContext || 2x java.lang.NoClassDefFoundError: Could not initialize cla
BRK link: ClassNotFoundException, IllegalAccessError, IncompatibleClassChangeError, LinkageError, NoClassDefFoundError, NoSuchMethodError
archived non-report files: pre=820 breaking=820 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -            <version>2.16.0</version>
   +            <version>2.18.0</version>
 SF ERROR ai.elimu.dao.ApplicationDaoTest#initializationError type=java.lang.NoClassDefFoundError msg=Could not initialize class org.springframework.test.context.junit4.SpringJUnit4ClassRunner
 SF ERROR ai.elimu.dao.ApplicationVersionDaoTest#initializationError type=java.lang.NoClassDefFoundError msg=Could not initialize class org.springframework.test.context.junit4.SpringJUnit ...[cut]
```

**Paths:** logs/batch_triage/1eb6d9d5_pre.log; logs/batch_triage/1eb6d9d5_breaking.log; logs/case25_evidence/; results/case25_review.md; audit_claude_review/digests/case025.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 28

- **Project / update:** alphagov/pay-cardid · `org.dhatim:dropwizard-sentry 2.0.22 -> 2.0.28-8`
- **Why sampled:** representative of DROPWIZARD_SENTRY_CONFIG (5 cases)
- **Proposed label:** **BEHAVIORAL** by rule **R7** (Configuration property no longer accepted), category ACCEPTED_INPUT
- **Codex label:** PROVISIONAL_BEHAVIORAL · **Claude blind label:** BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=44 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=34 failures=0 errors=1 skipped=0

**Initiating cause (Claude):** dropwizard-sentry 2.0.28-8 sentry appender factory no longer accepts the config property logging.appenders[1].stacktraceAppPackages -> ConfigurationParsingException (UnrecognizedPropertyException) when CardIdResourceITest boots the app

**What changed:** Accepted configuration input changed: a previously valid YAML appender property is now rejected

**Group evidence (DECISION_ONLY):** appender_javap.txt (28, 35, 39) and appender_factory_inspection.json (162) show the factory's public fields; the property is absent in the updated factory.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 44, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 34, Failures: 0, Errors: 1, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.22.2:test (default-test) on project pay-cardid: There are test failures.
 CB Caused by: com.fasterxml.jackson.databind.exc.UnrecognizedPropertyException:
BRK sigs:  1x io.dropwizard.configuration.ConfigurationParsingException:
archived non-report files: pre=31 breaking=31 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -            <version>2.0.22</version>
   +            <version>2.0.28-8</version>
 SF ERROR uk.gov.pay.card.it.resources.CardIdResourceITest#uk.gov.pay.card.it.resources.CardIdResourceITest type=io.dropwizard.configuration.ConfigurationParsingException msg=/pay-cardid/target/classes/config/config.yaml has an error:   * Unrecognized field at: logging.appenders.[1].stacktraceAppPac
 CB Caused by: com.fasterxml.jackson.databind.exc.UnrecognizedPropertyException:
```

**Paths:** logs/batch_triage/22eec990_pre.log; logs/batch_triage/22eec990_breaking.log; logs/case28_evidence/; results/case28_review.md; audit_claude_review/digests/case028.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 30

- **Project / update:** retest/recheck · `org.eclipse.persistence:org.eclipse.persistence.moxy 3.0.2 -> 4.0.1`
- **Why sampled:** singleton mechanism
- **Proposed label:** **NON_BEHAVIORAL** by rule **R13** (Packaging change removes a runtime provider)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=737 failures=0 errors=0 skipped=4
- **Updated:** BUILD FAILURE; surefire tests=737 failures=0 errors=15 skipped=4

**Initiating cause (Claude):** EclipseLink MOXy 4.0.1 requires a pluggable ASM service; none on the classpath -> ValidationException EclipseLink-7359 'No any ASM service available' in ASMFactory initializer, then 14x 'Could not initialize class ASMFactory'

**Group evidence (DONE):** ValidationException 'No any ASM service available'. Control: add org.eclipse.persistence:org.eclipse.persistence.asm 4.0.1 and run XmlFolderPersistenceTest; pass -> packaging change (R13). | RESULT 2026-11-20: Control: + org.eclipse.persistence.asm 9.4.0 -> 737 tests, 0 F/0 E (reruns/case30_asm_provider_control.log)

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 737, Failures: 0, Errors: 0, Skipped: 4
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 737, Failures: 0, Errors: 15, Skipped: 4
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0-M6:test (default-test) on project recheck:
 CB Caused by: Exception [EclipseLink-7359] (Eclipse Persistence Services - 4.0.1.v202302241130): org.eclipse.persistence.exceptions.ValidationException
BRK sigs:  1x java.lang.ExceptionInInitializerError || 14x java.lang.NoClassDefFoundError: Could not initialize class org.eclipse.persistence.asm.ASMFactory
BRK console: WARNING: An illegal reflective access operation has occurred
BRK link: ClassNotFoundException, NoClassDefFoundError
archived non-report files: pre=596 breaking=596 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -			<version>3.0.2</version>
   +			<version>4.0.1</version>
 SF ERROR de.retest.recheck.LegacyCompatibilityFileNamerStrategyTest#default_test_class_name_should_be_implemented(Path) type=java.lang.NoClassDefFoundError msg=Could not initialize class org.eclipse.persistence.asm.ASMFactory
 SF ERROR de.retest.recheck.persistence.xml.XmlFolderPersistenceTest#simple_save_to_folder type=java.lang.NoClassDefFoundError msg=Could not initialize class org.eclipse.persistence.asm.ASMFactory
```

**Paths:** logs/batch_triage/25926ea2_pre.log; logs/batch_triage/25926ea2_breaking.log; logs/case30_evidence/; results/case30_review.md; audit_claude_review/digests/case030.txt; audit_claude_review/reruns/RESULTS.md

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 32

- **Project / update:** matteobaccan/html2pop3 · `ch.qos.logback:logback-classic 1.2.11 -> 1.4.0`
- **Why sampled:** representative of LOGBACK_CLASSIC_CORE_SKEW (5 cases)
- **Proposed label:** **NON_BEHAVIORAL** by rule **R1** (Linkage or bytecode incompatibility)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=5 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=5 failures=0 errors=2 skipped=0

**Initiating cause (Claude):** logback-classic 1.4.0 with logback-core 1.2.11 (archived) -> NoSuchMethodError EnvUtil.logbackVersion(); second error is follow-on 'Could not initialize class FilterTest'

**Group evidence (STATIC_EVIDENCE):** NoSuchMethodError/NoClassDefFoundError; resolved_jar_inspection (54) shows EnvUtil without logbackVersion.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 5, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 5, Failures: 0, Errors: 2, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0:test (default-test) on project HTML2POP3:
BRK sigs:  1x java.lang.NoSuchMethodError: 'java.lang.String ch.qos.logback.core.util.EnvUtil.logbackVersion()' || 1x java.lang.NoClassDefFoundError: Could not initialize class it.baccan.html2pop3.utils.FilterTest
BRK link: NoClassDefFoundError, NoSuchMethodError
archived non-report files: pre=66 breaking=66 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -            <version>1.2.11</version>
   +            <version>1.4.0</version>
 SF ERROR it.baccan.html2pop3.utils.FilterTest#testAdd type=java.lang.NoSuchMethodError msg='java.lang.String ch.qos.logback.core.util.EnvUtil.logbackVersion()'
 SF ERROR it.baccan.html2pop3.utils.FilterTest#testIsAllow type=java.lang.NoClassDefFoundError msg=Could not initialize class it.baccan.html2pop3.utils.FilterTest
```

**Paths:** logs/batch_triage/2b60dcd8_pre.log; logs/batch_triage/2b60dcd8_breaking.log; logs/case32_evidence/; results/case32_review.md; audit_claude_review/digests/case032.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 34

- **Project / update:** apache/directory-scimple · `javax:javaee-api 7.0 -> 8.0.1`
- **Why sampled:** singleton mechanism
- **Proposed label:** **NON_BEHAVIORAL** by rule **R1** (Linkage or bytecode incompatibility)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=717 failures=0 errors=0 skipped=17
- **Updated:** BUILD FAILURE; surefire tests=686 failures=0 errors=10 skipped=15

**Initiating cause (Claude):** javaee-api 8.0.1 (JAX-RS 2.1 API) on a classpath with resteasy-jaxrs 3.0.11.Final (JAX-RS 2.0 impl): AbstractMethodError in ResponseBuilderImpl; UnfinishedStubbing is follow-on

**Group evidence (COVERED):** AbstractMethodError; archived javaee-api 8.0.1 and resteasy 3.0.11 jars.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 448, Failures: 0, Errors: 0, Skipped: 8 || Tests run: 46, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 125, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 67, Failures: 0, Errors: 0, Skipped: 7 || Tests run: 31, Failures: 0, Errors: 0, Skipped: 2
BRK status: [INFO] BUILD FAILURE
BRK reactor: SCIM - Parent   SUCCESS [  2.620 s]; SCIM - Specification   SUCCESS [  0.079 s]; SCIM - Specification - Schema   SUCCESS [ 16.403 s]; SCIM - Specification - Protocol   SUCCESS [  5.230 s]; SCIM - Common   SUCCESS [  0.428 s]; SCIM - Client   SUCCESS [  4.151 s]; SCIM - Server   SUCCESS 
BRK agg: Tests run: 448, Failures: 0, Errors: 0, Skipped: 8 || Tests run: 46, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 125, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 67, Failures: 0, Errors: 10, Skipped: 7
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0-M5:test (default-test) on project scim-server-common: There are test failures.
BRK sigs:  9x java.lang.AbstractMethodError: Receiver class org.jboss.resteasy.specimpl.ResponseBuilderImpl does not define or inherit || 1x org.mockito.exceptions.misusing.UnfinishedStubbingException:
BRK link: AbstractMethodError
```

**Paths:** logs/batch_triage/2f9d75d4_pre.log; logs/batch_triage/2f9d75d4_breaking.log; logs/case34_evidence/; results/case34_review.md; audit_claude_review/digests/case034.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 37

- **Project / update:** International-Data-Spaces-Association/IDS-Messaging-Services · `org.springframework:spring-tx 5.3.24 -> 6.0.4`
- **Why sampled:** representative of JAVA17_BYTECODE_ON_JAVA11 (11 cases)
- **Proposed label:** **NON_BEHAVIORAL** by rule **R1** (Linkage or bytecode incompatibility)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=32 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=18 failures=0 errors=5 skipped=0

**Initiating cause (Claude):** spring-tx 6.0.4 classes are Java 17 bytecode (class file 61) on Java 11 -> UnsupportedClassVersionError TransactionDefinition, wrapped in BeanInstantiationException

**Group evidence (COVERED):** UnsupportedClassVersionError naming class file 61.0 vs maximum 55.0.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 6, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 12, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 2, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 6, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 3, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 3, Failures: 0, Err
BRK status: [INFO] BUILD FAILURE
BRK reactor: messaging-services   SUCCESS [  6.613 s]; core   SUCCESS [ 25.440 s]; messaging   FAILURE [ 12.718 s]; clearinghouse   SKIPPED; broker   SKIPPED; vocol   SKIPPED; paris   SKIPPED; appstore   SKIPPED; BUILD FAILURE
BRK agg: Tests run: 6, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 12, Failures: 0, Errors: 5, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.22.2:test (default-test) on project messaging: There are test failures.
 CB Caused by: java.lang.UnsupportedClassVersionError: org/springframework/transaction/TransactionDefinition has been compiled by a more recent version of the Java Runtime (class file version 61.0), this version of the Java 
 CB Caused by: java.lang.UnsupportedClassVersionError: org/springframework/transaction/TransactionDefinition has been compiled by a more recent version of the Java Runtime (class file version 61.0), this version of the Java 
BRK sigs:  5x org.springframework.beans.BeanInstantiationException: Failed to instantiate [org.springframework.test.context.transac ...[cut]
```

**Paths:** logs/batch_triage/31a177fb_pre.log; logs/batch_triage/31a177fb_breaking.log; logs/case37_evidence/; results/case37_review.md; audit_claude_review/digests/case037.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 42

- **Project / update:** camunda-community-hub/camunda-platform-7-camel · `jakarta.xml.bind:jakarta.xml.bind-api 2.3.2 -> 4.0.0`
- **Why sampled:** representative of JAVAX_JAKARTA_NAMESPACE (13 cases)
- **Proposed label:** **NON_BEHAVIORAL** by rule **R3** (javax/jakarta namespace migration)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=42 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=42 failures=0 errors=16 skipped=0

**Initiating cause (Claude):** jakarta.xml.bind-api 4.0.0 provides jakarta.xml.bind only; javax.xml.bind classes formerly supplied by 2.3.2 disappear -> NoClassDefFoundError javax/xml/bind/JAXBException in CamelNamespaceHandler -> ApplicationContext load failures

**Group evidence (COVERED_BY_TRACE):** Stack traces name javax classes or javax NoProviderFound; archived jars show only jakarta packages; AnnotationCompatibilityProbe (109); class_origins (124).

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 25, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 17, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK reactor: camunda BPM - Apache Camel Integration   SUCCESS [  0.298 s]; camunda BPM - Apache Camel Integration (Common)   SUCCESS [ 18.434 s]; camunda BPM - Apache Camel Integration (Common Test Resources) SUCCESS [  0.866 s]; camunda BPM - Apache Camel Integration (Spring)   FAILURE [ 28.622 s];
BRK agg: Tests run: 25, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 17, Failures: 0, Errors: 16, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.22.2:test (default-test) on project camunda-bpm-camel-spring: There are test failures.
 CB Caused by: org.springframework.beans.factory.BeanDefinitionStoreException: Unexpected exception parsing XML document from class path resource [start-process-from-route-config.xml]; nested exception is org.springframework
 CB Caused by: org.springframework.beans.BeanInstantiationException: Failed to instantiate [org.apache.camel.spring.xml.handler.CamelNamespaceHandler]: Unresolvable class definition; nested exception is java.lang.NoClassDefF
 CB Caused by: java.lang.NoClassDefFoundError: javax/xml/bind/JAXBException
BRK sigs:  16x java.lang.IllegalStateException: Failed to load ApplicationContext
BRK console: WARNING: An illegal reflective access operation has occurred
BRK link: ClassNotFoundException, NoClassDefFoundError
```

**Paths:** logs/batch_triage/3b26e047_pre.log; logs/batch_triage/3b26e047_breaking.log; logs/case42_evidence/; results/case42_review.md; audit_claude_review/digests/case042.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 44

- **Project / update:** pac4j/dropwizard-pac4j · `org.glassfish.jersey.core:jersey-server 2.32 -> 2.36`
- **Why sampled:** representative of JERSEY_JETTY_SKEW (11 cases)
- **Proposed label:** **NON_BEHAVIORAL** by rule **R1** (Linkage or bytecode incompatibility)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=16 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=16 failures=0 errors=10 skipped=0

**Initiating cause (Claude):** jersey-server 2.36 with jersey-common 2.32 (archived jars) -> NoClassDefFoundError org.glassfish.jersey.internal.DynamicFeatureConfigurator

**Group evidence (STATIC_EVIDENCE):** NoClassDefFoundError DynamicFeatureConfigurator / AbstractMethodError lifeCycleFailure / StopException; archived jars.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 16, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 16, Failures: 0, Errors: 10, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0:test (default-test) on project dropwizard-pac4j:
 CB Caused by: java.lang.ClassNotFoundException: org.glassfish.jersey.internal.DynamicFeatureConfigurator
BRK sigs:  10x java.lang.NoClassDefFoundError: org/glassfish/jersey/internal/DynamicFeatureConfigurator
BRK link: ClassNotFoundException, NoClassDefFoundError
archived non-report files: pre=27 breaking=27 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -        <version>2.32</version>
   +        <version>2.36</version>
 SF ERROR org.pac4j.dropwizard.bundle.BundleFactoryTest#emptyPac4jInConfig type=java.lang.NoClassDefFoundError msg=org/glassfish/jersey/internal/DynamicFeatureConfigurator
 SF ERROR org.pac4j.dropwizard.bundle.BundleFactoryTest#sessiondisabledForced type=java.lang.NoClassDefFoundError msg=org/glassfish/jersey/internal/DynamicFeatureConfigurator
 CB Caused by: java.lang.ClassNotFoundException: org.glassfish.jersey.internal.DynamicFeatureConfigurator
```

**Paths:** logs/batch_triage/3b7f524a_pre.log; logs/batch_triage/3b7f524a_breaking.log; logs/case44_evidence/; results/case44_review.md; audit_claude_review/digests/case044.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 46

- **Project / update:** retest/recheck.cli · `ch.qos.logback:logback-classic 1.2.11 -> 1.4.3`
- **Why sampled:** representative of SLF4J17_REMOVED_STATICLOGGERBINDER (6 cases)
- **Proposed label:** **NON_BEHAVIORAL** by rule **R6** (Retained API references a removed binding class)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=12 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=12 failures=2 errors=0 skipped=0

**Initiating cause (Claude):** logback-classic 1.4.3 no longer ships org.slf4j.impl.StaticLoggerBinder; the retained slf4j-api 1.7.36 (archived) looks up that removed binding class, fails ('Failed to load class StaticLoggerBinder') and falls back to NOP, so CLI log output is empty and 2 assertions fail

**Group evidence (COVERED):** Logs: 'Failed to load class org.slf4j.impl.StaticLoggerBinder'; archived logback-classic 1.4.x jars lack the class (resolved_jar_inspection in 66, 97).

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 12, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 12, Failures: 2, Errors: 0, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.22.2:test (default-test) on project recheck.cli: There are test failures.
BRK sigs:  2x java.lang.AssertionError:
BRK console: SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder". | SLF4J: Defaulting to no-operation (NOP) logger implementation | SLF4J: See http://www.slf4j.org/codes.html#StaticLoggerBinder for further details.
archived non-report files: pre=45 breaking=45 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -			<version>1.2.11</version>
   +			<version>1.4.3</version>
 SF FAILURE de.retest.recheck.cli.PreConditionTest#should_warn_when_not_a_recheck_project type=java.lang.AssertionError msg= Expecting actual:   "" to contain:   "Not a recheck project."
 SF FAILURE de.retest.recheck.cli.utils.SystemInUtilTest#should_repeatedly_ask_yes_or_no_when_input_is_invalid type=java.lang.AssertionError msg= Expecting actual:   "" to contain:   "Invalid input, please only use (y)es or (n)o:"
```

**Paths:** logs/batch_triage/41164ec5_pre.log; logs/batch_triage/41164ec5_breaking.log; logs/case46_evidence/; results/case46_review.md; audit_claude_review/digests/case046.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 49

- **Project / update:** Refactoring-Bot/Refactoring-Bot · `org.antlr:antlr4-runtime 4.7.2 -> 4.10.1`
- **Why sampled:** disputed label; representative of ANTLR_ATN_FORMAT (6 cases)
- **Proposed label:** **NON_BEHAVIORAL** by rule **R8** (Generator/runtime serialized-format alignment (ANTLR))
- **Codex label:** PROVISIONAL_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** YES
- **Baseline:** BUILD SUCCESS; surefire tests=62 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=62 failures=0 errors=1 skipped=0

**Initiating cause (Claude):** antlr4-runtime 4.10.1 refuses the serialized ATN (version 3) embedded in a parser generated by the 4.7.x tool -> InvalidClassException 'Could not deserialize ATN with version 3 (expected 4)' in static init (ExceptionInInitializerError)

**Group evidence (DECISION_ONLY):** lexer_probe in 112, 127, 140, 188: same compiled lexer, runtime 4.7/4.9 OK, 4.10+ rejects ATN v3 via the same deserialize(char[]) method.

**Codex comparison:** Codex: BEHAVIORAL (the same deserialize(char[]) API now rejects serialized ATN v3 = accepted input changed). Claude blind: NON_BEHAVIORAL (generated-code/runtime format alignment, repaired by regenerating with a matching tool). Both mechanisms agree; only the taxonomy differs. Post-comparison: UNCERTAIN pending human adjudication of the ANTLR family (6 cases, 3.2% of 188).

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 62, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 62, Failures: 0, Errors: 1, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.22.2:test (unit-tests) on project RefactoringBot: There are test failures.
 CB Caused by: java.lang.UnsupportedOperationException: java.io.InvalidClassException: org.antlr.v4.runtime.atn.ATN; Could not deserialize ATN with version 3 (expected 4).
 CB Caused by: java.io.InvalidClassException: org.antlr.v4.runtime.atn.ATN; Could not deserialize ATN with version 3 (expected 4).
 CB Caused by: java.lang.UnsupportedOperationException: java.io.InvalidClassException: org.antlr.v4.runtime.atn.ATN; Could not deserialize ATN with version 3 (expected 4).
BRK sigs:  1x java.lang.ExceptionInInitializerError
archived non-report files: pre=153 breaking=153 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -			<version>4.7.2</version>
   +			<version>4.10.1</version>
 SF ERROR de.refactoringbot.services.main.GrammarServiceTest#testCheckComment type=java.lang.ExceptionInInitializerError msg=
```

**Paths:** logs/batch_triage/448ff013_pre.log; logs/batch_triage/448ff013_breaking.log; logs/case49_evidence/; results/case49_review.md; audit_claude_review/digests/case049.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 53

- **Project / update:** codehaus-plexus/plexus-archiver · `org.codehaus.plexus:plexus-io 3.2.0 -> 3.3.0`
- **Why sampled:** singleton mechanism
- **Proposed label:** **BEHAVIORAL** by rule **R12** (Core behavioral change (same API, same input, different observable result)), category RETURN_VALUE
- **Codex label:** PROVISIONAL_BEHAVIORAL · **Claude blind label:** BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=177 failures=0 errors=0 skipped=2
- **Updated:** BUILD FAILURE; surefire tests=177 failures=0 errors=22 skipped=2

**Initiating cause (Claude):** plexus-io 3.3.0 no longer reports a symlink-to-directory resource as a directory (directory_probe: File.isDirectory=true but resource.isDirectory=false); plexus-archiver then throws ArchiverException 'Not a directory: .../symLinkToDirOnTheOutside'

**What changed:** Return value of PlexusIoResource.isDirectory() for symbolic links to directories changed true -> false

**Group evidence (COVERED):** DirectoryProbe: isDirectory true->false for a symlink to a directory.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 177, Failures: 0, Errors: 0, Skipped: 2
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 177, Failures: 0, Errors: 22, Skipped: 2
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.22.2:test (default-test) on project plexus-archiver: There are test failures.
BRK sigs:  13x org.codehaus.plexus.archiver.ArchiverException: Not a directory: test/resources/symlinks/src/symLinkToDirOnTheOutside || 1x org.codehaus.plexus.archiver.ArchiverException: Not a directory: bzz/symLinkToDirOnTheOutside || 1x org.codehaus.plexus.archiver.ArchiverException: Not a directo
archived non-report files: pre=212 breaking=212 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -      <version>3.2.0</version>
   +      <version>3.3.0</version>
 SF ERROR org.codehaus.plexus.archiver.SymlinkTest#testSymlinkDirArchiver type=org.codehaus.plexus.archiver.ArchiverException msg=Not a directory: symLinkToDirOnTheOutside
 SF ERROR org.codehaus.plexus.archiver.SymlinkTest#testSymlinkTar type=org.codehaus.plexus.archiver.ArchiverException msg=Not a directory: symLinkToDirOnTheOutside
```

**Paths:** logs/batch_triage/46698497_pre.log; logs/batch_triage/46698497_breaking.log; logs/case53_evidence/; results/case53_review.md; audit_claude_review/digests/case053.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 64

- **Project / update:** jenkinsci/github-checks-plugin · `org.jenkins-ci.plugins:github-api 1.117 -> 1.303-400.v35c2d8258028`
- **Why sampled:** singleton mechanism
- **Proposed label:** **NON_BEHAVIORAL** by rule **R10** (Tooling or test-infrastructure failure)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=49 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=49 failures=1 errors=0 skipped=0

**Initiating cause (Claude):** ArchUnit rule ArchitectureTest.NO_JENKINS_INSTANCE_CALL now scans io.jenkins.plugins.okhttp.api.JenkinsOkHttpClient from the new transitive okhttp-api 4.9.2 jar, which calls Jenkins.get(); static architecture violation caused by classpath contents, not runtime behaviour

**Group evidence (COVERED_BY_TRACE):** ArchUnit violation lists JenkinsOkHttpClient from the new transitive jar.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 49, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 49, Failures: 1, Errors: 0, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0-M4:test (default-test) on project github-checks: There are test failures.
BRK sigs:  1x java.lang.AssertionError:
archived non-report files: pre=55 breaking=55 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -      <version>1.117</version>
   +      <version>1.303-400.v35c2d8258028</version>
 SF FAILURE ArchitectureTest#NO_JENKINS_INSTANCE_CALL type=java.lang.AssertionError msg=
```

**Paths:** logs/batch_triage/52ba94ad_pre.log; logs/batch_triage/52ba94ad_breaking.log; logs/case64_evidence/; results/case64_review.md; audit_claude_review/digests/case064.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 67

- **Project / update:** btrplace/scheduler · `org.antlr:antlr4-runtime 4.9.3 -> 4.10`
- **Why sampled:** disputed label
- **Proposed label:** **NON_BEHAVIORAL** by rule **R8** (Generator/runtime serialized-format alignment (ANTLR))
- **Codex label:** PROVISIONAL_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** YES
- **Baseline:** BUILD SUCCESS; surefire tests=943 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=903 failures=1 errors=0 skipped=0

**Initiating cause (Claude):** antlr4-runtime 4.10 cannot deserialize ATN version 3 from a parser generated by the 4.9.x tool -> UnsupportedOperationException/InvalidClassException in safeplace

**Group evidence (DECISION_ONLY):** lexer_probe in 112, 127, 140, 188: same compiled lexer, runtime 4.7/4.9 OK, 4.10+ rejects ATN v3 via the same deserialize(char[]) method.

**Codex comparison:** Codex: BEHAVIORAL (the same deserialize(char[]) API now rejects serialized ATN v3 = accepted input changed). Claude blind: NON_BEHAVIORAL (generated-code/runtime format alignment, repaired by regenerating with a matching tool). Both mechanisms agree; only the taxonomy differs. Post-comparison: UNCERTAIN pending human adjudication of the ANTLR family (6 cases, 3.2% of 188).

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 260, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 93, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 241, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 271, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 38, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 2, Failures:
BRK status: [INFO] BUILD FAILURE
BRK reactor: scheduler   SUCCESS [  0.908 s]; scheduler-api   SUCCESS [ 15.404 s]; scheduler-json   SUCCESS [  7.521 s]; scheduler-choco   SUCCESS [01:53 min]; scheduler-examples   SUCCESS [  0.855 s]; btrpsl   SUCCESS [ 21.960 s]; safeplace   FAILURE [ 18.311 s]; bench   SKIPPED; scheduler-split   
BRK agg: Tests run: 260, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 93, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 241, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 271, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 38, Failures: 1, Errors: 0, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0-M5:test (default-test) on project safeplace: There are test failures.
 CB Caused by: java.lang.UnsupportedOperationException: java.io.InvalidClassException: org.antlr.v4.runtime.atn.ATN; Could not deserialize ATN with version 3 (expected 4).
 CB Caused by: java.io.InvalidClassException: org.antlr.v4.runtime.atn.ATN; Could not deserialize ATN with version 3 (expected 4).
 CB Caused by: java.lang.UnsupportedOperati ...[cut]
```

**Paths:** logs/batch_triage/5476e69f_pre.log; logs/batch_triage/5476e69f_breaking.log; logs/case67_evidence/; results/case67_review.md; audit_claude_review/digests/case067.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 69

- **Project / update:** fmtn/a · `org.graalvm.js:js-scriptengine 22.0.0 -> 22.1.0`
- **Why sampled:** disputed label; representative of GRAALJS (1 cases)
- **Proposed label:** **NON_BEHAVIORAL** by rule **R2** (Version skew within one library family)
- **Codex label:** PROVISIONAL_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** YES
- **Baseline:** BUILD SUCCESS; surefire tests=80 failures=0 errors=0 skipped=1
- **Updated:** BUILD FAILURE; surefire tests=80 failures=3 errors=9 skipped=1

**Initiating cause (Claude):** js-scriptengine 22.1.0 run with GraalVM js 22.0.0 and graal-sdk 22.0.0 (archived): the engine sets option js.charset, which the 22.0.0 language does not define -> IllegalArgumentException 'Could not find option with name js.charset'; assertion failures and FileNotFound dump.json are downstream

**Group evidence (DONE):** ScriptEngineProbe (69): PRE ok; BREAKING 'Could not find option with name js.charset' with js 22.0.0 retained. | RESULT 2026-11-20: Control: js 22.0.0 -> 22.1.0 (scriptengine 22.1.0 kept) -> 80 tests, 0 F/0 E (reruns/case69_graaljs_alignment_control.log)

**Codex comparison:** Codex: BEHAVIORAL (ScriptEngine 22.1.0 adds default option js.charset which retained GraalJS 22.0.0 rejects). Claude: NON_BEHAVIORAL because this is version skew between two GraalJS components, the same class as log4j api/core or logback classic/core skew, which both reviewers label NON_BEHAVIORAL. Maintained after comparison. CONTROL RESULT: aligning the retained GraalJS js artifact to 22.1.0 makes all 80 tests pass with the updated js-scriptengine retained, which supports NON_BEHAVIORAL (component skew, R2).

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 80, Failures: 0, Errors: 0, Skipped: 1
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 80, Failures: 3, Errors: 9, Skipped: 1
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0:test (default-test) on project a: There are test failures.
BRK sigs:  2x java.lang.AssertionError: A message is expected || 3x java.lang.IllegalArgumentException: Could not find option with name js.charset. || 1x java.io.FileNotFoundException: /tmp/junit13164462012255806981/junit16038784913987111075/dump.json (No such file or direc || 1x java.io.FileNotFoun
archived non-report files: pre=30 breaking=30 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -      <version>22.0.0</version>
   +      <version>22.1.0</version>
 SF FAILURE co.nordlander.a.AMQPTest#testBatch type=java.lang.AssertionError msg=A message is expected
 SF ERROR co.nordlander.a.AMQPTest#testCopyQueueWithTransformer type=java.lang.IllegalArgumentException msg=Could not find option with name js.charset.
```

**Paths:** logs/batch_triage/56b1cde5_pre.log; logs/batch_triage/56b1cde5_breaking.log; logs/case69_evidence/; results/case69_review.md; audit_claude_review/digests/case069.txt; audit_claude_review/reruns/RESULTS.md

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 70

- **Project / update:** jericks/geoserver-shell · `org.json:json 20090211 -> 20230227`
- **Why sampled:** singleton mechanism
- **Proposed label:** **BEHAVIORAL** by rule **R12** (Core behavioral change (same API, same input, different observable result)), category EXCEPTION_TYPE_OR_CONDITION
- **Codex label:** PROVISIONAL_BEHAVIORAL · **Claude blind label:** BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=205 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=205 failures=0 errors=2 skipped=0

**Initiating cause (Claude):** org.json 20230227 JSONObject.getString throws JSONException for a non-string (Integer) value; 20090211 coerced it to a string. Confirmed by archived JsonStringProbe (pre exit=0, breaking JSONException)

**What changed:** getString on an Integer-valued key changed from returning its string form to throwing JSONException

**Group evidence (COVERED):** JsonStringProbe: getString on an Integer returns a string in PRE, throws in BREAKING.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 205, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 205, Failures: 0, Errors: 2, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0:test (default-test) on project geoserver-shell:
BRK sigs:  1x org.json.JSONException: JSONObject["id"] is not a string (class java.lang.Integer : 0). || 1x org.json.JSONException: JSONObject["id"] is not a string (class java.lang.Integer : 1).
archived non-report files: pre=123 breaking=123 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -            <version>20090211</version>
   +            <version>20230227</version>
 SF ERROR org.geoserver.shell.ScriptCommandsTest#listSession type=org.json.JSONException msg=JSONObject["id"] is not a string (class java.lang.Integer : 0).
 SF ERROR org.geoserver.shell.ScriptCommandsTest#getSession type=org.json.JSONException msg=JSONObject["id"] is not a string (class java.lang.Integer : 1).
```

**Paths:** logs/batch_triage/57062474_pre.log; logs/batch_triage/57062474_breaking.log; logs/case70_evidence/; results/case70_review.md; audit_claude_review/digests/case070.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 71

- **Project / update:** googleapis/java-pubsublite · `com.google.flogger:google-extensions 0.6 -> 0.7.1`
- **Why sampled:** singleton mechanism
- **Proposed label:** **NON_BEHAVIORAL** by rule **R1** (Linkage or bytecode incompatibility)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=372 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=331 failures=0 errors=123 skipped=0

**Initiating cause (Claude):** google-extensions 0.7.1 with an older flogger core: DefaultPlatform fails with NoSuchMethodError StaticMethodCaller.callGetterFromSystemProperty -> IllegalStateException 'No logging platforms found' -> ExceptionInInitializerError, then 'Could not initialize class ApiServiceUtils' follow-ons [post-comparison provenance note: see root_cause_comparison]

**Group evidence (DONE):** NoSuchMethodError StaticMethodCaller. Run mvn dependency:tree to confirm flogger core 0.7.1 vs system-backend 0.6. | RESULT 2026-11-20: dependency:tree: flogger 0.7.1 with flogger-system-backend 0.6; Codex direction correct (reruns/case71_dependency_tree.log)

**Codex comparison:** Partial disagreement on provenance, now corrected in Claude's view: Codex identifies retained flogger-system-backend 0.6 calling a StaticMethodCaller method absent from resolved flogger core 0.7.1. That is consistent with DefaultPlatform living in the system backend. Claude's blind wording had the skew reversed.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 331, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 41, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK reactor: Google Cloud Pub/Sub Lite Parent 1.2.1-SNAPSHOT   SUCCESS [  8.071 s]; proto-google-cloud-pubsublite-v1 1.2.1-SNAPSHOT   SUCCESS [ 34.607 s]; grpc-google-cloud-pubsublite-v1 1.2.1-SNAPSHOT   SUCCESS [ 10.829 s]; Google Cloud Pub/Sub Lite 1.2.1-SNAPSHOT   FAILURE [01:23 min]; Pub/Sub Lit
BRK agg: Tests run: 331, Failures: 0, Errors: 123, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0-M5:test (default-test) on project google-cloud-pubsublite: There are test failures.
 CB Caused by: java.lang.IllegalStateException:
 CB Caused by: java.lang.IllegalStateException:
BRK sigs:  1x java.lang.ExceptionInInitializerError || 1x java.lang.NoClassDefFoundError: Could not initialize class com.google.cloud.pubsublite.internal.wire.ApiServiceUtils || 1x java.lang.NoClassDefFoundError: Could not initialize class com.google.common.flogger.backend.Platform$LazyHolder || 1x 
BRK link: NoClassDefFoundError, NoSuchMethodError
```

**Paths:** logs/batch_triage/5743793a_pre.log; logs/batch_triage/5743793a_breaking.log; logs/case71_evidence/; results/case71_review.md; audit_claude_review/digests/case071.txt; audit_claude_review/reruns/RESULTS.md

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 87

- **Project / update:** alphagov/pay-cardid · `org.dhatim:dropwizard-sentry 2.1.2-4 -> 4.0.1-2`
- **Why sampled:** representative of DROPWIZARD_SENTRY_DW4 (3 cases)
- **Proposed label:** **NON_BEHAVIORAL** by rule **R4** (Framework-generation mismatch)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=47 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=37 failures=0 errors=1 skipped=0

**Initiating cause (Claude):** dropwizard-sentry 4.0.1-2 targets Dropwizard 4: its service file registers io.dropwizard.logging.common.AppenderFactory, while the app uses dropwizard-logging 2.1.6 (io.dropwizard.logging.AppenderFactory), so type id 'sentry' cannot be resolved -> InvalidTypeIdException -> ConfigurationParsingException

**Group evidence (COVERED):** Jar service file registers io.dropwizard.logging.common.AppenderFactory (Dropwizard 4); 130 shows NoClassDefFoundError for the DW4 superclass.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 47, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 37, Failures: 0, Errors: 1, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.1.0:test (default-test) on project pay-cardid:
 CB Caused by: com.fasterxml.jackson.databind.exc.InvalidTypeIdException: Could not resolve type id 'sentry' as a subtype of `io.dropwizard.logging.AppenderFactory<ch.qos.logback.classic.spi.ILoggingEvent>`: known type ids =
BRK sigs:  1x io.dropwizard.configuration.ConfigurationParsingException:
archived non-report files: pre=31 breaking=31 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -            <version>2.1.2-4</version>
   +            <version>4.0.1-2</version>
 SF ERROR uk.gov.pay.card.it.resources.CardIdResourceITest# type=io.dropwizard.configuration.ConfigurationParsingException msg=/pay-cardid/target/classes/config/config.yaml has an error:   * Failed to parse configuration at: logging.appenders.[1]; Could not resolve type id 'sentry' as a subtype of `
 CB Caused by: com.fasterxml.jackson.databind.exc.InvalidTypeIdException: Could not resolve type id 'sentry' as a subtype of `io.dropwizard.logging.AppenderFactory<ch.qos.logback.classic.spi.ILoggingEvent>`: known type ids =
```

**Paths:** logs/batch_triage/770174eb_pre.log; logs/batch_triage/770174eb_breaking.log; logs/case87_evidence/; results/case87_review.md; audit_claude_review/digests/case087.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 91

- **Project / update:** spotify/semantic-metrics · `com.squareup.okhttp3:okhttp 3.3.1 -> 3.14.9`
- **Why sampled:** singleton mechanism
- **Proposed label:** **NON_BEHAVIORAL** by rule **R1** (Linkage or bytecode incompatibility)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=111 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=111 failures=0 errors=2 skipped=0

**Initiating cause (Claude):** okhttp 3.14.9 with mockwebserver 3.3.1 (resolved_jar_inspection): mockwebserver subclasses an okhttp internal class that is final in 3.14.9 -> VerifyError 'Cannot inherit from final class' (class_load_probe.log)

**Group evidence (COVERED):** ClassLoadProbe: VerifyError 'Cannot inherit from final class'.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 18, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 57, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 12, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 1, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 23, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK reactor: Semantic Metrics: Parent POM   SUCCESS [  6.255 s]; Semantic Metrics: API Package   SUCCESS [  7.542 s]; Semantic Metrics: Core   SUCCESS [  7.481 s]; Semantic Metrics: FFWD Reporter   SUCCESS [  4.069 s]; Semantic Metrics: Examples   SUCCESS [  0.487 s]; Semantic Metrics: Guava Extensi
BRK agg: Tests run: 18, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 57, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 12, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 1, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 23, Failures: 0, Errors: 2, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0:test (default-test) on project semantic-metrics-remote:
BRK sigs:  2x java.lang.VerifyError: Cannot inherit from final class
BRK console: WARNING: An illegal reflective access operation has occurred | SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder". | SLF4 ...[cut]
```

**Paths:** logs/batch_triage/851e6b16_pre.log; logs/batch_triage/851e6b16_breaking.log; logs/case91_evidence/; results/case91_review.md; audit_claude_review/digests/case091.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 104

- **Project / update:** open-pdf-sign/open-pdf-sign · `eu.europa.ec.joinup.sd-dss:dss-pades-pdfbox 5.9 -> 5.10.2`
- **Why sampled:** singleton mechanism
- **Proposed label:** **NON_BEHAVIORAL** by rule **R1** (Linkage or bytecode incompatibility)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=5 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=5 failures=0 errors=1 skipped=0

**Initiating cause (Claude):** dss-pades-pdfbox 5.10.2 with dss-pades 5.9 (archived) -> NoSuchMethodError PdfBoxSignatureService.checkDocumentPermissions(...)

**Group evidence (DONE):** NoSuchMethodError checkDocumentPermissions. Run mvn dependency:tree to confirm dss-pades 5.9 is pinned. | RESULT 2026-11-20: dependency:tree: dss-pades 5.9 declared directly next to dss-pades-pdfbox 5.10.2 (reruns/case104_dependency_tree.log)

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 5, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 5, Failures: 0, Errors: 1, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.22.2:test (default-test) on project openpdfsign: There are test failures.
BRK sigs:  1x java.lang.NoSuchMethodError: 'void eu.europa.esig.dss.pdf.pdfbox.PdfBoxSignatureService.checkDocumentPermissions(eu.euro
BRK link: NoSuchMethodError
archived non-report files: pre=23 breaking=23 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -            <version>5.9</version>
   +            <version>5.10.2</version>
 SF ERROR org.openpdfsign.SignerTest#testSignPdf type=java.lang.NoSuchMethodError msg='void eu.europa.esig.dss.pdf.pdfbox.PdfBoxSignatureService.checkDocumentPermissions(eu.europa.esig.dss.pdf.PdfDocumentReader)'
```

**Paths:** logs/batch_triage/8fe55d8b_pre.log; logs/batch_triage/8fe55d8b_breaking.log; logs/case104_evidence/; results/case104_review.md; audit_claude_review/digests/case104.txt; audit_claude_review/reruns/RESULTS.md

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 105

- **Project / update:** quick-perf/quickperf · `org.apache.logging.log4j:log4j-core 2.11.1 -> 2.16.0`
- **Why sampled:** representative of LOG4J_API_CORE_SKEW (11 cases)
- **Proposed label:** **NON_BEHAVIORAL** by rule **R1** (Linkage or bytecode incompatibility)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=309 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=309 failures=6 errors=4 skipped=0

**Initiating cause (Claude):** log4j-core 2.16.0 with an older log4j-api: ClassNotFoundException org.apache.logging.log4j.spi.LoggerContextShutdownAware -> 'Could not initialize class SpringJUnit4ClassRunner'; SQL-count assertion failures in forked-JVM tests are downstream

**Group evidence (STATIC_EVIDENCE):** NoSuchMethodError/NoClassDefFoundError/NoSuchFieldError from core into api; archived api/core jars; Case129LoggerProbe.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 41, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 44, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 6, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 14, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 6, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 116, Failures: 0,
BRK status: [INFO] BUILD FAILURE
BRK reactor: quick-perf   SUCCESS [  2.003 s]; quick-perf-core   SUCCESS [  8.002 s]; quick-perf-jvm-parent   SUCCESS [  0.015 s]; quick-perf-jvm-core   SUCCESS [  0.291 s]; quick-perf-jvm-annotations   SUCCESS [  6.736 s]; quick-perf-jfr-annotations   SUCCESS [  4.717 s]; quick-perf-sql-parent   SU
BRK agg: Tests run: 41, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 44, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 6, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 14, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 6, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 116, Failures: 0,
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.22.1:test (default-test) on project quick-perf-junit4-spring-boot-test: There are test failures.
BRK sigs:  5x java.lang.AssertionError: || 1x java.lang.NoClassDefFoundError: Could not initialize class org.springframework.test.context.junit4.SpringJUnit4ClassRunn || 1x java.lang.NoClassDefFoundError: Could not initialize class org.quickperf.spring.junit4.SpringRunnerWithQuickPerfFeatures || 1x 
```

**Paths:** logs/batch_triage/90690462_pre.log; logs/batch_triage/90690462_breaking.log; logs/case105_evidence/; results/case105_review.md; audit_claude_review/digests/case105.txt; audit_claude_review/reruns/RESULTS.md

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 108

- **Project / update:** jcabi/jcabi-ssh · `org.apache.sshd:sshd-common 2.9.2 -> 2.10.0`
- **Why sampled:** representative of SSHD_SKEW (2 cases)
- **Proposed label:** **NON_BEHAVIORAL** by rule **R1** (Linkage or bytecode incompatibility)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=5 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=5 failures=0 errors=3 skipped=0

**Initiating cause (Claude):** sshd-common 2.10.0 with sshd-core 2.9.2 (archived): SshServer.stop calls CloseFuture.await(Duration) missing -> NoSuchMethodError; the Connection reset error in SshByPasswordTest is consistent with the same server/client skew

**Group evidence (STATIC_EVIDENCE):** NoSuchMethodError CloseFuture.await(Duration) / NoClassDefFoundError CancelOption; archived jars.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 5, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 5, Failures: 0, Errors: 3, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0-M7:test (default-test) on project jcabi-ssh:
 CB Caused by: com.jcraft.jsch.JSchException: Session.connect: java.net.SocketException: Connection reset
 CB Caused by: java.net.SocketException: Connection reset
BRK sigs:  1x java.io.IOException: com.jcraft.jsch.JSchException: Session.connect: java.net.SocketException: Connection reset || 2x java.lang.NoSuchMethodError: 'boolean org.apache.sshd.common.future.CloseFuture.await(java.time.Duration)'
BRK link: NoSuchMethodError
archived non-report files: pre=25 breaking=25 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -      <version>2.9.2</version>
   +      <version>2.10.0</version>
 SF ERROR com.jcabi.ssh.SshByPasswordTest#executesCommand type=java.io.IOException msg=com.jcraft.jsch.JSchException: Session.connect: java.net.SocketException: Connection reset
 CB Caused by: com.jcraft.jsch.JSchException: Session.connect: java.net.SocketException: Connection reset
 SF ERROR com.jcabi.ssh.SshTest#executeCommandOnServerWithPrivateKey type=java.lang.NoSuchMethodError msg='boolean org.apache.sshd.common.future.CloseFuture.await(java.time.Duration)'
```

**Paths:** logs/batch_triage/93ac5faf_pre.log; logs/batch_triage/93ac5faf_breaking.log; logs/case108_evidence/; results/case108_review.md; audit_claude_review/digests/case108.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 109

- **Project / update:** pmckeown/dependency-track-maven-plugin · `com.google.inject:guice 5.1.0 -> 7.0.0`
- **Why sampled:** disputed label; representative of JAVAX_JAKARTA_NAMESPACE (13 cases)
- **Proposed label:** **NON_BEHAVIORAL** by rule **R3** (javax/jakarta namespace migration)
- **Codex label:** PROVISIONAL_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** YES
- **Baseline:** BUILD SUCCESS; surefire tests=223 failures=0 errors=0 skipped=3
- **Updated:** BUILD FAILURE; surefire tests=223 failures=0 errors=54 skipped=3

**Initiating cause (Claude):** Guice 7.0.0 only recognises jakarta.inject qualifiers; org.eclipse.sisu.Parameters is annotated @javax.inject.Qualifier, so Key.get rejects it ('not a binding annotation') -> ExceptionInInitializerError ParameterKeys -> 53 follow-on errors. AnnotationCompatibilityProbe reproduces with Guice 7 and passes with 5.1.0

**Group evidence (COVERED_BY_TRACE):** Stack traces name javax classes or javax NoProviderFound; archived jars show only jakarta packages; AnnotationCompatibilityProbe (109); class_origins (124).

**Codex comparison:** Codex: BEHAVIORAL (Guice 7 no longer recognises javax.inject.Qualifier). Claude: NON_BEHAVIORAL as a javax->jakarta namespace migration. Codex labels the analogous hibernate-validator javax/jakarta cases (83, 93, 164, 180) NON_BEHAVIORAL, so Codex's own labels are inconsistent across namespace migrations. Maintained after comparison; adjudicate jointly with 83/93/164/180.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 223, Failures: 0, Errors: 0, Skipped: 3
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 223, Failures: 0, Errors: 54, Skipped: 3
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.1.2:test (default-test) on project dependency-track-maven-plugin:
 CB Caused by: java.lang.IllegalArgumentException: org.eclipse.sisu.Parameters is not a binding annotation. Please annotate it with @BindingAnnotation.
BRK sigs:  1x java.lang.ExceptionInInitializerError || 53x java.lang.NoClassDefFoundError: Could not initialize class org.eclipse.sisu.wire.ParameterKeys
BRK console: SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder". | SLF4J: Defaulting to no-operation (NOP) logger implementation | SLF4J: See http://www.slf4j.org/codes.html#StaticLoggerBinder for further details.
BRK link: NoClassDefFoundError
archived non-report files: pre=151 breaking=151 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -            <version>5.1.0</version>
   +            <version>7.0.0</version>
 SF ERROR io.github.pmckeown.dependencytrack.finding.FindingsMojoIntegrationTest#thatBuildFailsWhenFindingsNumberBreachesDefinedThresholds type=java.lang.NoClassDefFoundError msg=Could not initialize class org.eclipse.sisu.wire.ParameterKeys
 SF ERROR i ...[cut]
```

**Paths:** logs/batch_triage/94380c9e_pre.log; logs/batch_triage/94380c9e_breaking.log; logs/case109_evidence/; results/case109_review.md; audit_claude_review/digests/case109.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 112

- **Project / update:** Refactoring-Bot/Refactoring-Bot · `org.antlr:antlr4-runtime 4.7.2 -> 4.12.0`
- **Why sampled:** disputed label
- **Proposed label:** **NON_BEHAVIORAL** by rule **R8** (Generator/runtime serialized-format alignment (ANTLR))
- **Codex label:** PROVISIONAL_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** YES
- **Baseline:** BUILD SUCCESS; surefire tests=62 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=62 failures=0 errors=1 skipped=0

**Initiating cause (Claude):** antlr4-runtime 4.12.0 cannot deserialize ATN version 3 from a parser generated with the 4.7.x tool -> ExceptionInInitializerError

**Group evidence (DECISION_ONLY):** lexer_probe in 112, 127, 140, 188: same compiled lexer, runtime 4.7/4.9 OK, 4.10+ rejects ATN v3 via the same deserialize(char[]) method.

**Codex comparison:** Codex: BEHAVIORAL (the same deserialize(char[]) API now rejects serialized ATN v3 = accepted input changed). Claude blind: NON_BEHAVIORAL (generated-code/runtime format alignment, repaired by regenerating with a matching tool). Both mechanisms agree; only the taxonomy differs. Post-comparison: UNCERTAIN pending human adjudication of the ANTLR family (6 cases, 3.2% of 188).

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 62, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 62, Failures: 0, Errors: 1, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.22.2:test (unit-tests) on project RefactoringBot: There are test failures.
 CB Caused by: java.lang.UnsupportedOperationException: java.io.InvalidClassException: org.antlr.v4.runtime.atn.ATN; Could not deserialize ATN with version 3 (expected 4).
 CB Caused by: java.io.InvalidClassException: org.antlr.v4.runtime.atn.ATN; Could not deserialize ATN with version 3 (expected 4).
 CB Caused by: java.lang.UnsupportedOperationException: java.io.InvalidClassException: org.antlr.v4.runtime.atn.ATN; Could not deserialize ATN with version 3 (expected 4).
BRK sigs:  1x java.lang.ExceptionInInitializerError
archived non-report files: pre=153 breaking=153 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -			<version>4.7.2</version>
   +			<version>4.12.0</version>
 SF ERROR de.refactoringbot.services.main.GrammarServiceTest#testCheckComment type=java.lang.ExceptionInInitializerError msg=
```

**Paths:** logs/batch_triage/99ec071a_pre.log; logs/batch_triage/99ec071a_breaking.log; logs/case112_evidence/; results/case112_review.md; audit_claude_review/digests/case112.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 116

- **Project / update:** jenkinsci/incrementals-tools · `org.codehaus.mojo:versions-maven-plugin 2.15.0 -> 2.16.0`
- **Why sampled:** singleton mechanism
- **Proposed label:** **NON_BEHAVIORAL** by rule **R10** (Tooling or test-infrastructure failure)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=7 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=0 failures=0 errors=0 skipped=0

**Initiating cause (Claude):** versions-maven-plugin 2.16.0 adds junit:junit 3.8.x (via plexus-container-default/plexus deps, debug classpath in discovery_classpaths.json) to the incrementals-maven-plugin test classpath; the JUnit Vintage engine fails to discover tests

**Group evidence (DONE):** Vintage engine discovery fails; the underlying exception was not captured. Run the failing module with -Dsurefire.trimStackTrace=false and keep the .dumpstream; expect a JUnit 3.8 version rejection. | RESULT 2026-11-20: Surefire dump: Unsupported version of junit:junit: 3.8.1 (reruns/case116_vintage_discovery.log)

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 5, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 2, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK reactor: Incrementals Tools POM   SUCCESS [  1.623 s]; lib   SUCCESS [  4.546 s]; incrementals-maven-plugin   FAILURE [ 13.702 s]; Git Changelist Maven Extension   SKIPPED; incrementals-enforcer-rules   SKIPPED; BUILD FAILURE
BRK agg: Tests run: 0, Failures: 0, Errors: 0, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0:test (default-test) on project incrementals-maven-plugin:
archived non-report files: pre=19 breaking=19 changed=1 added=0 removed=0
DIFF maven-plugin/pom.xml (7 lines):
   -            <version>2.15.0</version>
   +            <version>2.16.0</version>
```

**Paths:** logs/batch_triage/a047d2d3_pre.log; logs/batch_triage/a047d2d3_breaking.log; logs/case116_evidence/; results/case116_review.md; audit_claude_review/digests/case116.txt; audit_claude_review/reruns/RESULTS.md

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 127

- **Project / update:** Refactoring-Bot/Refactoring-Bot · `org.antlr:antlr4-runtime 4.7.2 -> 4.11.1`
- **Why sampled:** disputed label
- **Proposed label:** **NON_BEHAVIORAL** by rule **R8** (Generator/runtime serialized-format alignment (ANTLR))
- **Codex label:** PROVISIONAL_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** YES
- **Baseline:** BUILD SUCCESS; surefire tests=62 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=62 failures=0 errors=1 skipped=0

**Initiating cause (Claude):** antlr4-runtime 4.11.1 cannot deserialize ATN version 3 from the 4.7.x-generated parser

**Group evidence (DECISION_ONLY):** lexer_probe in 112, 127, 140, 188: same compiled lexer, runtime 4.7/4.9 OK, 4.10+ rejects ATN v3 via the same deserialize(char[]) method.

**Codex comparison:** Codex: BEHAVIORAL (the same deserialize(char[]) API now rejects serialized ATN v3 = accepted input changed). Claude blind: NON_BEHAVIORAL (generated-code/runtime format alignment, repaired by regenerating with a matching tool). Both mechanisms agree; only the taxonomy differs. Post-comparison: UNCERTAIN pending human adjudication of the ANTLR family (6 cases, 3.2% of 188).

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 62, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 62, Failures: 0, Errors: 1, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.22.2:test (unit-tests) on project RefactoringBot: There are test failures.
 CB Caused by: java.lang.UnsupportedOperationException: java.io.InvalidClassException: org.antlr.v4.runtime.atn.ATN; Could not deserialize ATN with version 3 (expected 4).
 CB Caused by: java.io.InvalidClassException: org.antlr.v4.runtime.atn.ATN; Could not deserialize ATN with version 3 (expected 4).
 CB Caused by: java.lang.UnsupportedOperationException: java.io.InvalidClassException: org.antlr.v4.runtime.atn.ATN; Could not deserialize ATN with version 3 (expected 4).
BRK sigs:  1x java.lang.ExceptionInInitializerError
archived non-report files: pre=153 breaking=153 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -			<version>4.7.2</version>
   +			<version>4.11.1</version>
 SF ERROR de.refactoringbot.services.main.GrammarServiceTest#testCheckComment type=java.lang.ExceptionInInitializerError msg=
```

**Paths:** logs/batch_triage/aaffc267_pre.log; logs/batch_triage/aaffc267_breaking.log; logs/case127_evidence/; results/case127_review.md; audit_claude_review/digests/case127.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 138

- **Project / update:** versly/wsdoc · `org.yaml:snakeyaml 1.13 -> 1.32`
- **Why sampled:** representative of SNAKEYAML_RAML_SKEW (2 cases)
- **Proposed label:** **NON_BEHAVIORAL** by rule **R1** (Linkage or bytecode incompatibility)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=59 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=59 failures=20 errors=0 skipped=0

**Initiating cause (Claude):** snakeyaml 1.32 removed/changed SequenceNode.getFlowStyle() returning Boolean used by raml-parser 0.9-SNAPSHOT (archived) -> NoSuchMethodError

**Group evidence (COVERED):** NoSuchMethodError SequenceNode.getFlowStyle() returning Boolean; archived raml-parser jar.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 59, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 59, Failures: 20, Errors: 0, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0:test (default-test) on project versly-wsdoc: There are test failures.
BRK sigs:  20x java.lang.NoSuchMethodError: 'java.lang.Boolean org.yaml.snakeyaml.nodes.SequenceNode.getFlowStyle()'
BRK console: log4j:WARN No appenders could be found for logger (freemarker.cache). | log4j:WARN Please initialize the log4j system properly. | log4j:WARN See http://logging.apache.org/log4j/1.2/faq.html#noconfig for more info.
BRK link: NoSuchMethodError
archived non-report files: pre=71 breaking=71 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -            <version>1.13</version>
   +            <version>1.32</version>
 SF FAILURE org.versly.rest.wsdoc.JaxRSRestAnnotationProcessorTest#apiLevelDocs type=java.lang.NoSuchMethodError msg='java.lang.Boolean org.yaml.snakeyaml.nodes.SequenceNode.getFlowStyle()'
 SF FAILURE org.versly.rest.wsdoc.JaxRSRestAnnotationProcessorTest#assertNoRedundantUriParametersForResource type=java.lang.NoSuchMethodError msg='java.lang.Boolean org.yaml.snakeyaml.nodes.SequenceNode.getFlowStyle()'
```

**Paths:** logs/batch_triage/bbb6f746_pre.log; logs/batch_triage/bbb6f746_breaking.log; logs/case138_evidence/; results/case138_review.md; audit_claude_review/digests/case138.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 140

- **Project / update:** btrplace/scheduler · `org.antlr:antlr4-runtime 4.9.3 -> 4.10.1`
- **Why sampled:** disputed label
- **Proposed label:** **NON_BEHAVIORAL** by rule **R8** (Generator/runtime serialized-format alignment (ANTLR))
- **Codex label:** PROVISIONAL_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** YES
- **Baseline:** BUILD SUCCESS; surefire tests=944 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=904 failures=1 errors=0 skipped=0

**Initiating cause (Claude):** antlr4-runtime 4.10.1 cannot deserialize ATN version 3 from the 4.9.x-generated parser in safeplace

**Group evidence (DECISION_ONLY):** lexer_probe in 112, 127, 140, 188: same compiled lexer, runtime 4.7/4.9 OK, 4.10+ rejects ATN v3 via the same deserialize(char[]) method.

**Codex comparison:** Codex: BEHAVIORAL (the same deserialize(char[]) API now rejects serialized ATN v3 = accepted input changed). Claude blind: NON_BEHAVIORAL (generated-code/runtime format alignment, repaired by regenerating with a matching tool). Both mechanisms agree; only the taxonomy differs. Post-comparison: UNCERTAIN pending human adjudication of the ANTLR family (6 cases, 3.2% of 188).

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 260, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 93, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 242, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 271, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 38, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 2, Failures:
BRK status: [INFO] BUILD FAILURE
BRK reactor: scheduler   SUCCESS [  1.620 s]; scheduler-api   SUCCESS [ 17.196 s]; scheduler-json   SUCCESS [  5.395 s]; scheduler-choco   SUCCESS [01:22 min]; scheduler-examples   SUCCESS [  0.496 s]; btrpsl   SUCCESS [ 10.972 s]; safeplace   FAILURE [ 11.165 s]; bench   SKIPPED; scheduler-split   
BRK agg: Tests run: 260, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 93, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 242, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 271, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 38, Failures: 1, Errors: 0, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0-M6:test (default-test) on project safeplace: There are test failures.
 CB Caused by: java.lang.UnsupportedOperationException: java.io.InvalidClassException: org.antlr.v4.runtime.atn.ATN; Could not deserialize ATN with version 3 (expected 4).
 CB Caused by: java.io.InvalidClassException: org.antlr.v4.runtime.atn.ATN; Could not deserialize ATN with version 3 (expected 4).
BRK sigs:  1x java.lang.ExceptionInIniti ...[cut]
```

**Paths:** logs/batch_triage/bc209e43_pre.log; logs/batch_triage/bc209e43_breaking.log; logs/case140_evidence/; results/case140_review.md; audit_claude_review/digests/case140.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 158

- **Project / update:** lookfirst/sardine · `org.apache.httpcomponents:httpclient 4.5.1 -> 4.5.13`
- **Why sampled:** singleton mechanism
- **Proposed label:** **BEHAVIORAL** by rule **R12** (Core behavioral change (same API, same input, different observable result)), category OUTPUT_FORMAT
- **Codex label:** PROVISIONAL_BEHAVIORAL · **Claude blind label:** BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=26 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=26 failures=1 errors=0 skipped=0

**Initiating cause (Claude):** httpclient 4.5.13 HttpResponseException now builds its message as 'status code: 400, reason phrase: ...'; the sardine test expects the bare reason phrase (Case158MessageProbeTest archived)

**What changed:** Exception message format changed (status code and reason phrase prefixed)

**Group evidence (COVERED):** Case158MessageProbeTest: HttpResponseException message format differs between versions.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 26, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 26, Failures: 1, Errors: 0, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.19:test (default-test) on project sardine: There are test failures.
BRK sigs:  1x org.junit.ComparisonFailure: expected:<[]m (400 response phra...> but was:<[status code: 400, reason phrase: ]m (400 res
archived non-report files: pre=138 breaking=138 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -            <version>4.5.1</version>
   +            <version>4.5.13</version>
 SF FAILURE com.github.sardine.impl.SardineExceptionTest#testMessage type=org.junit.ComparisonFailure msg=expected:<[]m (400 response phra...> but was:<[status code: 400, reason phrase: ]m (400 response phra...>
```

**Paths:** logs/batch_triage/d4aade95_pre.log; logs/batch_triage/d4aade95_breaking.log; logs/case158_evidence/; results/case158_review.md; audit_claude_review/digests/case158.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 161

- **Project / update:** takari/polyglot-maven · `org.jetbrains.kotlin:kotlin-stdlib 1.3.31 -> 1.6.0`
- **Why sampled:** singleton mechanism
- **Proposed label:** **NON_BEHAVIORAL** by rule **R11** (Fixture-only edit)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=302 failures=0 errors=0 skipped=7
- **Updated:** BUILD FAILURE; surefire tests=302 failures=1 errors=0 skipped=7

**Initiating cause (Claude):** Fixture-only edit: the only changed file is the test resource polyglot-kotlin/src/test/resources/example/pom.xml (kotlin-stdlib 1.3.31 -> 1.6.0 inside an example POM). The project's own POMs and therefore its test classpath are unchanged (all_poms: 1 of 145 changed, and it is the fixture). KotlinModelReaderTests compares the parsed Kotlin model against this fixture -> ComparisonFailure

**Group evidence (COVERED):** Only a test-resource POM changed; Codex reports identical test classpaths (34) and kotlin-stdlib jar hash.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 7, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 1, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 80, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 31, Failures: 0, Errors: 0, Skipped: 7 || Tests run: 33, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 5, Failures: 0, E
BRK status: [INFO] BUILD FAILURE
BRK reactor: Polyglot :: Aggregator   SUCCESS [  1.104 s]; Polyglot :: Common   SUCCESS [ 25.783 s]; Polyglot :: Atom   SUCCESS [  5.285 s]; Polyglot :: Maven Plugin   SUCCESS [  2.869 s]; Polyglot :: Ruby   SUCCESS [02:57 min]; Polyglot :: Scala   SUCCESS [01:03 min]; Polyglot :: Groovy   SUCCESS [
BRK agg: Tests run: 7, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 1, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 80, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 31, Failures: 0, Errors: 0, Skipped: 7 || Tests run: 33, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 5, Failures: 0, E
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.22.0:test (default-test) on project polyglot-kotlin: There are test failures.
BRK sigs:  1x org.junit.ComparisonFailure:
BRK console: SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerB ...[cut]
```

**Paths:** logs/batch_triage/d9a0df6f_pre.log; logs/batch_triage/d9a0df6f_breaking.log; logs/case161_evidence/; results/case161_review.md; audit_claude_review/digests/case161.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 163

- **Project / update:** btrplace/scheduler · `net.minidev:json-smart 2.4.8 -> 2.4.9`
- **Why sampled:** representative of JSON_SMART_DEPTH_LIMIT (2 cases)
- **Proposed label:** **BEHAVIORAL** by rule **R12** (Core behavioral change (same API, same input, different observable result)), category ACCEPTED_INPUT
- **Codex label:** PROVISIONAL_BEHAVIORAL · **Claude blind label:** BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=966 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=617 failures=2 errors=0 skipped=0

**Initiating cause (Claude):** json-smart 2.4.9 introduces a nesting-depth limit; parsing btrplace JSON instances now throws ParseException 'Malicious payload, having non natural depths' (positions 141434 and 49876) in IssuesTest

**What changed:** Accepted input changed: deeply nested JSON documents previously parsed are now rejected

**Group evidence (COVERED_BY_TRACE):** PRE passes on the same fixtures; only json/pom.xml changes; the exception comes from json-smart's own depth check ('Malicious payload, having non natural depths').

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 260, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 93, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 264, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 271, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 38, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 2, Failures:
BRK status: [INFO] BUILD FAILURE
BRK reactor: scheduler   SUCCESS [  0.415 s]; scheduler-api   SUCCESS [  7.631 s]; scheduler-json   SUCCESS [  2.657 s]; scheduler-choco   FAILURE [02:25 min]; scheduler-examples   SKIPPED; btrpsl   SKIPPED; safeplace   SKIPPED; bench   SKIPPED; scheduler-split   SKIPPED; BUILD FAILURE
BRK agg: Tests run: 260, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 93, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 264, Failures: 2, Errors: 0, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0-M7:test (default-test) on project scheduler-choco: There are test failures.
 CB Caused by: org.btrplace.json.JSONConverterException: net.minidev.json.parser.ParseException: Malicious payload, having non natural depths, parsing stoped on { at position 141434.
 CB Caused by: net.minidev.json.parser.ParseException: Malicious payload, having non natural depths, parsing stoped on { at position 141434.
BRK sigs:  2x java.lang.IllegalArgumentException: org.btrplace.json.JSONConverterException: net.minidev.json.parser.ParseException: Ma
BRK console: SLF4J: No SLF4J providers were found. | SLF4 ...[cut]
```

**Paths:** logs/batch_triage/db4b37b7_pre.log; logs/batch_triage/db4b37b7_breaking.log; logs/case163_evidence/; results/case163_review.md; audit_claude_review/digests/case163.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 178

- **Project / update:** kstateome/lti-launch · `org.springframework:spring-webmvc 4.1.6.RELEASE -> 5.3.18`
- **Why sampled:** singleton mechanism
- **Proposed label:** **NON_BEHAVIORAL** by rule **R1** (Linkage or bytecode incompatibility)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=1 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=1 failures=0 errors=1 skipped=0

**Initiating cause (Claude):** spring-webmvc 5.3.18 with older spring-web (4.1.x line) -> NoClassDefFoundError org.springframework.web.util.pattern.PathPatternParser

**Group evidence (DONE):** NoClassDefFoundError PathPatternParser. Run mvn dependency:tree to confirm the spring-web version. | RESULT 2026-11-20: dependency:tree: spring-web 4.1.6.RELEASE with spring-webmvc 5.3.18 (reruns/case178_dependency_tree.log)

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 1, Failures: 0, Errors: 1, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.19.1:test (default-test) on project lti-launch: There are test failures.
 CB Caused by: java.lang.ClassNotFoundException: org.springframework.web.util.pattern.PathPatternParser
 CB Caused by: java.lang.ClassNotFoundException: org.springframework.web.util.pattern.PathPatternParser
BRK sigs:  1x java.lang.NoClassDefFoundError: org/springframework/web/util/pattern/PathPatternParser
BRK link: ClassNotFoundException, NoClassDefFoundError
archived non-report files: pre=28 breaking=28 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -        <version>4.1.6.RELEASE</version>
   +        <version>5.3.18</version>
 SF ERROR edu.ksu.lti.launch.test.SpringContextITest#testSpringContext type=java.lang.NoClassDefFoundError msg=org/springframework/web/util/pattern/PathPatternParser
 CB Caused by: java.lang.ClassNotFoundException: org.springframework.web.util.pattern.PathPatternParser
```

**Paths:** logs/batch_triage/f61b113c_pre.log; logs/batch_triage/f61b113c_breaking.log; logs/case178_evidence/; results/case178_review.md; audit_claude_review/digests/case178.txt; audit_claude_review/reruns/RESULTS.md

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 181

- **Project / update:** SPARQL-Anything/sparql.anything · `org.jsoup:jsoup 1.14.2 -> 1.15.3`
- **Why sampled:** singleton mechanism
- **Proposed label:** **BEHAVIORAL** by rule **R12** (Core behavioral change (same API, same input, different observable result)), category OUTPUT_FORMAT
- **Codex label:** PROVISIONAL_BEHAVIORAL · **Claude blind label:** BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=240 failures=0 errors=0 skipped=14
- **Updated:** BUILD FAILURE; surefire tests=57 failures=2 errors=0 skipped=4

**Initiating cause (Claude):** jsoup 1.15.3 serialises the same HTML fixture differently (archived html_probe_by_element: PRE '<body> | <div ...' vs BREAKING '<body>| <div ...', whitespace/pretty-print change), so the HTML triplifier output differs and HTMLMicrodataTest isomorphism assertions fail

**What changed:** Element.html()/outerHtml output format (whitespace normalisation) changed

**Group evidence (COVERED):** html_probe_by_element: html() whitespace differs for the same fixture.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 19, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 1, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 12, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 6, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 7, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 7, Failures: 0, Er
BRK status: [INFO] BUILD FAILURE
BRK reactor: sparql.anything   SUCCESS [  1.546 s]; sparql-anything-model   SUCCESS [ 26.978 s]; sparql-anything-metadata   SUCCESS [  3.593 s]; sparql-anything-parser   SUCCESS [  4.802 s]; sparql-anything-csv   SUCCESS [  6.195 s]; sparql-anything-testutils   SUCCESS [  0.460 s]; sparql-anything-x
BRK agg: Tests run: 19, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 1, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 12, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 6, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 7, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 7, Failures: 0, Er
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.0.0:test (default-test) on project sparql-anything-html: There are test failures.
BRK sigs:  2x java.lang.AssertionError
```

**Paths:** logs/batch_triage/fa6503da_pre.log; logs/batch_triage/fa6503da_breaking.log; logs/case181_evidence/; results/case181_review.md; audit_claude_review/digests/case181.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 183

- **Project / update:** quarkiverse/quarkus-micrometer-registry · `io.quarkiverse.googlecloudservices:quarkus-google-cloud-common-grpc 1.4.0 -> 2.2.0`
- **Why sampled:** singleton mechanism
- **Proposed label:** **NON_BEHAVIORAL** by rule **R1** (Linkage or bytecode incompatibility)
- **Codex label:** NON_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** NO
- **Baseline:** BUILD SUCCESS; surefire tests=19 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=19 failures=0 errors=1 skipped=0

**Initiating cause (Claude):** quarkus-google-cloud-common-grpc 2.2.0 brings proto-google-common-protos compiled against a newer protobuf-java; with the resolved older protobuf -> IllegalAccessError LazyStringArrayList.emptyList() during Quarkus start

**Group evidence (COVERED):** IllegalAccessError; jar_inspection lists proto-google-common-protos 2.22.1 with protobuf-java 3.14.0.

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 2, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 2, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 1, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 2, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 3, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 2, Failures: 0, Erro
BRK status: [INFO] BUILD FAILURE
BRK reactor: Quarkus Micrometer Registry - Parent   SUCCESS [  9.204 s]; Quarkus Micrometer Registry - Azure Monitor - Parent SUCCESS [  0.207 s]; Quarkus Micrometer Registry - Azure Monitor - Runtime SUCCESS [ 35.714 s]; Quarkus Micrometer Registry - Azure Monitor - Deployment SUCCESS [01:22 min]; 
BRK agg: Tests run: 2, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 2, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 1, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 2, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 3, Failures: 0, Errors: 0, Skipped: 0 || Tests run: 2, Failures: 0, Erro
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.1.2:test (default-test) on project quarkus-micrometer-registry-it-native:
 CB Caused by: java.lang.RuntimeException: Failed to start quarkus
 CB Caused by: java.lang.IllegalAccessError: class com.google.api.MetricDescriptor tried to access method 'com.google.protobuf.LazyStringArrayList com.google.protobuf.LazyStringArrayList.emptyList()' (com.google.api.MetricDe
BRK sigs:  1x java.lang.RuntimeExceptio ...[cut]
```

**Paths:** logs/batch_triage/fb40f5e5_pre.log; logs/batch_triage/fb40f5e5_breaking.log; logs/case183_evidence/; results/case183_review.md; audit_claude_review/digests/case183.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

---

## Case 188

- **Project / update:** Refactoring-Bot/Refactoring-Bot · `org.antlr:antlr4-runtime 4.7.2 -> 4.10`
- **Why sampled:** disputed label
- **Proposed label:** **NON_BEHAVIORAL** by rule **R8** (Generator/runtime serialized-format alignment (ANTLR))
- **Codex label:** PROVISIONAL_BEHAVIORAL · **Claude blind label:** NON_BEHAVIORAL · **Changes Codex's label:** YES
- **Baseline:** BUILD SUCCESS; surefire tests=62 failures=0 errors=0 skipped=0
- **Updated:** BUILD FAILURE; surefire tests=62 failures=0 errors=1 skipped=0

**Initiating cause (Claude):** antlr4-runtime 4.10 cannot deserialize ATN version 3 from the 4.7.x-generated parser

**Group evidence (DECISION_ONLY):** lexer_probe in 112, 127, 140, 188: same compiled lexer, runtime 4.7/4.9 OK, 4.10+ rejects ATN v3 via the same deserialize(char[]) method.

**Codex comparison:** Codex: BEHAVIORAL (the same deserialize(char[]) API now rejects serialized ATN v3 = accepted input changed). Claude blind: NON_BEHAVIORAL (generated-code/runtime format alignment, repaired by regenerating with a matching tool). Both mechanisms agree; only the taxonomy differs. Post-comparison: UNCERTAIN pending human adjudication of the ANTLR family (6 cases, 3.2% of 188).

**Evidence excerpt** (from the original logs and archives):

```
PRE status: [INFO] BUILD SUCCESS
PRE agg: Tests run: 62, Failures: 0, Errors: 0, Skipped: 0
BRK status: [INFO] BUILD FAILURE
BRK agg: Tests run: 62, Failures: 0, Errors: 1, Skipped: 0
 ERR [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.22.2:test (unit-tests) on project RefactoringBot: There are test failures.
 CB Caused by: java.lang.UnsupportedOperationException: java.io.InvalidClassException: org.antlr.v4.runtime.atn.ATN; Could not deserialize ATN with version 3 (expected 4).
 CB Caused by: java.io.InvalidClassException: org.antlr.v4.runtime.atn.ATN; Could not deserialize ATN with version 3 (expected 4).
 CB Caused by: java.lang.UnsupportedOperationException: java.io.InvalidClassException: org.antlr.v4.runtime.atn.ATN; Could not deserialize ATN with version 3 (expected 4).
BRK sigs:  1x java.lang.ExceptionInInitializerError
archived non-report files: pre=153 breaking=153 changed=1 added=0 removed=0
DIFF pom.xml (7 lines):
   -			<version>4.7.2</version>
   +			<version>4.10</version>
 SF ERROR de.refactoringbot.services.main.GrammarServiceTest#testCheckComment type=java.lang.ExceptionInInitializerError msg=
```

**Paths:** logs/batch_triage/ff98f9e9_pre.log; logs/batch_triage/ff98f9e9_breaking.log; logs/case188_evidence/; results/case188_review.md; audit_claude_review/digests/case188.txt

**Checklist**

- [ ] 1. The first error in the BREAKING log is the cause named above, not a follow-on ("Could not initialize class", an assertion on null output).
- [ ] 2. Test counts match the Maven summary.
- [ ] 3. Only the dependency version changed, or what else changed is noted.
- [ ] 4. The control, probe or trace supports the label under the approved rule.
- [ ] 5. Label recorded in `human_sample.csv`.

