import csv
from pathlib import Path

CSV_PATH = Path("results/behavioral_classification.csv")

CASE_ID = "125f1253d8331f14752a4a8d49559445301ab02d"

new_row = {
    "case_id": CASE_ID,
    "project": "jspc-maven-plugin",
    "dependency_group": "org.codehaus.plexus",
    "dependency_artifact": "plexus-utils",
    "old_version": "3.5.1",
    "new_version": "4.0.0",
    "bump_category": "TEST_FAILURE",
    "pre_build_status": "SUCCESS",
    "breaking_build_status": "FAILURE",
    "pre_tests": "22",
    "breaking_tests": "22",
    "breaking_failures": "0",
    "breaking_errors": "16",
    "test_effect_type": "TEST_ERROR",
    "test_effect_subtype": "JAVA_ERROR",
    "main_exception": "java.lang.NoClassDefFoundError",
    "failure_origin": "UPDATED_LIBRARY",
    "origin_library": "org.codehaus.plexus:plexus-utils:4.0.0",
    "binary_linkage_incompatibility": "YES",
    "behavioral_status": "NON_BEHAVIORAL",
    "behavior_change_type": "",
    "behavior_description": "",
    "pre_log": "logs/test_failure_evidence/125f1253_pre.log",
    "breaking_log": "logs/test_failure_evidence/125f1253_breaking.log",
    "review_status": "PENDING_SECOND_REVIEW",
    "reviewer_1_label": "NON_BEHAVIORAL",
    "reviewer_2_label": "",
    "final_label": "",
    "notes": (
        "PRE build with plexus-utils 3.5.1 runs 22 tests with 0 failures "
        "and 0 errors and ends with BUILD SUCCESS. BREAKING build with "
        "plexus-utils 4.0.0 runs the same 22 tests with 0 failures and "
        "16 errors and ends with BUILD FAILURE. The affected tests fail "
        "with java.lang.NoClassDefFoundError for "
        "org/codehaus/plexus/util/xml/XmlStreamReader, caused by "
        "ClassNotFoundException. Direct JAR inspection confirmed that "
        "XmlStreamReader.class exists in plexus-utils 3.5.1 but is absent "
        "from plexus-utils 4.0.0. Therefore the dependency update removes "
        "a class required at runtime. This is classified as NON_BEHAVIORAL "
        "because the breakage is a binary/runtime compatibility failure "
        "rather than a semantic behavior change."
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

    print(f"Added Case 11: {CASE_ID}")