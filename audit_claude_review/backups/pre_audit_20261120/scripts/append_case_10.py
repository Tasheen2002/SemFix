import csv
from pathlib import Path

CSV_PATH = Path("results/behavioral_classification.csv")

CASE_ID = "11fa4228dbff2f7e96f71120afac3528cafa85b4"

new_row = {
    "case_id": CASE_ID,
    "project": "IDS-Messaging-Services",
    "dependency_group": "com.fasterxml.jackson.core",
    "dependency_artifact": "jackson-databind",
    "old_version": "2.9.10.8",
    "new_version": "2.13.1",
    "bump_category": "TEST_FAILURE",
    "pre_build_status": "SUCCESS",
    "breaking_build_status": "FAILURE",
    "pre_tests": "12",
    "breaking_tests": "12",
    "breaking_failures": "1",
    "breaking_errors": "5",
    "test_effect_type": "TEST_ERROR",
    "test_effect_subtype": "JAVA_ERROR",
    "main_exception": "java.lang.NoClassDefFoundError",
    "failure_origin": "UPDATED_LIBRARY",
    "origin_library": "com.fasterxml.jackson.core:jackson-databind:2.13.1",
    "binary_linkage_incompatibility": "YES",
    "behavioral_status": "NON_BEHAVIORAL",
    "behavior_change_type": "",
    "behavior_description": "",
    "pre_log": "logs/11fa4228_pre.log",
    "breaking_log": "logs/11fa4228_breaking.log",
    "review_status": "PENDING_SECOND_REVIEW",
    "reviewer_1_label": "NON_BEHAVIORAL",
    "reviewer_2_label": "",
    "final_label": "",
    "notes": (
        "PRE build succeeds. In the PRE messaging module, jackson-databind "
        "2.9.10.8 and jackson-core 2.9.10 coexist with jackson-annotations "
        "2.11.2 without failure. After updating jackson-databind to 2.13.1, "
        "the messaging module resolves jackson-databind 2.13.1 and "
        "jackson-core 2.13.1 while jackson-annotations remains at 2.11.2. "
        "The breaking build executes 12 tests with 1 failure and 5 errors. "
        "All affected tests are caused by java.lang.NoClassDefFoundError for "
        "com/fasterxml/jackson/annotation/JsonKey. Direct JAR inspection "
        "confirmed JsonKey.class is absent from jackson-annotations 2.11.2 "
        "and present in jackson-annotations 2.13.1. The apparent assertion "
        "failure also wraps the same NoClassDefFoundError. Therefore this is "
        "classified as NON_BEHAVIORAL because the failure is caused by a "
        "mixed-version Jackson runtime/binary dependency incompatibility, "
        "not an observable semantic behavior change."
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

    print(f"Added Case 10: {CASE_ID}")