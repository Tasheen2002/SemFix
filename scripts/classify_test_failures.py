import re
from pathlib import Path

import pandas as pd


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = Path(
    r"C:\Users\TASHEEN\Desktop\Research Implementation"
)

INPUT_CSV = BASE_DIR / "results" / "test_failure_candidates.csv"

OUTPUT_CSV = BASE_DIR / "results" / "preliminary_classification.csv"

LOG_DIR = BASE_DIR / "logs"

# For verification, process only the first 3 cases.
# Later we will remove this limit.
MAX_CASES = 3


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def read_log(path: Path) -> str:
    if not path.exists():
        return ""

    return path.read_text(
        encoding="utf-8",
        errors="ignore"
    )


def get_build_status(text: str) -> str:

    if "BUILD SUCCESS" in text:
        return "BUILD_SUCCESS"

    if "BUILD FAILURE" in text:
        return "BUILD_FAILURE"

    return "UNKNOWN"


def extract_failing_tests(text: str):

    failing_tests = []

    for line in text.splitlines():

        if "<<< FAILURE!" not in line and "<<< ERROR!" not in line:
            continue

        clean = line.strip()

        # Remove Maven prefix
        clean = re.sub(
            r"^\[ERROR\]\s*",
            "",
            clean
        )

        # Remove everything after timing/failure marker
        clean = clean.split(" Time elapsed:")[0]
        clean = clean.split(" <<<")[0]

        # Ignore aggregate Maven summary lines
        if clean.startswith("Tests run:"):
            continue

        if clean and clean not in failing_tests:
            failing_tests.append(clean)

    return failing_tests


def extract_exceptions(text: str):

    exceptions = []

    pattern = re.compile(
        r"((?:java|javax|jakarta|org|com)\."
        r"[\w.$]+"
        r"(?:Exception|Error))"
    )

    for line in text.splitlines():

        match = pattern.search(line)

        if match:

            exception = match.group(1)

            if exception not in exceptions:
                exceptions.append(exception)

    return exceptions


def extract_root_exception(text: str):

    root_causes = []

    for line in text.splitlines():

        if "Caused by:" not in line:
            continue

        match = re.search(
            r"Caused by:\s+"
            r"((?:java|javax|jakarta|org|com)\."
            r"[\w.$]+"
            r"(?:Exception|Error))",
            line
        )

        if match:
            root_causes.append(match.group(1))

    if root_causes:
        return root_causes[-1]

    return ""


def detect_evidence_flags(text: str):

    flags = []

    checks = {
        "SLF4J_NO_PROVIDER":
            "No SLF4J providers were found" in text,

        "SLF4J_IGNORED_BINDING":
            "Ignoring binding found at" in text,

        "NOPLOGGER":
            "NOPLogger" in text,

        "CLASS_CAST_EXCEPTION":
            "ClassCastException" in text,

        "NO_CLASS_DEF":
            "NoClassDefFoundError" in text,

        "CLASS_NOT_FOUND":
            "ClassNotFoundException" in text,

        "NO_SUCH_METHOD":
            "NoSuchMethodError" in text,

        "NO_SUCH_FIELD":
            "NoSuchFieldError" in text,

        "ABSTRACT_METHOD":
            "AbstractMethodError" in text,

        "ASSERTION_ERROR":
            "AssertionError" in text,

        "EXPECTED_ACTUAL":
            (
                "expected:" in text.lower()
                or "but was:" in text.lower()
                or "expected <" in text.lower()
                or "expected [" in text.lower()
            ),
    }

    for flag, present in checks.items():

        if present:
            flags.append(flag)

    return flags


# =========================================================
# PRELIMINARY ROOT-CAUSE CLASSIFIER
# =========================================================

def classify_preliminary(text: str, flags):

    # -----------------------------------------------------
    # 1. Logging provider compatibility
    # -----------------------------------------------------

    if (
        "SLF4J_NO_PROVIDER" in flags
        and (
            "NOPLOGGER" in flags
            or "SLF4J_IGNORED_BINDING" in flags
        )
    ):

        return {
            "root_cause":
                "RUNTIME_PROVIDER_COMPATIBILITY",

            "semantic_candidate":
                "NO",

            "confidence":
                "HIGH",

            "manual_review":
                "NO"
        }

    # -----------------------------------------------------
    # 2. Missing/incompatible runtime dependencies
    # -----------------------------------------------------

    runtime_dependency_flags = {
        "NO_CLASS_DEF",
        "CLASS_NOT_FOUND",
        "NO_SUCH_METHOD",
        "NO_SUCH_FIELD",
        "ABSTRACT_METHOD",
    }

    if runtime_dependency_flags.intersection(flags):

        return {
            "root_cause":
                "RUNTIME_DEPENDENCY_COMPATIBILITY",

            "semantic_candidate":
                "NO",

            "confidence":
                "HIGH",

            "manual_review":
                "NO"
        }

    # -----------------------------------------------------
    # 3. Assertion/output mismatch
    # -----------------------------------------------------

    if (
        "ASSERTION_ERROR" in flags
        or "EXPECTED_ACTUAL" in flags
    ):

        return {
            "root_cause":
                "POSSIBLE_BEHAVIORAL_CHANGE",

            "semantic_candidate":
                "REVIEW",

            "confidence":
                "MEDIUM",

            "manual_review":
                "YES"
        }

    # -----------------------------------------------------
    # 4. Other runtime exceptions
    # -----------------------------------------------------

    if "Exception" in text or "Error" in text:

        return {
            "root_cause":
                "RUNTIME_EXCEPTION_REVIEW",

            "semantic_candidate":
                "REVIEW",

            "confidence":
                "LOW",

            "manual_review":
                "YES"
        }

    # -----------------------------------------------------
    # 5. Unknown
    # -----------------------------------------------------

    return {
        "root_cause":
            "UNKNOWN",

        "semantic_candidate":
            "REVIEW",

        "confidence":
            "LOW",

        "manual_review":
            "YES"
    }


# =========================================================
# MAIN
# =========================================================

df = pd.read_csv(INPUT_CSV)

print(f"Total TEST_FAILURE cases available: {len(df)}")

# Only first three for verification
df = df.head(MAX_CASES)

results = []


for index, row in df.iterrows():

    case_id = str(row["case_id"])

    short_id = case_id[:8]

    pre_log = LOG_DIR / f"{short_id}_pre.log"

    breaking_log = LOG_DIR / f"{short_id}_breaking.log"

    print()
    print("=" * 70)
    print(f"Case {index + 1}")
    print("=" * 70)

    print(f"Case ID      : {case_id}")
    print(f"Project      : {row['project']}")

    dependency = (
        f"{row['dependency_group']}:"
        f"{row['dependency_artifact']}"
    )

    print(f"Dependency   : {dependency}")

    print(
        f"Version      : "
        f"{row['previous_version']} "
        f"-> "
        f"{row['new_version']}"
    )

    print(f"PRE log      : {pre_log}")
    print(f"Breaking log : {breaking_log}")

    # -----------------------------------------------------
    # Missing log handling
    # -----------------------------------------------------

    if not breaking_log.exists():

        print("Breaking log not found.")

        results.append({
            "case_id": case_id,
            "project": row["project"],
            "dependency": dependency,
            "old_version": row["previous_version"],
            "new_version": row["new_version"],
            "bump_category": row["failure_category"],
            "pre_build_status": "UNKNOWN",
            "breaking_build_status": "MISSING_LOG",
            "failing_test_count": 0,
            "failing_tests": "",
            "main_exception": "",
            "root_exception": "",
            "evidence_flags": "",
            "preliminary_root_cause": "MISSING_LOG",
            "semantic_candidate": "UNKNOWN",
            "confidence": "NONE",
            "manual_review_required": "YES",
            "pre_log_file": str(pre_log),
            "breaking_log_file": str(breaking_log),
        })

        continue

    # -----------------------------------------------------
    # Read logs
    # -----------------------------------------------------

    pre_text = read_log(pre_log)

    breaking_text = read_log(breaking_log)

    # -----------------------------------------------------
    # Extract evidence
    # -----------------------------------------------------

    pre_build_status = get_build_status(pre_text)

    breaking_build_status = get_build_status(
        breaking_text
    )

    failing_tests = extract_failing_tests(
        breaking_text
    )

    exceptions = extract_exceptions(
        breaking_text
    )

    main_exception = (
        exceptions[0]
        if exceptions
        else ""
    )

    root_exception = extract_root_exception(
        breaking_text
    )

    flags = detect_evidence_flags(
        breaking_text
    )

    classification = classify_preliminary(
        breaking_text,
        flags
    )

    # -----------------------------------------------------
    # Print result
    # -----------------------------------------------------

    print()
    print("Extracted evidence")
    print("-" * 70)

    print(
        f"PRE build     : "
        f"{pre_build_status}"
    )

    print(
        f"Breaking build: "
        f"{breaking_build_status}"
    )

    print(
        f"Failing tests : "
        f"{len(failing_tests)}"
    )

    print(
        f"Main exception: "
        f"{main_exception}"
    )

    print(
        f"Root exception: "
        f"{root_exception}"
    )

    print(
        f"Evidence flags: "
        f"{', '.join(flags)}"
    )

    print()
    print("Preliminary classification")
    print("-" * 70)

    print(
        f"Root cause    : "
        f"{classification['root_cause']}"
    )

    print(
        f"Semantic cand.: "
        f"{classification['semantic_candidate']}"
    )

    print(
        f"Confidence    : "
        f"{classification['confidence']}"
    )

    print(
        f"Manual review : "
        f"{classification['manual_review']}"
    )

    # -----------------------------------------------------
    # Save row
    # -----------------------------------------------------

    results.append({

        "case_id":
            case_id,

        "project":
            row["project"],

        "dependency":
            dependency,

        "old_version":
            row["previous_version"],

        "new_version":
            row["new_version"],

        "bump_category":
            row["failure_category"],

        "pre_build_status":
            pre_build_status,

        "breaking_build_status":
            breaking_build_status,

        "failing_test_count":
            len(failing_tests),

        "failing_tests":
            " | ".join(failing_tests),

        "main_exception":
            main_exception,

        "root_exception":
            root_exception,

        "evidence_flags":
            " | ".join(flags),

        "preliminary_root_cause":
            classification["root_cause"],

        "semantic_candidate":
            classification["semantic_candidate"],

        "confidence":
            classification["confidence"],

        "manual_review_required":
            classification["manual_review"],

        "pre_log_file":
            str(pre_log),

        "breaking_log_file":
            str(breaking_log),
    })


# =========================================================
# SAVE RESULTS
# =========================================================

result_df = pd.DataFrame(results)

result_df.to_csv(
    OUTPUT_CSV,
    index=False
)

print()
print("=" * 70)
print("PRELIMINARY CLASSIFICATION COMPLETED")
print("=" * 70)

print(f"Cases processed : {len(result_df)}")

print(
    f"Output saved to : "
    f"{OUTPUT_CSV}"
)

print()
print("Classification summary:")

if not result_df.empty:

    print(
        result_df[
            "preliminary_root_cause"
        ].value_counts()
    )