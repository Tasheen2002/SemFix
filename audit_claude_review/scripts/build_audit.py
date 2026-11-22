"""Build audit_claude_review/claude_audit.csv from the frozen blind labels, original-log outcomes and the Codex comparison."""
import csv, json, os, re, sys

ROOT = sys.argv[1]
P = lambda *a: os.path.join(ROOT, *a)
A = lambda *a: P("audit_claude_review", *a)

cands = list(csv.DictReader(open(P("results", "test_failure_candidates.csv"), encoding="utf-8")))
cx = {r["case_id"]: r for r in csv.DictReader(open(P("results", "behavioral_classification.csv"), encoding="utf-8"))}
blind = {int(r["n"]): r for r in csv.DictReader(open(A("claude_blind_labels.tsv"), encoding="utf-8"), delimiter="\t")}
counts = {r["n"]: r for r in json.load(open(A("count_check.json"), encoding="utf-8"))}
corr = {c["case"]: c for c in json.load(open(A("corrections_applied.json"), encoding="utf-8"))}


def status(path):
    raw = open(P(path), "rb").read()
    t = raw.decode("utf-16", "replace") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8", "replace")
    s = re.findall(r"BUILD (SUCCESS|FAILURE)", t)
    return s[-1] if s else "NO_BUILD_LINE"


# Mechanism families for evaluation-split grouping (derived from the blind primary cause + dependency)
FAMILIES = [
    ("SLF4J2_IGNORES_LEGACY_BINDING", lambda c, d: "slf4j-api 2" in c and ("ignores" in c or "binding ignored" in c or "Same as Case" in c and d == "slf4j-api")),
    ("SLF4J17_REMOVED_STATICLOGGERBINDER", lambda c, d: "StaticLoggerBinder" in c and "removed" in c or ("Same as Case 46" in c)),
    ("JACKSON_MODULE_SKEW", lambda c, d: "jackson" in c.lower() and ("NoClassDefFoundError" in c or "NoSuchMethodError" in c or "JsonKey" in c or "JacksonFeature" in c or "JsonMerge" in c)),
    ("LOG4J_API_CORE_SKEW", lambda c, d: "log4j-" in c and ("NoSuchMethodError" in c or "ServiceLoaderUtil" in c or "ClassNotFound" in c or "NoSuchFieldError" in c)),
    ("LOGBACK_CLASSIC_CORE_SKEW", lambda c, d: "logback-classic" in c and "logback-core" in c),
    ("JAVA17_BYTECODE_ON_JAVA11", lambda c, d: "UnsupportedClassVersionError" in c or "Java 17 bytecode" in c),
    ("POI_MODULE_MIX", lambda c, d: d.startswith("poi")),
    ("ANTLR_ATN_FORMAT", lambda c, d: d == "antlr4-runtime"),
    ("JERSEY_JETTY_SKEW", lambda c, d: d in ("jersey-server", "jetty-server")),
    ("SUREFIRE_PROVIDER_TOOLING", lambda c, d: d in ("junit-platform-surefire-provider", "surefire-junit4", "surefire-junit47")),
    ("JUNIT_PLATFORM_SKEW", lambda c, d: d in ("junit-jupiter-params", "junit-jupiter-engine")),
    ("JAVAX_JAKARTA_NAMESPACE", lambda c, d: d in ("jakarta.xml.bind-api", "jaxb-impl", "hibernate-validator", "guice")),
    ("MOCKITO5_INLINE_DEFAULT", lambda c, d: d == "mockito-core"),
    ("DROPWIZARD_SENTRY_CONFIG", lambda c, d: d == "dropwizard-sentry" and "stacktraceAppPackages" in c or (d == "dropwizard-sentry" and "Same as Case 28" in c)),
    ("DROPWIZARD_SENTRY_DW4", lambda c, d: d == "dropwizard-sentry"),
    ("PLEXUS_UTILS_4_REMOVALS", lambda c, d: d == "plexus-utils"),
    ("H2_VARCHAR_LIMIT", lambda c, d: d == "h2"),
    ("JSON_SMART_DEPTH_LIMIT", lambda c, d: d == "json-smart"),
    ("SNAKEYAML_RAML_SKEW", lambda c, d: d == "snakeyaml"),
    ("GRAALJS", lambda c, d: d == "js-scriptengine"),
    ("SSHD_SKEW", lambda c, d: d.startswith("sshd")),
]


def family(cause, dep):
    for name, fn in FAMILIES:
        try:
            if fn(cause, dep):
                return name
        except Exception:
            pass
    return "SINGLETON"


norm = lambda s: "BEHAVIORAL" if s in ("PROVISIONAL_BEHAVIORAL", "BEHAVIORAL") else s
POST = {n: "UNCERTAIN" for n in (49, 67, 112, 127, 140, 188)}
DUP = {135: 123, 123: 135, 163: 168, 168: 163, 65: 169, 169: 65}
ROOT_NOTES = {
    71: "Partial disagreement on provenance, now corrected in Claude's view: Codex identifies retained flogger-system-backend 0.6 calling a StaticMethodCaller method absent from resolved flogger core 0.7.1. That is consistent with DefaultPlatform living in the system backend. Claude's blind wording had the skew reversed.",
    113: "Same mechanism class (inline mock maker). Codex names Tracer.getCurrentSpan/Span.addAnnotation as the intercepted final methods; Claude's blind guess (spanBuilder delegation) was less specific. Codex's account is preferred.",
    75: "Same root cause; Codex places the AbstractMethodError during server shutdown (lifeCycleFailure), Claude said start-up. Codex's account is more specific.",
    84: "Same root cause; Codex: shutdown-time AbstractMethodError.", 99: "Same root cause; Codex: shutdown-time AbstractMethodError.", 149: "Same root cause; Codex: shutdown-time AbstractMethodError.",
    69: "Codex: BEHAVIORAL (ScriptEngine 22.1.0 adds default option js.charset which retained GraalJS 22.0.0 rejects). Claude: NON_BEHAVIORAL because this is version skew between two GraalJS components, the same class as log4j api/core or logback classic/core skew, which both reviewers label NON_BEHAVIORAL. Maintained after comparison.",
    109: "Codex: BEHAVIORAL (Guice 7 no longer recognises javax.inject.Qualifier). Claude: NON_BEHAVIORAL as a javax->jakarta namespace migration. Codex labels the analogous hibernate-validator javax/jakarta cases (83, 93, 164, 180) NON_BEHAVIORAL, so Codex's own labels are inconsistent across namespace migrations. Maintained after comparison; adjudicate jointly with 83/93/164/180.",
}
for n in (49, 67, 112, 127, 140, 188):
    ROOT_NOTES[n] = ("Codex: BEHAVIORAL (the same deserialize(char[]) API now rejects serialized ATN v3 = accepted input changed). Claude blind: NON_BEHAVIORAL (generated-code/runtime format alignment, repaired by regenerating with a matching tool). "
                     "Both mechanisms agree; only the taxonomy differs. Post-comparison: UNCERTAIN pending human adjudication of the ANTLR family (6 cases, 3.2% of 188).")
COUNT_NOTES = {
    12: "Codex pre_tests=726 contradicted the original PRE log (757). Corrected in results/behavioral_classification.csv.",
    9: "Codex recorded module-scoped counts (core 510) unlike other rows; corrected to whole-build PRE 1114 / BREAKING 510.",
    10: "Codex recorded messaging-module counts (12/12); corrected to whole-build PRE 32 / BREAKING 18.",
    14: "Codex recorded persistence-module counts (32/32); corrected to whole-build PRE 190 / BREAKING 52.",
    17: "Codex row uses diagnostic counts/logs (fixed-date PRE control 4104; BREAKING scoped to one class, 11). Original PRE fails (1 date-sensitive failure) and original BREAKING was stopped (exit 143). Note added to the classification row.",
    2: "Agree. Class-level setup errors mask 197 PRE tests (291 -> 94).", 18: "Agree. 291 -> 94 from class-level errors.", 132: "Agree. 291 -> 94 from class-level errors.",
    75: "Agree on aggregate 16/10; raw XML double-counts to 22/16.", 84: "Agree on aggregate; raw XML double-counts.", 99: "Agree on aggregate; raw XML double-counts.", 149: "Agree on aggregate; raw XML double-counts.",
    105: "Agree with reconciled counts (raw XML 319 includes 10 TestNG duplicates; aggregate 309).", 138: "Agree with Maven aggregate 59; fresh archive double-counts (118).", 139: "Agree with Maven aggregate 59; fresh archive double-counts (118).",
    163: "Agree; raw XML 1235 vs aggregate 617 (TestNG duplicates).", 168: "Agree; raw XML 1235 vs aggregate 617 (TestNG duplicates).", 77: "Agree; PRE log prints the 453 summary twice (counted once).",
}
PROV_NOTES = {
    33: "Archive coverage gap: artifacts.tar has 0 changed files, but the separately archived avans-module-pom.xml shows jackson-core 2.4.2 -> 2.13.3. Codex's account uses the resolved jars, consistent.",
    4: "Same update fails in a different module across images (paris/broker/clearinghouse/core/messaging for Cases 4/23/60/121/177).", 23: "Failing module varies across images (see Case 4).",
    60: "Failing module varies across images (see Case 4).", 121: "Failing module varies across images (see Case 4).", 177: "Failing module varies across images (see Case 4).",
    14: "Verified repair log shows full-reactor BUILD SUCCESS (190 tests, 36 skipped), more than the recorded 32/32. The log does not print the resolved H2 jar, so 'H2 2.0.206 retained' is not evidenced by the log alone.",
    161: "Agree with Codex: fixture-only edit; test classpaths identical (Codex reports 34 matching classpaths and identical kotlin-stdlib 1.4.10 hash).",
}

cols = ["case_number", "case_id", "project", "dependency", "old_version", "new_version",
        "claude_label_blind", "claude_label_post_comparison", "confidence", "primary_cause", "behavior_change", "binary_linkage",
        "baseline_outcome", "updated_outcome", "count_notes", "evidence_paths",
        "codex_label", "codex_binary_linkage", "label_agreement", "linkage_agreement",
        "root_cause_comparison", "count_comparison", "provenance_comparison",
        "related_group", "possible_duplicate_of", "resolve_uncertainty", "label_exposure_before_blind",
        "corrections_applied_to_original", "review_source", "human_reviewer_label", "final_label"]
out = []
for n in range(1, 189):
    c = cands[n - 1]; r = cx[c["case_id"]]; b = blind[n]; k = counts[n]
    pre_s, brk_s = status(r["pre_log"]), status(r["breaking_log"])
    lp, lb = k["log_pre"], k["log_brk"]; rp, rb = k["log_pre_rnd"], k["log_brk_rnd"]
    def fmt(st, l, rr):
        s = f"BUILD {st}; surefire tests={l[0]} failures={l[1]} errors={l[2]} skipped={l[3]}"
        if rr[0]:
            s += f"; randomized-runner tests={rr[0]} failures={rr[1]} errors={rr[2]} ignored={rr[3]}"
        return s
    ev = [r["pre_log"], r["breaking_log"]]
    if os.path.isdir(P("logs", f"case{n}_evidence")): ev.append(f"logs/case{n}_evidence/")
    if os.path.exists(P("results", f"case{n}_review.md")): ev.append(f"results/case{n}_review.md")
    ev.append(f"audit_claude_review/digests/case{n:03d}.txt")
    cl = norm(r["behavioral_status"])
    agree = "AGREE" if cl == b["label"] else "DISAGREE"
    fam = family(b["primary_cause"], c["dependency_artifact"])
    out.append({
        "case_number": n, "case_id": c["case_id"], "project": f"{c['organisation']}/{c['project']}",
        "dependency": f"{c['dependency_group']}:{c['dependency_artifact']}", "old_version": c["previous_version"], "new_version": c["new_version"],
        "claude_label_blind": b["label"], "claude_label_post_comparison": POST.get(n, b["label"]), "confidence": b["confidence"],
        "primary_cause": b["primary_cause"] + (" [post-comparison provenance note: see root_cause_comparison]" if n == 71 else ""),
        "behavior_change": b["behavior_change"], "binary_linkage": b["binary_linkage"],
        "baseline_outcome": fmt(pre_s, lp, rp), "updated_outcome": fmt(brk_s, lb, rb), "count_notes": b["count_notes"],
        "evidence_paths": "; ".join(ev),
        "codex_label": r["behavioral_status"], "codex_binary_linkage": r["binary_linkage_incompatibility"],
        "label_agreement": agree, "linkage_agreement": "AGREE" if r["binary_linkage_incompatibility"] == b["binary_linkage"] else "DISAGREE",
        "root_cause_comparison": ROOT_NOTES.get(n, "Agree: Codex's description names the same initiating mechanism."),
        "count_comparison": COUNT_NOTES.get(n, "Agree: recorded counts match the Maven summaries in the original logs."),
        "provenance_comparison": PROV_NOTES.get(n, "No disagreement found on dependency provenance."),
        "related_group": f"{fam} | {c['organisation']}/{c['project']}:{c['dependency_artifact']}",
        "possible_duplicate_of": DUP.get(n, ""),
        "resolve_uncertainty": b["resolve_uncertainty"],
        "label_exposure_before_blind": "YES - Codex label seen in completion check before review" if n in (161, 162) else "NO (aggregate counts only)",
        "corrections_applied_to_original": "; ".join(f"{x['field']}" + (f" {x['old']}->{x['new']}" if 'old' in x and x['field'] != 'notes(text)' else '') for x in corr[n]["changes"]) if n in corr else "",
        "review_source": "AI second review (Claude, claude-opus-5-5), 2026-11-20; not a human review",
        "human_reviewer_label": "", "final_label": "",
    })
with open(A("claude_audit.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(out)
import collections
print(len(out), collections.Counter(o["claude_label_blind"] for o in out), collections.Counter(o["claude_label_post_comparison"] for o in out))
print(collections.Counter(o["label_agreement"] for o in out), collections.Counter(o["linkage_agreement"] for o in out))
print(collections.Counter(o["related_group"].split(" | ")[0] for o in out).most_common())
json.dump({o["case_number"]: o["related_group"] for o in out}, open(A("_groups.json"), "w"), indent=0)
