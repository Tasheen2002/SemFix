from pathlib import Path
import csv

BASE_DIR = Path(r"C:\Users\TASHEEN\Desktop\Research Implementation")
OUTPUT_CSV = BASE_DIR / "results" / "behavioral_classification.csv"

case_4 = {
    "case_id": "0671a30e3673989830ed7f4aa345b867c29547f0",
    "project": "IDS-Messaging-Services",
    "dependency_group": "org.junit.platform",
    "dependency_artifact": "junit-platform-surefire-provider",
    "old_version": "1.0.3",
    "new_version": "1.3.2",
    "bump_category": "TEST_FAILURE",

    "pre_build_status": "SUCCESS",
    "breaking_build_status": "FAILURE",

    "pre_tests": "32",
    "breaking_tests": "26",
    "breaking_failures": "0",
    "breaking_errors": "0",

    "test_effect_type": "TEST_ERROR",
    "test_effect_subtype": "ERROR",
    "main_exception": "java.lang.NoSuchMethodError",

    "failure_origin": "LIBRARY_USED_FOR_TESTING",
    "origin_library": "org.junit.platform:junit-platform-surefire-provider:1.3.2",

    "binary_linkage_incompatibility": "YES",
    "behavioral_status": "NON_BEHAVIORAL",
    "behavior_change_type": "",

    "behavior_description": (
        "After junit-platform-surefire-provider changed from 1.0.3 to 1.3.2, "
        "the paris module failed before executing its tests. "
        "The updated provider 1.3.2 brings Surefire runtime components "
        "surefire-api 2.22.0 and common-java5 2.22.0, while the project still "
        "uses maven-surefire-plugin 2.19.1. During test execution Maven reported "
        "java.lang.NoSuchMethodError for "
        "org.apache.maven.surefire.util.internal.StringUtils.requireNonNull(Object). "
        "This is a runtime binary/linkage incompatibility in the testing "
        "infrastructure rather than a behavioral change in the client program."
    ),

    "pre_log": "logs/0671a30e_pre.log",
    "breaking_log": "logs/0671a30e_breaking.log",

    "review_status": "PENDING_SECOND_REVIEW",
    "reviewer_1_label": "NON_BEHAVIORAL",
    "reviewer_2_label": "",
    "final_label": "",

    "notes": (
        "PRE completed 32 tests with 0 failures and 0 errors and BUILD SUCCESS. "
        "BREAKING completed 26 tests successfully in earlier modules, then the "
        "paris module started 0 tests and Maven ended with BUILD FAILURE. "
        "PRE paris configuration used maven-surefire-plugin 2.19.1 with "
        "junit-platform-surefire-provider 1.0.3. Provider 1.0.3 depends on "
        "surefire-api 2.19.1 and common-java5 2.19.1. "
        "BREAKING kept maven-surefire-plugin 2.19.1 but changed the provider "
        "to 1.3.2, which depends on surefire-api 2.22.0 and common-java5 2.22.0. "
        "The breaking plugin realm therefore contains mixed Surefire versions. "
        "common-java5 2.22.0 contains "
        "org.apache.maven.surefire.util.internal.StringUtils but its version "
        "does not contain requireNonNull(Object). Maven reports "
        "NoSuchMethodError for that method. "
        "Classified as runtime binary/linkage incompatibility and NON_BEHAVIORAL."
    ),
}


# Read the existing CSV structure and check for duplicates
with OUTPUT_CSV.open("r", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    fieldnames = reader.fieldnames
    existing_ids = {row["case_id"] for row in reader}


# Append only if Case 4 is not already present
if case_4["case_id"] in existing_ids:
    print("Case 4 already exists. Nothing added.")
else:
    with OUTPUT_CSV.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(case_4)

    print("Case 4 appended successfully.")