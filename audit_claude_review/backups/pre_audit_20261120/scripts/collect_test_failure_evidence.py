import argparse
import re
import subprocess
import time
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(
    r"C:\Users\TASHEEN\Desktop\Research Implementation"
)

INPUT_FILE = BASE_DIR / "results" / "test_failure_candidates.csv"

OUTPUT_FILE = BASE_DIR / "results" / "test_failure_evidence.csv"

LOG_DIR = BASE_DIR / "logs" / "test_failure_evidence"

TIMEOUT_SECONDS = 45 * 60


# ---------------------------------------------------------
# Setup
# ---------------------------------------------------------

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# Docker runner
# ---------------------------------------------------------

def prepare_docker_command(command):
    """
    Convert:

        docker run IMAGE

    into:

        docker run --rm IMAGE

    so stopped containers are not left behind.
    """

    parts = command.split()

    if (
        len(parts) >= 2
        and parts[0].lower() == "docker"
        and parts[1].lower() == "run"
        and "--rm" not in parts
    ):
        parts.insert(2, "--rm")

    return parts


def run_image(command, case_id, build_type):

    short_id = case_id[:8]

    log_file = (
        LOG_DIR
        / f"{short_id}_{build_type}.log"
    )

    command_parts = prepare_docker_command(
        command
    )

    print()
    print(
        "=========================================="
    )
    print(
        f"Running {build_type.upper()} image"
    )
    print(f"Case: {case_id}")
    print(f"Log : {log_file}")
    print(
        "=========================================="
    )

    start_time = time.time()

    try:

        with log_file.open(
            "w",
            encoding="utf-8"
        ) as log:

            process = subprocess.run(
                command_parts,
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=TIMEOUT_SECONDS
            )

        duration = round(
            time.time() - start_time,
            2
        )

        return {
            "exit_code": process.returncode,
            "duration_seconds": duration,
            "timeout": False,
            "log_file": str(log_file)
        }

    except subprocess.TimeoutExpired:

        duration = round(
            time.time() - start_time,
            2
        )

        return {
            "exit_code": None,
            "duration_seconds": duration,
            "timeout": True,
            "log_file": str(log_file)
        }


# ---------------------------------------------------------
# Maven log analysis
# ---------------------------------------------------------

def analyze_log(log_file):

    text = Path(log_file).read_text(
        encoding="utf-8",
        errors="ignore"
    )

    build_success = (
        "BUILD SUCCESS" in text
    )

    build_failure = (
        "BUILD FAILURE" in text
    )

    compilation_error = (
        "COMPILATION ERROR" in text
        or "Compilation failure" in text
    )

    # -----------------------------------------------------
    # Test summary lines
    # -----------------------------------------------------

    test_summary_lines = []

    for line in text.splitlines():

        if "Tests run:" in line:
            test_summary_lines.append(
                line.strip()
            )

    # -----------------------------------------------------
    # Failure / exception evidence
    # -----------------------------------------------------

    evidence_keywords = [
        "<<< FAILURE!",
        "<<< ERROR!",
        "AssertionError",
        "AssertionFailedError",
        "Caused by:",
        "Exception",
        "NoClassDefFoundError",
        "ClassNotFoundException",
        "NoSuchMethodError",
        "NoSuchFieldError",
        "AbstractMethodError",
        "IncompatibleClassChangeError",
        "UnsupportedClassVersionError",
        "LinkageError",
        "BUILD FAILURE",
    ]

    important_lines = []

    for line in text.splitlines():

        if any(
            keyword.lower()
            in line.lower()
            for keyword
            in evidence_keywords
        ):
            important_lines.append(
                line.strip()
            )

    # Keep output readable.
    important_lines = important_lines[:120]

    # -----------------------------------------------------
    # Binary/linkage evidence
    # -----------------------------------------------------

    linkage_patterns = [
        "NoClassDefFoundError",
        "NoSuchMethodError",
        "NoSuchFieldError",
        "AbstractMethodError",
        "IncompatibleClassChangeError",
        "UnsupportedClassVersionError",
        "LinkageError",
    ]

    linkage_signals = []

    for pattern in linkage_patterns:

        if pattern in text:
            linkage_signals.append(
                pattern
            )

    # -----------------------------------------------------
    # Assertion evidence
    # -----------------------------------------------------

    assertion_signal = bool(
        re.search(
            r"AssertionError|"
            r"AssertionFailedError|"
            r"expected:<|"
            r"expected:",
            text,
            re.IGNORECASE
        )
    )

    # -----------------------------------------------------
    # Exception names
    # -----------------------------------------------------

    exception_pattern = re.compile(
        r"\b(?:java\.)?"
        r"[A-Za-z0-9_$.]+"
        r"(?:Exception|Error)\b"
    )

    exception_names = []

    for match in exception_pattern.findall(
        text
    ):

        if match not in exception_names:
            exception_names.append(
                match
            )

    exception_names = exception_names[:30]

    # -----------------------------------------------------
    # Evidence status
    # -----------------------------------------------------

    if compilation_error:

        evidence_status = (
            "COMPILATION_FAILURE_FOUND"
        )

    elif (
        build_failure
        and len(test_summary_lines) > 0
    ):

        evidence_status = (
            "TEST_PHASE_BREAKAGE_FOUND"
        )

    elif build_success:

        evidence_status = (
            "BUILD_SUCCESS"
        )

    else:

        evidence_status = (
            "NEEDS_MANUAL_REVIEW"
        )

    return {
        "build_success":
            build_success,

        "build_failure":
            build_failure,

        "compilation_error":
            compilation_error,

        "evidence_status":
            evidence_status,

        "test_summary_lines":
            "\n".join(
                test_summary_lines
            ),

        "assertion_signal":
            assertion_signal,

        "binary_linkage_signal":
            len(linkage_signals) > 0,

        "linkage_signals":
            ", ".join(
                linkage_signals
            ),

        "exception_names":
            ", ".join(
                exception_names
            ),

        "important_log_lines":
            "\n".join(
                important_lines
            )
    }


# ---------------------------------------------------------
# Save / update evidence CSV
# ---------------------------------------------------------

def save_result(result):

    new_df = pd.DataFrame(
        [result]
    )

    if OUTPUT_FILE.exists():

        old_df = pd.read_csv(
            OUTPUT_FILE
        )

        # Remove an older row for the same case
        # so rerunning a case does not duplicate it.
        if "case_id" in old_df.columns:

            old_df = old_df[
                old_df["case_id"]
                != result["case_id"]
            ]

        combined = pd.concat(
            [
                old_df,
                new_df
            ],
            ignore_index=True
        )

    else:

        combined = new_df

    combined.to_csv(
        OUTPUT_FILE,
        index=False
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

parser = argparse.ArgumentParser(
    description=(
        "Collect PRE and BREAKING evidence "
        "for one BUMP TEST_FAILURE case."
    )
)

parser.add_argument(
    "--case-number",
    type=int,
    required=True,
    help=(
        "1-based row number from "
        "test_failure_candidates.csv"
    )
)

args = parser.parse_args()


df = pd.read_csv(
    INPUT_FILE
)

case_number = args.case_number

if (
    case_number < 1
    or case_number > len(df)
):
    raise ValueError(
        f"Case number must be between "
        f"1 and {len(df)}."
    )


# Convert human numbering to Python index.
row = df.iloc[
    case_number - 1
]

case_id = str(
    row["case_id"]
)


print()
print(
    "=========================================="
)
print(
    f"BUMP candidate #{case_number}"
)
print(
    "=========================================="
)

print(
    f"Case ID    : {case_id}"
)

print(
    f"Project    : {row['project']}"
)

print(
    "Dependency : "
    f"{row['dependency_group']}:"
    f"{row['dependency_artifact']}"
)

print(
    "Version    : "
    f"{row['previous_version']} "
    f"-> "
    f"{row['new_version']}"
)

print(
    f"BUMP label : "
    f"{row['failure_category']}"
)


# ---------------------------------------------------------
# Run PRE
# ---------------------------------------------------------

pre_run = run_image(
    row["pre_command"],
    case_id,
    "pre"
)

pre_analysis = analyze_log(
    pre_run["log_file"]
)


# ---------------------------------------------------------
# Run BREAKING
# ---------------------------------------------------------

breaking_run = run_image(
    row["breaking_command"],
    case_id,
    "breaking"
)

breaking_analysis = analyze_log(
    breaking_run["log_file"]
)


# ---------------------------------------------------------
# Create evidence record
# ---------------------------------------------------------

result = {

    "candidate_number":
        case_number,

    "case_id":
        case_id,

    "project":
        row["project"],

    "dependency_group":
        row["dependency_group"],

    "dependency_artifact":
        row["dependency_artifact"],

    "previous_version":
        row["previous_version"],

    "new_version":
        row["new_version"],

    "java_version":
        row.get(
            "java_version",
            ""
        ),

    "bump_failure_category":
        row["failure_category"],

    # PRE
    "pre_exit_code":
        pre_run["exit_code"],

    "pre_timeout":
        pre_run["timeout"],

    "pre_duration_seconds":
        pre_run["duration_seconds"],

    "pre_build_success":
        pre_analysis[
            "build_success"
        ],

    "pre_build_failure":
        pre_analysis[
            "build_failure"
        ],

    "pre_compilation_error":
        pre_analysis[
            "compilation_error"
        ],

    "pre_test_summary_lines":
        pre_analysis[
            "test_summary_lines"
        ],

    "pre_log_file":
        pre_run["log_file"],

    # BREAKING
    "breaking_exit_code":
        breaking_run[
            "exit_code"
        ],

    "breaking_timeout":
        breaking_run[
            "timeout"
        ],

    "breaking_duration_seconds":
        breaking_run[
            "duration_seconds"
        ],

    "breaking_build_success":
        breaking_analysis[
            "build_success"
        ],

    "breaking_build_failure":
        breaking_analysis[
            "build_failure"
        ],

    "breaking_compilation_error":
        breaking_analysis[
            "compilation_error"
        ],

    "breaking_test_summary_lines":
        breaking_analysis[
            "test_summary_lines"
        ],

    "assertion_signal":
        breaking_analysis[
            "assertion_signal"
        ],

    "binary_linkage_signal":
        breaking_analysis[
            "binary_linkage_signal"
        ],

    "linkage_signals":
        breaking_analysis[
            "linkage_signals"
        ],

    "exception_names":
        breaking_analysis[
            "exception_names"
        ],

    "evidence_status":
        breaking_analysis[
            "evidence_status"
        ],

    "breaking_log_file":
        breaking_run["log_file"],

    "important_log_lines":
        breaking_analysis[
            "important_log_lines"
        ],

    # IMPORTANT:
    # Automation does NOT decide this.
    "behavioral_status":
        "PENDING_MANUAL_REVIEW"
}


save_result(
    result
)


# ---------------------------------------------------------
# Console summary
# ---------------------------------------------------------

print()
print(
    "=========================================="
)
print(
    "AUTOMATED EVIDENCE SUMMARY"
)
print(
    "=========================================="
)

print()
print("PRE:")
print(
    f"  Build success      : "
    f"{pre_analysis['build_success']}"
)
print(
    f"  Compilation error  : "
    f"{pre_analysis['compilation_error']}"
)

print()
print("BREAKING:")
print(
    f"  Build failure      : "
    f"{breaking_analysis['build_failure']}"
)
print(
    f"  Compilation error  : "
    f"{breaking_analysis['compilation_error']}"
)
print(
    f"  Assertion signal   : "
    f"{breaking_analysis['assertion_signal']}"
)
print(
    f"  Linkage signal     : "
    f"{breaking_analysis['binary_linkage_signal']}"
)
print(
    f"  Linkage types      : "
    f"{breaking_analysis['linkage_signals']}"
)
print(
    f"  Exceptions/errors  : "
    f"{breaking_analysis['exception_names']}"
)

print()
print(
    "IMPORTANT:"
)
print(
    "No semantic classification was made "
    "automatically."
)
print(
    "behavioral_status = "
    "PENDING_MANUAL_REVIEW"
)

print()
print(
    f"Evidence CSV: "
    f"{OUTPUT_FILE}"
)

print(
    f"PRE log     : "
    f"{pre_run['log_file']}"
)

print(
    f"BREAKING log: "
    f"{breaking_run['log_file']}"
)