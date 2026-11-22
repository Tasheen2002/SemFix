"""Build the developer-fix catalogue for the 56 BEHAVIORAL cases.

Inputs: fix_mining/cases.json, version_trace.json, pr_meta.json (may be partial), failing_tests.json,
        results/final_classification_rule_based.csv.
Outputs: fix_mining/developer_fixes.csv, fix_mining/patches/<case>_<sha10>.patch (developer fix vs first parent),
         fix_mining/fix_summary.json.
Fix status / type values are assigned per project family from the inspected commits (see FAMILY below);
every assignment cites the commit it rests on. Read-only on the repositories.
Usage: python -I build_fix_catalog.py <research root>
"""
import csv, json, os, subprocess, sys
from collections import Counter

ROOT = sys.argv[1]
F = lambda *a: os.path.join(ROOT, "fix_mining", *a)
cases = {c["case"]: c for c in json.load(open(F("cases.json"), encoding="utf-8"))}
trace = {r["case"]: r for r in json.load(open(F("version_trace.json"), encoding="utf-8"))}
prm = json.load(open(F("pr_meta.json"), encoding="utf-8")) if os.path.exists(F("pr_meta.json")) else {}
ft = json.load(open(F("failing_tests.json"), encoding="utf-8"))
fin = {r["case_number"]: r for r in csv.DictReader(open(os.path.join(ROOT, "results", "final_classification_rule_based.csv"), encoding="utf-8"))}

# status, type, evidence-match, validation need, note
FAMILY = {
    "damianszczepanik/cucumber-reporting": ("FIXED", "CLIENT_CODE_ADAPTATION", "YES",
        "Developer widened the catch to IOException | IllegalArgumentException in ReportBuilder, the class under the failing test."),
    "apache/logging-chainsaw": ("FIXED", "TEST_ADAPTATION_API_CONFIG", "YES",
        "Developer added XStream.allowTypes(LogPanelPreferenceModel.class) in the failing test: adapts to the new deny-by-default security policy."),
    "lookfirst/sardine": ("FIXED", "TEST_EXPECTATION_UPDATE", "YES",
        "Developer updated the expected exception message in SardineExceptionTest to the new httpclient format (landed with 4.5.14)."),
    "SPARQL-Anything/sparql.anything": ("FIXED", "TEST_EXPECTATION_UPDATE", "YES",
        "Developer regenerated expected output Microdata1.nq for jsoup's new whitespace handling (commit message says so)."),
    "alphagov/pay-cardid": ("FIXED", "CONFIGURATION_ADAPTATION", "YES",
        "Developer renamed the rejected Sentry appender property stacktraceAppPackages -> inAppIncludes in config.yaml (PR #732, landed with 2.0.28-8)."),
    "feedzai/pdb": ("FIXED", "COMPANION_DEPENDENCY_UPGRADE", "YES",
        "slf4j 2.0.17 landed together with logback-classic 1.2.13 -> 1.3.16 (an SLF4J-2 provider), POM only. Fixes the R5 provider-selection change."),
    "jadler-mocking/jadler": ("FIXED", "COMPANION_DEPENDENCY_UPGRADE", "YES",
        "slf4j 2.0.3 landed together with logback-classic 1.2.11 -> 1.3.4 (an SLF4J-2 provider), POM only. Fixes the R5 provider-selection change."),
    "alphagov/pay-adminusers": ("FIXED", "FRAMEWORK_MIGRATION", "LIKELY",
        "Dropwizard 2 -> 3 upgrade (#2049): explicit slf4j-api 1.7.36 pin removed, versions now from the Dropwizard 3 BOM (SLF4J 2 + logback 1.4). Large diff; not a minimal fix. "
        "Validated reference is a DERIVED minimal fix (logback-classic/core 1.3.5 under Dropwizard 2.0.29), not the developer's commit."),
    "pac4j/dropwizard-pac4j": ("FIXED", "FRAMEWORK_MIGRATION", "LIKELY",
        "Dropwizard 2 -> 4 and pac4j upgrade (#397). Validated by REPLAYING the developer commit onto the breaking commit: all Java changes applied "
        "cleanly (Java files identical between breaking commit and fix parent); 3 pom.xml conflicts resolved with the developer's side; slf4j-api kept "
        "at the case's 2.0.0 and jax-rs-pac4j 6.0.0-SNAPSHOT replaced by released 6.0.0. A minimal logback-only fix fails (logback 1.3 removed "
        "JMXConfigurator used by Dropwizard 2.0), so the framework migration is necessary."),
    "codehaus-plexus/plexus-archiver": ("UPSTREAM_RESOLVED", "VERSION_SKIP", "YES",
        "3.3.0 never landed; 3.3.1 landed POM-only. Validated: plexus-io 3.3.1 alone makes all tests pass, so the library undid the symlink isDirectory change."),
    "btrplace/scheduler": ("UPSTREAM_RESOLVED", "VERSION_SKIP", "YES",
        "2.4.9 never landed; 2.4.10 landed POM-only. Validated: json-smart 2.4.10 alone makes the json module pass, so the library relaxed the nesting-depth rejection."),
    "geosolutions-it/geostore": ("UPSTREAM_RESOLVED", "VERSION_SKIP", "YES",
        "h2 2.2.220 landed in a 22-dependency security sweep. Validated: h2 2.2.220 alone (no other sweep change) makes all tests pass, so later h2 accepts varchar(10000000) again; the schema never changed."),
    "s4u/sign-maven-plugin": ("NOT_ADOPTED", "NONE", "N/A",
        "Project stayed active (commits to 2026-09) and kept other updates, but slf4j-api is still 1.7.36 at HEAD."),
    "pholser/junit-quickcheck": ("NOT_ADOPTED", "NONE", "N/A",
        "Project stayed active (to 2024-08) and kept other updates, but mockito-core is still 4.11.0 at HEAD."),
    "retest/recheck": ("NOT_ADOPTED_PROJECT_INACTIVE", "NONE", "N/A",
        "Default branch has no commits after 2022-06-02; slf4j-api still 1.7.36."),
    "searls/jasmine-maven-plugin": ("NOT_ADOPTED_PROJECT_INACTIVE", "NONE", "N/A",
        "Default branch has no commits after 2022-10-04; slf4j-api still 1.7.32."),
    "jericks/geoserver-shell": ("NOT_ADOPTED_PROJECT_INACTIVE", "NONE", "N/A",
        "Default branch has no commits after 2021-09-10; org.json still 20090211."),
    "googleapis/gax-java": ("REPOSITORY_MIGRATED", "NONE", "N/A",
        "Repository retired 2023-07 ('removing outdated files in favor of googleapis/google-cloud-java'); mockito 5 adoption would be in the successor repository, not mined."),
}
FIX_KIND = {"FIXED", "UPSTREAM_RESOLVED"}
VAL = {}
if os.path.exists(F("validation", "results.jsonl")):
    VAL = {json.loads(l)["case"]: json.loads(l) for l in open(F("validation", "results.jsonl"), encoding="utf-8") if l.strip()}
# Researcher-written fixes (separate group: they show a case is fixable; they are NOT reference answers).
RW = {}
if os.path.exists(F("researcher_written", "results.jsonl")):
    RW = {json.loads(l)["case"]: json.loads(l) for l in open(F("researcher_written", "results.jsonl"), encoding="utf-8") if l.strip()}


def reference_group(n, status):
    v = VAL.get(n, {}).get("verdict")
    if v == "FIX_VALIDATED":
        return "DERIVED_MINIMAL_FIX" if "DERIVED" in VAL[n]["recipe_source"] else "DEVELOPER_FIX"
    if RW.get(n, {}).get("verdict") == "FIX_VALIDATED":
        return "RESEARCHER_WRITTEN_ONLY"
    return "NO_VALIDATED_FIX"

os.makedirs(F("patches"), exist_ok=True)
rows = []
for n in sorted(cases):
    c, t = cases[n], trace[n]
    status, ftype, match, note = FAMILY[c["slug"]]
    L = t["landing"] or {}
    if not L and status == "FIXED":
        # Version moved under a BOM: the fix commit is the one where the explicit pin became MANAGED.
        m = [v for v in t["version_changes"] if v["version"] == "MANAGED"]
        if m:
            repo = F("repos", c["repo"])
            files = subprocess.run(["git", "-C", repo, "diff", "--name-only", m[0]["commit"] + "^1", m[0]["commit"]],
                                   capture_output=True, text=True).stdout.split()
            L = dict(m[0], version="MANAGED (BOM)", files=files,
                     file_kinds=sorted({("pom" if f.endswith("pom.xml") else "test" if "/src/test/" in "/" + f else
                                         "main" if "/src/main/" in "/" + f else "other") for f in files}),
                     other_dependency_changes_in_pom={})
    patch = ""
    if status in FIX_KIND and L:
        repo = F("repos", c["repo"])
        parent = subprocess.run(["git", "-C", repo, "rev-parse", L["commit"] + "^1"], capture_output=True, text=True).stdout.strip()
        diff = subprocess.run(["git", "-C", repo, "diff", "--binary", parent, L["commit"]], capture_output=True).stdout
        patch = f"patches/{c['repo']}_{L['commit'][:10]}.patch"
        open(F(patch), "wb").write(diff)
    p = prm.get(str(n), {})
    rows.append(dict(
        case_number=n, case_id=c["id"], project=c["slug"], dependency=f"{c['group']}:{c['artifact']}",
        old_version=c["old"], new_version=c["new"], rule=fin[str(n)]["rule"],
        behavior_change_category=fin[str(n)]["behavior_change_category"], related_group=c["related_group"],
        pr_url=c["url"], pr_state=("merged" if p.get("merged") else p.get("state", "")) if p else "NOT_FETCHED",
        pr_closed_at=p.get("closed_at") or "", default_branch=t["default_branch"].replace("origin/", ""),
        fix_status=status, fix_type=ftype, fix_matches_classified_behavior=match,
        fix_commit=L.get("commit", ""), fix_date=L.get("date", "")[:10], fix_version=L.get("version", ""),
        fix_files=";".join(L.get("files", [])) if len(L.get("files", [])) <= 12 else f"{len(L['files'])} files",
        fix_file_kinds=";".join(L.get("file_kinds", [])),
        companion_changes=";".join(f"{k} {a}->{b}" for k, (a, b) in list(L.get("other_dependency_changes_in_pom", {}).items())[:6])
            + (f" (+{len(L['other_dependency_changes_in_pom']) - 6} more)" if len(L.get("other_dependency_changes_in_pom", {})) > 6 else ""),
        patch_file=patch, head_version=t["head_version"], head_date=t["head_date"][:10],
        failing_test_classes=";".join(ft[str(n)]["classes"]),
        validation_status=(("DERIVED_" if "DERIVED" in VAL[n]["recipe_source"] else "") + VAL[n]["verdict"]) if n in VAL else ("NOT_VALIDATED" if status in FIX_KIND else "N/A (no developer fix)"),
        validation_detail=(f"BREAKING {VAL[n]['original']['tests']}/{VAL[n]['original']['failures']}/{VAL[n]['original']['errors']} -> fixed "
                           f"{VAL[n]['fixed']['tests']}/{VAL[n]['fixed']['failures']}/{VAL[n]['fixed']['errors']} (t/f/e), BUILD {VAL[n]['fixed']['build']}, "
                           f"MAVEN_EXIT={VAL[n]['maven_exit']}; backport {VAL[n]['patch']}") if n in VAL else "",
        researcher_fix_status=RW[n]["verdict"] if n in RW else "",
        researcher_fix_patch=RW[n]["patch"] if n in RW else "",
        researcher_fix_detail=(f"{RW[n]['recipe_source']} | BREAKING {RW[n]['original']['tests']}/{RW[n]['original']['failures']}/{RW[n]['original']['errors']} -> "
                               f"{RW[n]['fixed']['tests']}/{RW[n]['fixed']['failures']}/{RW[n]['fixed']['errors']} (t/f/e), MAVEN_EXIT={RW[n]['maven_exit']}"
                               + (f" | {RW[n]['verdict_note']}" if RW[n].get("verdict_note") else "")) if n in RW else "",
        reference_group=reference_group(n, status),
        evaluation_mode=("compare to reference fix + tests" if reference_group(n, status) in ("DEVELOPER_FIX", "DERIVED_MINIMAL_FIX")
                         else "tests only (failing tests pass, nothing else breaks)"),
        notes=note))

cols = list(rows[0])
with open(F("developer_fixes.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)
uniq = {r["fix_commit"] for r in rows if r["fix_commit"] and r["fix_status"] in FIX_KIND}
summ = dict(reference_group=Counter(r["reference_group"] for r in rows),
            researcher_written=Counter(r["researcher_fix_status"] for r in rows if r["researcher_fix_status"]),
            validation=Counter(r["validation_status"] for r in rows), cases=len(rows), by_status=Counter(r["fix_status"] for r in rows), by_type=Counter(r["fix_type"] for r in rows),
            unique_fix_commits=len(uniq), pr_state=Counter(r["pr_state"] for r in rows))
json.dump(summ, open(F("fix_summary.json"), "w", encoding="utf-8"), indent=1)
print(json.dumps(summ, indent=1))
