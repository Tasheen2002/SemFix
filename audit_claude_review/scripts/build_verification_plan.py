"""Generate verification_plan/control_plan.csv and verification_plan/human_sample.csv."""
import csv, os, sys
ROOT = sys.argv[1]
A = lambda *a: os.path.join(ROOT, "audit_claude_review", *a)
OUT = A("verification_plan"); os.makedirs(OUT, exist_ok=True)
rows = list(csv.DictReader(open(A("claude_audit.csv"), encoding="utf-8")))
by = {}
for r in rows:
    by.setdefault(r["related_group"].split(" | ")[0], []).append(r)

# family -> (rule, decisive question, existing evidence, status, proposed control, representative case)
F = {
 "SLF4J2_IGNORES_LEGACY_BINDING": ("R5", "Does the updated API select a different logger while the old binding is still on the classpath?",
   "LoggerSelectionProbe in 18 cases (117,132,134,142,144,145,147,148,150,151,153,155,156,159,171,184,185,186): PRE selects the binding's logger, BREAKING selects NOP with the same jars. All 36 logs print 'Ignoring binding found at ...'.",
   "DECISION_ONLY", "None needed. The open item is rule R5.", ""),
 "SLF4J17_REMOVED_STATICLOGGERBINDER": ("R6", "Does the retained API reference a binding class the update removed?",
   "Logs: 'Failed to load class org.slf4j.impl.StaticLoggerBinder'; archived logback-classic 1.4.x jars lack the class (resolved_jar_inspection in 66, 97).",
   "COVERED", "None needed.", ""),
 "MOCKITO5_INLINE_DEFAULT": ("R9", "Does the failing test pass on the updated Mockito when only the mock maker is reset to subclass?",
   "subclass_control passes in 52, 89, 98 (CompositeGeneratorTest) and 113 (OpencensusTracerFactoryTest); updated Mockito retained.",
   "COVERED", "Optional: the same subclass control for Case 9 (same test as 52/89/98).", "9"),
 "H2_VARCHAR_LIMIT": ("R12", "Does the same DDL succeed on the old H2 and fail on the new one?",
   "H2PrecisionProbe (114): CREATE TABLE ... VARCHAR(10000000) accepted on 1.3.175, rejected on 2.1.210. Case 14 has a verified CLOB repair.",
   "COVERED", "None needed.", ""),
 "JSON_SMART_DEPTH_LIMIT": ("R12", "Does json-smart 2.4.9 reject the same fixture that 2.4.8 parses?",
   "PRE passes on the same fixtures; only json/pom.xml changes; the exception comes from json-smart's own depth check ('Malicious payload, having non natural depths').",
   "COVERED_BY_TRACE", "Optional: a 10-line parse probe of the IssuesTest fixture on both jars.", "163"),
 "DROPWIZARD_SENTRY_CONFIG": ("R7", "Was the YAML property removed from SentryAppenderFactory?",
   "appender_javap.txt (28, 35, 39) and appender_factory_inspection.json (162) show the factory's public fields; the property is absent in the updated factory.",
   "DECISION_ONLY", "None needed. The open item is rule R7.", ""),
 "DROPWIZARD_SENTRY_DW4": ("R4", "Is the updated plugin built for a different framework major version?",
   "Jar service file registers io.dropwizard.logging.common.AppenderFactory (Dropwizard 4); 130 shows NoClassDefFoundError for the DW4 superclass.",
   "COVERED", "None needed.", ""),
 "ANTLR_ATN_FORMAT": ("R8", "Does the same generated lexer initialise on the old runtime and fail on the new one, with no linkage error?",
   "lexer_probe in 112, 127, 140, 188: same compiled lexer, runtime 4.7/4.9 OK, 4.10+ rejects ATN v3 via the same deserialize(char[]) method.",
   "DECISION_ONLY", "None needed. The open item is rule R8.", ""),
 "GRAALJS": ("R2", "Does aligning the retained GraalJS components to 22.1.0 make the tests pass?",
   "ScriptEngineProbe (69): PRE ok; BREAKING 'Could not find option with name js.charset' with js 22.0.0 retained.",
   "NEEDS_RUN", "Alignment control: add org.graalvm.js:js and org.graalvm.sdk:graal-sdk 22.1.0 next to js-scriptengine 22.1.0; run AMQPTest. Pass -> component skew (R2).", "69"),
 "JAVAX_JAKARTA_NAMESPACE": ("R3", "Is the failure a javax vs jakarta namespace mismatch (missing javax class, or no provider for the javax API)?",
   "Stack traces name javax classes or javax NoProviderFound; archived jars show only jakarta packages; AnnotationCompatibilityProbe (109); class_origins (124).",
   "COVERED_BY_TRACE", "Optional representatives: (a) 58: add a jakarta-matching JAXB API, or pin jaxb-impl 2.x alongside; (b) 109: upgrade sisu to a jakarta.inject-aware release. Pass -> namespace migration (R3).", "58;109"),
 "JACKSON_MODULE_SKEW": ("R1", "Is the initiating error a missing class or method from a Jackson module left at an older version?",
   "NoClassDefFoundError/NoSuchMethodError on JacksonFeature/JsonKey/JsonMerge/StreamConstraintsException; archived jars show the class absent in the retained core/annotations (most cases from 15 on); class_origins in 123, 128, 135, 170.",
   "STATIC_EVIDENCE", "Optional representative alignment control: Case 8, set jackson-core and jackson-annotations to the databind version.", "8"),
 "LOG4J_API_CORE_SKEW": ("R1", "Is the initiating error a missing API member between log4j-api and log4j-core?",
   "NoSuchMethodError/NoClassDefFoundError/NoSuchFieldError from core into api; archived api/core jars; Case129LoggerProbe.",
   "STATIC_EVIDENCE", "Optional representative: Case 25, align log4j-core to log4j-api 2.18.0.", "25"),
 "LOGBACK_CLASSIC_CORE_SKEW": ("R1", "Is the initiating error a missing logback-core member?",
   "NoSuchMethodError/NoClassDefFoundError; resolved_jar_inspection (54) shows EnvUtil without logbackVersion.",
   "STATIC_EVIDENCE", "Optional representative: Case 32, align logback-core to 1.4.0.", "32"),
 "POI_MODULE_MIX": ("R1", "Do assertion failures follow a POI linkage error swallowed by Tika?",
   "Tika logs NoSuchMethodError/IncompatibleClassChangeError/NoSuchFieldError before each null-text assertion; archived mixed-version POI jars.",
   "STATIC_EVIDENCE", "Optional representative: Case 6, align poi, poi-ooxml and poi-scratchpad to 5.1.0. Pass -> skew confirmed (assertions were downstream).", "6"),
 "JERSEY_JETTY_SKEW": ("R1", "Is the initiating error a missing class or abstract method between jersey-server/jersey-common or jetty-server/jetty-util?",
   "NoClassDefFoundError DynamicFeatureConfigurator / AbstractMethodError lifeCycleFailure / StopException; archived jars.",
   "STATIC_EVIDENCE", "Optional representatives: 44 (align jersey-common 2.36) and 75 (align jetty-util 9.4.50).", "44;75"),
 "JAVA17_BYTECODE_ON_JAVA11": ("R1", "Is the class-file version above what the Java 11 runtime accepts?",
   "UnsupportedClassVersionError naming class file 61.0 vs maximum 55.0.",
   "COVERED", "None needed (the JVM error is decisive).", ""),
 "PLEXUS_UTILS_4_REMOVALS": ("R1", "Was the class removed from plexus-utils 4?",
   "NoClassDefFoundError XmlStreamReader / XmlPullParserException; archived plexus-utils-4.0.0.jar.",
   "COVERED", "None needed.", ""),
 "JUNIT_PLATFORM_SKEW": ("R1", "Does a JUnit module call a member missing from the retained platform module?",
   "NoSuchMethodError ClassLoaderUtils.getClassLoader / parseQualifiedMethodName / getAncestors; archived jars.",
   "STATIC_EVIDENCE", "Optional representative: Case 19, align junit-platform-commons to 1.10.0.", "19"),
 "SURFIRE_PROVIDER_TOOLING": ("R10", "", "", "", "", ""),
 "SUREFIRE_PROVIDER_TOOLING": ("R10", "Does the Surefire plugin fail before running tests because of a provider/plugin API mismatch?",
   "'An API incompatibility was encountered' with NoSuchMethodError in the plugin realm; directoryscanner_javap (63, 86). Five IDS images fail in different modules.",
   "COVERED", "None needed.", ""),
 "SSHD_SKEW": ("R1", "Is the initiating error a missing member between sshd-core and sshd-common?",
   "NoSuchMethodError CloseFuture.await(Duration) / NoClassDefFoundError CancelOption; archived jars.",
   "STATIC_EVIDENCE", "Optional representative: Case 108, align sshd-core 2.10.0 (also tells whether the Connection reset error is skew-driven).", "108"),
 "SNAKEYAML_RAML_SKEW": ("R1", "Does the retained raml-parser call a changed SnakeYAML method descriptor?",
   "NoSuchMethodError SequenceNode.getFlowStyle() returning Boolean; archived raml-parser jar.",
   "COVERED", "None needed.", ""),
}
SINGLE = {
 "13": ("R12", "COVERED_BY_TRACE", "Trace shows FileUtils.requireFile throwing IllegalArgumentException where the test expects IOException.", ""),
 "20": ("R12", "COVERED_BY_TRACE", "ForbiddenClassException raised by XStream's security layer on the same round trip that passes in PRE.", ""),
 "30": ("R13", "NEEDS_RUN", "ValidationException 'No any ASM service available'. Control: add org.eclipse.persistence:org.eclipse.persistence.asm 4.0.1 and run XmlFolderPersistenceTest; pass -> packaging change (R13).", "30"),
 "34": ("R1", "COVERED", "AbstractMethodError; archived javaee-api 8.0.1 and resteasy 3.0.11 jars.", ""),
 "53": ("R12", "COVERED", "DirectoryProbe: isDirectory true->false for a symlink to a directory.", ""),
 "64": ("R10", "COVERED_BY_TRACE", "ArchUnit violation lists JenkinsOkHttpClient from the new transitive jar.", ""),
 "70": ("R12", "COVERED", "JsonStringProbe: getString on an Integer returns a string in PRE, throws in BREAKING.", ""),
 "71": ("R1", "NEEDS_RUN", "NoSuchMethodError StaticMethodCaller. Run mvn dependency:tree to confirm flogger core 0.7.1 vs system-backend 0.6.", "71"),
 "91": ("R1", "COVERED", "ClassLoadProbe: VerifyError 'Cannot inherit from final class'.", ""),
 "104": ("R1", "NEEDS_RUN", "NoSuchMethodError checkDocumentPermissions. Run mvn dependency:tree to confirm dss-pades 5.9 is pinned.", "104"),
 "116": ("R10", "NEEDS_RUN", "Vintage engine discovery fails; the underlying exception was not captured. Run the failing module with -Dsurefire.trimStackTrace=false and keep the .dumpstream; expect a JUnit 3.8 version rejection.", "116"),
 "158": ("R12", "COVERED", "Case158MessageProbeTest: HttpResponseException message format differs between versions.", ""),
 "161": ("R11", "COVERED", "Only a test-resource POM changed; Codex reports identical test classpaths (34) and kotlin-stdlib jar hash.", ""),
 "178": ("R1", "NEEDS_RUN", "NoClassDefFoundError PathPatternParser. Run mvn dependency:tree to confirm the spring-web version.", "178"),
 "181": ("R12", "COVERED", "html_probe_by_element: html() whitespace differs for the same fixture.", ""),
 "183": ("R1", "COVERED", "IllegalAccessError; jar_inspection lists proto-google-common-protos 2.22.1 with protobuf-java 3.14.0.", ""),
}
PROV = ["3", "21", "105", "122", "143"]  # dependency:tree only, extends 71/104/178

cp = []
for fam, cases in by.items():
    nums = [r["case_number"] for r in cases]
    beh = sum(r["claude_label_post_comparison"] == "BEHAVIORAL" for r in cases)
    if fam == "SINGLETON":
        for r in cases:
            rule, st, ev, rep = SINGLE[r["case_number"]]
            cp.append(dict(group=f"SINGLETON:{r['dependency']}", rule=rule, cases=r["case_number"], n=1,
                           codex_labels=r["codex_label"], claude_labels=r["claude_label_post_comparison"],
                           decisive_question="See existing_evidence", existing_evidence=ev, status=st,
                           proposed_control=ev if st == "NEEDS_RUN" else "None needed.", run_case=rep))
        continue
    rule, q, ev, st, ctl, rep = F[fam]
    cl = sorted({r["codex_label"] for r in cases}); ml = sorted({r["claude_label_post_comparison"] for r in cases})
    cp.append(dict(group=fam, rule=rule, cases=" ".join(nums), n=len(nums), codex_labels="/".join(cl), claude_labels="/".join(ml),
                   decisive_question=q, existing_evidence=ev, status=st, proposed_control=ctl, run_case=rep))
for n in PROV:
    cp.append(dict(group="PROVENANCE_CHECK", rule="-", cases=n, n=1, codex_labels="", claude_labels="", decisive_question="Which companion version is actually resolved?",
                   existing_evidence="Missing-class trace; resolved jar not archived or only one side archived.", status="NEEDS_RUN",
                   proposed_control="mvn -o dependency:tree in the BREAKING image (no tests).", run_case=n))
cols = ["group", "rule", "n", "cases", "codex_labels", "claude_labels", "status", "decisive_question", "existing_evidence", "proposed_control", "run_case"]
with open(os.path.join(OUT, "control_plan.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(cp)

# Human sample: all disputed, all singletons, 1 representative per family (+1 from a different project for families >= 10)
rk = {r["case_number"]: r for r in rows}
sample = {}
def add(n, why):
    sample.setdefault(n, []).append(why)
for r in rows:
    if r["label_agreement"] == "DISAGREE": add(r["case_number"], "disputed label")
for fam, cases in by.items():
    if fam == "SINGLETON":
        for r in cases: add(r["case_number"], "singleton mechanism")
        continue
    reps = []
    for r in cases:
        if r["case_number"] in sample: reps.append(r); break
    if not reps: reps.append(cases[0])
    if len(cases) >= 10:
        p0 = reps[0]["project"]
        other = next((r for r in cases if r["project"] != p0), None)
        if other: reps.append(other)
    for r in reps: add(r["case_number"], f"representative of {fam} ({len(cases)} cases)")
CHECK = ("1) First failure in the BREAKING log is the cause Claude/Codex name (not a follow-on). "
         "2) Counts match the Maven summary. 3) Only the dependency version changed (or note what else). "
         "4) Control/probe result in control_plan.csv supports the label under the approved rule. 5) Assign label.")
hs = []
for n in sorted(sample, key=int):
    r = rk[n]
    hs.append(dict(case_number=n, case_id=r["case_id"], project=r["project"], dependency=f"{r['dependency']} {r['old_version']} -> {r['new_version']}",
                   group=r["related_group"].split(" | ")[0], selected_because="; ".join(sample[n]),
                   codex_label=r["codex_label"], claude_label=r["claude_label_post_comparison"], primary_cause_claude=r["primary_cause"][:400],
                   evidence_paths=r["evidence_paths"], checklist=CHECK, human_label="", human_confidence="", human_notes="", reviewer_name="", review_date=""))
with open(os.path.join(OUT, "human_sample.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(hs[0])); w.writeheader(); w.writerows(hs)
import collections
print("control rows", len(cp), collections.Counter(c["status"] for c in cp))
print("runs needed", [c["run_case"] for c in cp if c["status"] == "NEEDS_RUN"])
print("optional runs", [c["run_case"] for c in cp if c["status"] != "NEEDS_RUN" and c["run_case"]])
print("human sample", len(hs), collections.Counter(h["selected_because"].split(";")[0].split(" (")[0].split(" of ")[0] for h in hs))
