from pathlib import Path
import csv

BASE_DIR = Path(r"C:\Users\TASHEEN\Desktop\Research Implementation")
OUTPUT_CSV = BASE_DIR / "results" / "behavioral_classification.csv"

fieldnames = [
    "case_id",
    "project",
    "dependency_group",
    "dependency_artifact",
    "old_version",
    "new_version",
    "bump_category",

    "pre_build_status",
    "breaking_build_status",
    "pre_tests",
    "breaking_tests",
    "breaking_failures",
    "breaking_errors",

    "test_effect_type",
    "test_effect_subtype",
    "main_exception",

    "failure_origin",
    "origin_library",

    "binary_linkage_incompatibility",

    "behavioral_status",
    "behavior_change_type",
    "behavior_description",

    "pre_log",
    "breaking_log",

    "review_status",
    "reviewer_1_label",
    "reviewer_2_label",
    "final_label",

    "notes",
]

case_1 = {
    "case_id": "02363207c365b3befd6426f6dda5c8eac904d760",
    "project": "recheck",
    "dependency_group": "org.slf4j",
    "dependency_artifact": "slf4j-api",
    "old_version": "1.7.36",
    "new_version": "2.0.3",
    "bump_category": "TEST_FAILURE",

    "pre_build_status": "SUCCESS",
    "breaking_build_status": "FAILURE",
    "pre_tests": "737",
    "breaking_tests": "737",
    "breaking_failures": "0",
    "breaking_errors": "30",

    "test_effect_type": "TEST_ERROR",
    "test_effect_subtype": "RUNTIME_EXCEPTION",
    "main_exception": "java.lang.ClassCastException",

    "failure_origin": "LIBRARY_USED_FOR_TESTING",
    "origin_library": "io.github.netmikey.logunit:logunit-logback:1.1.3",

    "binary_linkage_incompatibility": "NO",

    "behavioral_status": "PROVISIONAL_BEHAVIORAL",
    "behavior_change_type": "OTHER_BEHAVIORAL_CHANGE",
    "behavior_description": (
        "After slf4j-api changed from 1.7.36 to 2.0.3, "
        "SLF4J ignored the old Logback 1.2.11 StaticLoggerBinder, "
        "found no compatible provider, and returned NOPLogger. "
        "LogUnit 1.1.3 expected a Logback Logger and cast the returned "
        "logger to ch.qos.logback.classic.Logger, causing ClassCastException."
    ),

    "pre_log": "logs/02363207_pre.log",
    "breaking_log": "logs/02363207_breaking.log",

    "review_status": "PENDING_SECOND_REVIEW",
    "reviewer_1_label": "BEHAVIORAL",
    "reviewer_2_label": "",
    "final_label": "",

    "notes": (
        "PRE passed 737 tests with 0 failures and 0 errors. "
        "BREAKING produced 30 test errors. "
        "Dependency-tree comparison showed only slf4j-api changed; "
        "Logback 1.2.11 and LogUnit 1.1.3 remained unchanged."
    ),
}

OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow(case_1)

print(f"Created: {OUTPUT_CSV}")
print("Case 1 saved successfully.")