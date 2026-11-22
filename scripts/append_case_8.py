import csv
from pathlib import Path

CSV_PATH = Path("results/behavioral_classification.csv")

CASE_ID = "0c748afce24c983e8f330bc2435837c70b0fcde6"

new_row = {
    "case_id": CASE_ID,
    "project": "dropwizard-pac4j",
    "dependency_group": "com.fasterxml.jackson.core",
    "dependency_artifact": "jackson-databind",
    "old_version": "2.10.5.1",
    "new_version": "2.14.1",
    "bump_category": "TEST_FAILURE",
    "pre_build_status": "SUCCESS",
    "breaking_build_status": "FAILURE",
    "pre_tests": "16",
    "breaking_tests": "16",
    "breaking_failures": "0",
    "breaking_errors": "16",
    "test_effect_type": "TEST_ERROR",
    "test_effect_subtype": "JAVA_ERROR",
    "main_exception": "java.lang.NoClassDefFoundError",
    "failure_origin": "UPDATED_LIBRARY",
    "origin_library": "com.fasterxml.jackson.core:jackson-databind:2.14.1",
    "binary_linkage_incompatibility": "YES",
    "behavioral_status": "NON_BEHAVIORAL",
    "behavior_change_type": "",
    "behavior_description": (
        "Updating jackson-databind from 2.10.5.1 to 2.14.1 creates an "
        "incompatible Jackson dependency combination. The project continues "
        "to resolve jackson-core and jackson-annotations 2.10.5 while "
        "jackson-databind becomes 2.14.1. jackson-databind 2.14.1 requires "
        "com.fasterxml.jackson.core.util.JacksonFeature, but that class is "
        "not present in jackson-core 2.10.5. Test execution therefore stops "
        "with NoClassDefFoundError before meaningful application behavior "
        "can be compared."
    ),
    "pre_log": "logs/0c748afc_pre.log",
    "breaking_log": "logs/0c748afc_breaking.log",
    "review_status": "PENDING_SECOND_REVIEW",
    "reviewer_1_label": "NON_BEHAVIORAL",
    "reviewer_2_label": "",
    "final_label": "",
    "notes": (
        "PRE: 16 tests, 0 failures, 0 errors, BUILD SUCCESS. PRE dependency "
        "tree resolves jackson-core 2.10.5, jackson-annotations 2.10.5, and "
        "jackson-databind 2.10.5.1. BREAKING: 16 tests, 0 failures, 16 errors, "
        "BUILD FAILURE. BREAKING dependency tree resolves jackson-core 2.10.5, "
        "jackson-annotations 2.10.5, and jackson-databind 2.14.1. The first "
        "meaningful error is java.lang.NoClassDefFoundError for "
        "com/fasterxml/jackson/core/util/JacksonFeature, originating from "
        "jackson-databind DatatypeFeatures.defaultFeatures. Direct JAR "
        "inspection confirms JacksonFeature.class is absent from jackson-core "
        "2.10.5 and present in jackson-core 2.14.1. Evaluation of the "
        "jackson-databind 2.14.1 POM confirms jackson.version.core=2.14.1. "
        "Classified as NON_BEHAVIORAL binary/runtime dependency incompatibility."
    ),
}

with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

if CASE_ID in {row["case_id"] for row in rows}:
    print(f"Case {CASE_ID} already exists. Nothing added.")
else:
    with CSV_PATH.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(new_row)

    print(f"Added Case 8: {CASE_ID}")