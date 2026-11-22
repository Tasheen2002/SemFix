import csv
from pathlib import Path

CSV_PATH = Path("results/behavioral_classification.csv")

CASE_ID = "0c088ff435224b168f93d2a20b829af940bb67dd"

new_row = {
    "case_id": CASE_ID,
    "project": "a",
    "dependency_group": "org.graalvm.js",
    "dependency_artifact": "js-scriptengine",
    "old_version": "22.3.2",
    "new_version": "23.0.1",
    "bump_category": "TEST_FAILURE",
    "pre_build_status": "SUCCESS",
    "breaking_build_status": "FAILURE",
    "pre_tests": "80",
    "breaking_tests": "80",
    "breaking_failures": "0",
    "breaking_errors": "79",
    "test_effect_type": "TEST_ERROR",
    "test_effect_subtype": "JAVA_ERROR",
    "main_exception": "java.lang.UnsupportedClassVersionError",
    "failure_origin": "UPDATED_LIBRARY",
    "origin_library": "org.graalvm.js:js-scriptengine:23.0.1",
    "binary_linkage_incompatibility": "YES",
    "behavioral_status": "NON_BEHAVIORAL",
    "behavior_change_type": "",
    "behavior_description": (
        "Updating org.graalvm.js:js-scriptengine from 22.3.2 to 23.0.1 "
        "changes GraalJSEngineFactory from Java 11-compatible bytecode "
        "(class file major version 55) to Java 17 bytecode "
        "(class file major version 61). The project still runs on Java 11, "
        "which supports class file versions only up to 55. When the updated "
        "class is loaded during test setup, the JVM throws "
        "UnsupportedClassVersionError. This is a runtime platform/class-version "
        "compatibility failure rather than a semantic behavioral change."
    ),
    "pre_log": "logs/0c088ff4_pre.log",
    "breaking_log": "logs/0c088ff4_breaking.log",
    "review_status": "PENDING_SECOND_REVIEW",
    "reviewer_1_label": "NON_BEHAVIORAL",
    "reviewer_2_label": "",
    "final_label": "",
    "notes": (
        "PRE: js-scriptengine 22.3.2; javap shows GraalJSEngineFactory major "
        "version 55, compatible with Java 11. PRE runs 80 tests with 0 failures, "
        "0 errors, 1 skipped and BUILD SUCCESS. BREAKING: js-scriptengine 23.0.1; "
        "javap shows GraalJSEngineFactory major version 61, which corresponds to "
        "Java 17 bytecode. The breaking Docker image runs OpenJDK 11.0.19, which "
        "supports class file versions only up to 55. The breaking log reports "
        "java.lang.UnsupportedClassVersionError for GraalJSEngineFactory and "
        "finishes with 80 tests, 0 failures, 79 errors, 1 skipped, BUILD FAILURE. "
        "Classified as NON_BEHAVIORAL runtime/platform compatibility failure."
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

    print(f"Added Case 7: {CASE_ID}")