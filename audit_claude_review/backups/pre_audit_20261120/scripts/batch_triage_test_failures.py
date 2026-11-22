import argparse
import os
import re
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

import pandas as pd


# =========================================================
# Configuration
# =========================================================

BASE_DIR = Path(
    r"C:\Users\TASHEEN\Desktop\Research Implementation"
)

INPUT_FILE = (
    BASE_DIR
    / "results"
    / "test_failure_candidates.csv"
)

CLASSIFICATION_FILE = (
    BASE_DIR
    / "results"
    / "behavioral_classification.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "results"
    / "batch_triage_results.csv"
)

LOG_DIR = (
    BASE_DIR
    / "logs"
    / "batch_triage"
)

TIMEOUT_SECONDS = 45 * 60

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# Important error types
# =========================================================

LINKAGE_ERRORS = [
    "NoClassDefFoundError",
    "ClassNotFoundException",
    "NoSuchMethodError",
    "NoSuchFieldError",
    "AbstractMethodError",
    "IncompatibleClassChangeError",
    "UnsupportedClassVersionError",
    "LinkageError",
]

RUNTIME_EXCEPTIONS = [
    "ClassCastException",
    "NullPointerException",
    "IllegalArgumentException",
    "IllegalStateException",
    "UnsupportedOperationException",
    "IndexOutOfBoundsException",
    "RuntimeException",
]

ASSERTION_PATTERNS = [
    "AssertionError",
    "AssertionFailedError",
    "ComparisonFailure",
]


# =========================================================
# Helpers
# =========================================================

def prepare_docker_command(command):
    """
    Adds --rm to BUMP docker commands.

    Example:

        docker run IMAGE

    becomes:

        docker run --rm IMAGE
    """

    parts = str(command).split()

    if (
        len(parts) >= 2
        and parts[0].lower() == "docker"
        and parts[1].lower() == "run"
        and "--rm" not in parts
    ):
        parts.insert(2, "--rm")

    return parts


def run_docker_image(
    command,
    case_id,
    run_type
):
    """
    Runs PRE or BREAKING Docker image
    and saves the complete Maven log.
    """

    short_id = case_id[:8]

    log_file = (
        LOG_DIR
        / f"{short_id}_{run_type}.log"
    )

    command_parts = prepare_docker_command(
        command
    )

    # Keep the exact test environment available for Surefire/source extraction.
    if args.retain_containers:
        command_parts.remove("--rm")
        command_parts[2:2] = ["--name", f"bump-{case_id}-{run_type}"]

    if log_file.exists():
        if not args.force:
            raise FileExistsError(f"Existing evidence must be inspected first: {log_file}")
        shutil.copy2(log_file, log_file.with_name(log_file.name + "." +
                     datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".bak"))

    print()
    print(
        "=============================================="
    )
    print(
        f"{run_type.upper()} - {case_id}"
    )
    print(
        f"Log: {log_file}"
    )
    print(
        "=============================================="
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
            "exit_code":
                process.returncode,

            "timeout":
                False,

            "duration_seconds":
                duration,

            "log_file":
                str(log_file),

            "runner_error":
                "",
        }

    except subprocess.TimeoutExpired:

        duration = round(
            time.time() - start_time,
            2
        )

        return {
            "exit_code":
                None,

            "timeout":
                True,

            "duration_seconds":
                duration,

            "log_file":
                str(log_file),

            "runner_error":
                "TIMEOUT",
        }

    except Exception as exc:

        duration = round(
            time.time() - start_time,
            2
        )

        return {
            "exit_code":
                None,

            "timeout":
                False,

            "duration_seconds":
                duration,

            "log_file":
                str(log_file),

            "runner_error":
                str(exc),
        }


# =========================================================
# Maven test-summary extraction
# =========================================================

TEST_SUMMARY_RE = re.compile(
    r"Tests run:\s*(\d+),\s*"
    r"Failures:\s*(\d+),\s*"
    r"Errors:\s*(\d+),\s*"
    r"Skipped:\s*(\d+)",
    re.IGNORECASE
)


def extract_test_summaries(text):

    summaries = []

    for line in text.splitlines():

        match = TEST_SUMMARY_RE.search(
            line
        )

        if not match:
            continue

        summary = {
            "tests":
                int(match.group(1)),

            "failures":
                int(match.group(2)),

            "errors":
                int(match.group(3)),

            "skipped":
                int(match.group(4)),

            "line":
                line.strip(),

            # Maven per-class lines often contain:
            # "- in SomeTest"
            "aggregate_candidate":
                " - in " not in line,
        }

        summaries.append(
            summary
        )

    return summaries


def choose_last_aggregate_summary(
    summaries
):
    """
    Returns the last module-level aggregate summary
    when Maven provides one.

    Important:
    For multi-module projects this is only a useful
    automated hint. Human review can still inspect
    all test summaries.
    """

    aggregate = [
        item
        for item in summaries
        if item["aggregate_candidate"]
    ]

    if aggregate:
        return aggregate[-1]

    if summaries:
        return summaries[-1]

    return {
        "tests": "",
        "failures": "",
        "errors": "",
        "skipped": "",
        "line": "",
        "aggregate_candidate": False,
    }


# =========================================================
# Log analysis
# =========================================================

def analyze_log(log_file):

    path = Path(log_file)

    if not path.exists():

        return {
            "build_success": False,
            "build_failure": False,
            "compilation_error": False,
            "tests": "",
            "failures": "",
            "errors": "",
            "skipped": "",
            "all_test_summaries": "",
            "assertion_signal": False,
            "linkage_signal": False,
            "linkage_types": "",
            "runtime_exception_signal": False,
            "runtime_exception_types": "",
            "exception_names": "",
            "important_lines": "",
        }

    text = path.read_text(
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
        or "Compilation failure:" in text
    )

    # -----------------------------------------------------
    # Test summaries
    # -----------------------------------------------------

    summaries = extract_test_summaries(
        text
    )

    selected_summary = (
        choose_last_aggregate_summary(
            summaries
        )
    )

    all_test_summaries = "\n".join(
        item["line"]
        for item in summaries
    )

    # -----------------------------------------------------
    # Linkage errors
    # -----------------------------------------------------

    linkage_types = []

    class_initialization_failure = (
        "NoClassDefFoundError: Could not initialize class" in text
        or "ExceptionInInitializerError" in text
    )

    for error_name in LINKAGE_ERRORS:

        if error_name in text:

            # "Could not initialize class" is not evidence that
            # the class is missing. It can be a secondary error
            # caused by failed static initialization.
            if (
                error_name == "NoClassDefFoundError"
                and class_initialization_failure
            ):
                continue

            linkage_types.append(
                error_name
            )

    # -----------------------------------------------------
    # Runtime exceptions
    # -----------------------------------------------------

    runtime_types = []

    for exception_name in RUNTIME_EXCEPTIONS:

        if exception_name in text:

            runtime_types.append(
                exception_name
            )

    # -----------------------------------------------------
    # Assertion signal
    # -----------------------------------------------------

    assertion_signal = any(
        pattern.lower()
        in text.lower()
        for pattern
        in ASSERTION_PATTERNS
    )

    # -----------------------------------------------------
    # Extract exception/error names
    # -----------------------------------------------------

    exception_regex = re.compile(
        r"\b(?:java\.)?"
        r"(?:[a-zA-Z_$][\w$]*\.)*"
        r"[A-Z][A-Za-z0-9_$]*"
        r"(?:Exception|Error)\b"
    )

    exception_names = []

    for match in exception_regex.findall(
        text
    ):

        if match not in exception_names:

            exception_names.append(
                match
            )

    exception_names = (
        exception_names[:40]
    )

    # -----------------------------------------------------
    # Important evidence lines
    # -----------------------------------------------------

    important_patterns = [
        "<<< FAILURE!",
        "<<< ERROR!",
        "AssertionError",
        "AssertionFailedError",
        "ComparisonFailure",
        "NoClassDefFoundError",
        "ClassNotFoundException",
        "NoSuchMethodError",
        "NoSuchFieldError",
        "AbstractMethodError",
        "IncompatibleClassChangeError",
        "UnsupportedClassVersionError",
        "ClassCastException",
        "NullPointerException",
        "IllegalArgumentException",
        "IllegalStateException",
        "UnsupportedOperationException",
        "Caused by:",
        "Failed tests:",
        "Tests in error:",
        "BUILD FAILURE",
    ]

    important_lines = []

    for line in text.splitlines():

        if any(
            pattern.lower()
            in line.lower()
            for pattern
            in important_patterns
        ):

            important_lines.append(
                line.strip()
            )

    # Keep CSV manageable.
    important_lines = (
        important_lines[:120]
    )

    return {
        "build_success":
            build_success,

        "build_failure":
            build_failure,

        "compilation_error":
            compilation_error,

        "tests":
            selected_summary["tests"],

        "failures":
            selected_summary["failures"],

        "errors":
            selected_summary["errors"],

        "skipped":
            selected_summary["skipped"],

        "all_test_summaries":
            all_test_summaries,

        "assertion_signal":
            assertion_signal,

        "linkage_signal":
            len(linkage_types) > 0,

        "linkage_types":
            ", ".join(
                linkage_types
            ),

        "runtime_exception_signal":
            len(runtime_types) > 0,

        "runtime_exception_types":
            ", ".join(
                runtime_types
            ),

        "exception_names":
            ", ".join(
                exception_names
            ),

        "important_lines":
            "\n".join(
                important_lines
            ),
    }


# =========================================================
# Automated TRIAGE
# =========================================================

def determine_triage(
    pre_analysis,
    breaking_analysis,
    pre_run,
    breaking_run
):
    """
    IMPORTANT:

    This function does NOT create final research
    ground truth.

    It only produces an automated TRIAGE suggestion.
    """

    if (
        pre_run["timeout"]
        or breaking_run["timeout"]
    ):

        return (
            "AUTO_UNCERTAIN_TIMEOUT"
        )

    if (
        pre_run["runner_error"]
        or breaking_run["runner_error"]
    ):

        return (
            "AUTO_UNCERTAIN_RUNNER_ERROR"
        )

    # Healthy PRE is required.
    if not pre_analysis[
        "build_success"
    ]:

        return (
            "AUTO_BASELINE_PROBLEM"
        )

    # BUMP TEST_FAILURE candidate unexpectedly
    # becomes a compile failure during reproduction.
    if breaking_analysis[
        "compilation_error"
    ]:

        return (
            "AUTO_NON_TEST_PHASE_BREAKAGE"
        )

    # Breaking image unexpectedly passes.
    if breaking_analysis[
        "build_success"
    ]:

        return (
            "AUTO_BREAKAGE_NOT_REPRODUCED"
        )

    # Strong binary/runtime compatibility signal.
    if breaking_analysis[
        "linkage_signal"
    ]:

        return (
            "AUTO_NON_BEHAVIORAL_CANDIDATE"
        )

    failures = (
        breaking_analysis["failures"]
    )

    errors = (
        breaking_analysis["errors"]
    )

    # Assertion-only breakages are good behavioral
    # candidates, but MUST still be manually checked.
    if (
        breaking_analysis[
            "assertion_signal"
        ]
        and failures != ""
        and failures > 0
        and (
            errors == ""
            or errors == 0
        )
    ):

        return (
            "AUTO_LIKELY_BEHAVIORAL_CANDIDATE"
        )

    # Runtime exceptions are ambiguous:
    # they may be semantic OR non-semantic.
    if (
        breaking_analysis[
            "runtime_exception_signal"
        ]
        or (
            errors != ""
            and errors > 0
        )
    ):

        return (
            "AUTO_RUNTIME_REVIEW_REQUIRED"
        )

    if breaking_analysis[
        "assertion_signal"
    ]:

        return (
            "AUTO_LIKELY_BEHAVIORAL_CANDIDATE"
        )

    return (
        "AUTO_UNCERTAIN"
    )


# =========================================================
# Output persistence
# =========================================================

def load_existing_results():

    if not OUTPUT_FILE.exists():

        return pd.DataFrame()

    # Fail closed: a read failure must never be mistaken for an empty dataset.
    frame = pd.read_csv(OUTPUT_FILE, dtype=str, keep_default_na=False)
    if "case_id" not in frame or frame["case_id"].eq("").any() or frame["case_id"].duplicated().any():
        raise ValueError("Invalid or duplicate case IDs in existing batch results")
    return frame


def save_or_update_result(
    result
):

    old_df = load_existing_results()

    new_df = pd.DataFrame(
        [result]
    )

    if (
        not old_df.empty
        and "case_id"
        in old_df.columns
    ):

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

    if "candidate_number" in combined.columns:

        combined = combined.sort_values(
            by="candidate_number", key=lambda values: pd.to_numeric(values)
        )

    temporary = OUTPUT_FILE.with_suffix(".csv.tmp")
    combined.to_csv(temporary, index=False)
    if OUTPUT_FILE.exists():
        backup_dir = OUTPUT_FILE.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        shutil.copy2(OUTPUT_FILE, backup_dir / (
            OUTPUT_FILE.name + "." + datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".bak"))
    os.replace(temporary, OUTPUT_FILE)


# =========================================================
# Existing manual classifications
# =========================================================

def get_existing_classified_ids():

    if not CLASSIFICATION_FILE.exists():

        return set()

    try:

        df = pd.read_csv(
            CLASSIFICATION_FILE,
            dtype=str
        )

        if "case_id" not in df.columns:

            return set()

        return set(
            df["case_id"]
            .dropna()
            .astype(str)
            .tolist()
        )

    except Exception as exc:
        raise ValueError("Cannot safely read existing manual classifications") from exc


# =========================================================
# Process one candidate
# =========================================================

def process_candidate(
    candidate_number,
    row,
    force=False
):

    case_id = str(
        row["case_id"]
    )

    print()
    print()
    print(
        "##################################################"
    )
    print(
        f"CANDIDATE #{candidate_number}"
    )
    print(
        "##################################################"
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
        f"Java       : "
        f"{row.get('java_version', '')}"
    )

    # -----------------------------------------------------
    # PRE
    # -----------------------------------------------------

    pre_run = run_docker_image(
        row["pre_command"],
        case_id,
        "pre"
    )

    pre_analysis = analyze_log(
        pre_run["log_file"]
    )

    # -----------------------------------------------------
    # BREAKING
    # -----------------------------------------------------

    breaking_run = run_docker_image(
        row["breaking_command"],
        case_id,
        "breaking"
    )

    breaking_analysis = analyze_log(
        breaking_run["log_file"]
    )

    # -----------------------------------------------------
    # Automated triage suggestion
    # -----------------------------------------------------

    auto_triage = determine_triage(
        pre_analysis,
        breaking_analysis,
        pre_run,
        breaking_run
    )

    result = {
        "candidate_number":
            candidate_number,

        "case_id":
            case_id,

        "project":
            row["project"],

        "organisation":
            row.get(
                "organisation",
                ""
            ),

        "dependency_group":
            row["dependency_group"],

        "dependency_artifact":
            row["dependency_artifact"],

        "previous_version":
            row["previous_version"],

        "new_version":
            row["new_version"],

        "dependency_scope":
            row.get(
                "dependency_scope",
                ""
            ),

        "version_update_type":
            row.get(
                "version_update_type",
                ""
            ),

        "java_version":
            row.get(
                "java_version",
                ""
            ),

        "bump_failure_category":
            row["failure_category"],

        "pull_request_url":
            row.get(
                "pull_request_url",
                ""
            ),

        # ---------------------------------------------
        # PRE
        # ---------------------------------------------

        "pre_exit_code":
            pre_run["exit_code"],

        "pre_timeout":
            pre_run["timeout"],

        "pre_duration_seconds":
            pre_run[
                "duration_seconds"
            ],

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

        "pre_tests":
            pre_analysis[
                "tests"
            ],

        "pre_failures":
            pre_analysis[
                "failures"
            ],

        "pre_errors":
            pre_analysis[
                "errors"
            ],

        "pre_skipped":
            pre_analysis[
                "skipped"
            ],

        "pre_all_test_summaries":
            pre_analysis[
                "all_test_summaries"
            ],

        "pre_log":
            pre_run[
                "log_file"
            ],

        # ---------------------------------------------
        # BREAKING
        # ---------------------------------------------

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

        "breaking_tests":
            breaking_analysis[
                "tests"
            ],

        "breaking_failures":
            breaking_analysis[
                "failures"
            ],

        "breaking_errors":
            breaking_analysis[
                "errors"
            ],

        "breaking_skipped":
            breaking_analysis[
                "skipped"
            ],

        "breaking_all_test_summaries":
            breaking_analysis[
                "all_test_summaries"
            ],

        # ---------------------------------------------
        # Signals
        # ---------------------------------------------

        "assertion_signal":
            breaking_analysis[
                "assertion_signal"
            ],

        "binary_linkage_signal":
            breaking_analysis[
                "linkage_signal"
            ],

        "linkage_types":
            breaking_analysis[
                "linkage_types"
            ],

        "runtime_exception_signal":
            breaking_analysis[
                "runtime_exception_signal"
            ],

        "runtime_exception_types":
            breaking_analysis[
                "runtime_exception_types"
            ],

        "exception_names":
            breaking_analysis[
                "exception_names"
            ],

        "important_log_lines":
            breaking_analysis[
                "important_lines"
            ],

        "breaking_log":
            breaking_run[
                "log_file"
            ],

        # ---------------------------------------------
        # TRIAGE ONLY
        # ---------------------------------------------

        "auto_triage":
            auto_triage,

        "human_review_status":
            "PENDING_MANUAL_REVIEW",

        "reviewer_1_label":
            "",

        "reviewer_2_label":
            "",

        "final_label":
            "",

        "notes":
            "",
    }

    save_or_update_result(
        result
    )

    print()
    print(
        "---------------- AUTOMATED RESULT ----------------"
    )

    print(
        f"PRE success      : "
        f"{pre_analysis['build_success']}"
    )

    print(
        f"BREAKING failure : "
        f"{breaking_analysis['build_failure']}"
    )

    print(
        f"Tests            : "
        f"{breaking_analysis['tests']}"
    )

    print(
        f"Failures         : "
        f"{breaking_analysis['failures']}"
    )

    print(
        f"Errors           : "
        f"{breaking_analysis['errors']}"
    )

    print(
        f"Assertion signal : "
        f"{breaking_analysis['assertion_signal']}"
    )

    print(
        f"Linkage signal   : "
        f"{breaking_analysis['linkage_signal']}"
    )

    print(
        f"Linkage types    : "
        f"{breaking_analysis['linkage_types']}"
    )

    print(
        f"Runtime signal   : "
        f"{breaking_analysis['runtime_exception_signal']}"
    )

    print()
    print(
        f"AUTO TRIAGE      : {auto_triage}"
    )

    print(
        "FINAL LABEL      : "
        "PENDING HUMAN REVIEW"
    )

    print(
        "----------------------------------------------------"
    )


# =========================================================
# Command-line arguments
# =========================================================

parser = argparse.ArgumentParser(
    description=(
        "Batch automated evidence collection and "
        "provisional triage for BUMP TEST_FAILURE cases."
    )
)

parser.add_argument(
    "--start-case",
    type=int,
    default=12,
    help=(
        "First candidate number to process. "
        "Default: 12"
    )
)

parser.add_argument(
    "--end-case",
    type=int,
    default=None,
    help=(
        "Last candidate number to process. "
        "Default: process to final candidate."
    )
)

parser.add_argument(
    "--force",
    action="store_true",
    help=(
        "Re-run cases even when a batch result "
        "already exists."
    )
)

parser.add_argument(
    "--retain-containers", action="store_true",
    help="Keep named PRE/BREAKING containers for evidence extraction; remove after archiving reports."
)

args = parser.parse_args()


# =========================================================
# Load candidate data
# =========================================================

candidates_df = pd.read_csv(
    INPUT_FILE
)

total_candidates = len(
    candidates_df
)

start_case = args.start_case

end_case = (
    args.end_case
    if args.end_case is not None
    else total_candidates
)

if (
    start_case < 1
    or start_case > total_candidates
):

    raise ValueError(
        f"--start-case must be between "
        f"1 and {total_candidates}"
    )

if (
    end_case < start_case
    or end_case > total_candidates
):

    raise ValueError(
        f"--end-case must be between "
        f"{start_case} and "
        f"{total_candidates}"
    )


# =========================================================
# Existing state
# =========================================================

existing_manual_ids = (
    get_existing_classified_ids()
)

existing_batch_df = (
    load_existing_results()
)

existing_batch_ids = set()

if (
    not existing_batch_df.empty
    and "case_id"
    in existing_batch_df.columns
):

    existing_batch_ids = set(
        existing_batch_df[
            "case_id"
        ]
        .dropna()
        .astype(str)
        .tolist()
    )


# =========================================================
# Batch processing
# =========================================================

print()
print(
    "======================================================"
)
print(
    "BUMP TEST_FAILURE AUTOMATED TRIAGE"
)
print(
    "======================================================"
)

print(
    f"Total candidates : "
    f"{total_candidates}"
)

print(
    f"Requested range  : "
    f"{start_case} -> {end_case}"
)

print(
    f"Already manually classified: "
    f"{len(existing_manual_ids)}"
)

print(
    f"Existing batch results      : "
    f"{len(existing_batch_ids)}"
)

print(
    "======================================================"
)


processed = 0
skipped_manual = 0
skipped_existing = 0


for candidate_number in range(
    start_case,
    end_case + 1
):

    row = candidates_df.iloc[
        candidate_number - 1
    ]

    case_id = str(
        row["case_id"]
    )

    # -----------------------------------------------------
    # Never overwrite already manually reviewed cases.
    # -----------------------------------------------------

    if case_id in existing_manual_ids:

        print(
            f"[SKIP] Candidate #{candidate_number} "
            f"already exists in "
            f"behavioral_classification.csv"
        )

        skipped_manual += 1

        continue

    # -----------------------------------------------------
    # Resume support
    # -----------------------------------------------------

    if (
        not args.force
        and case_id
        in existing_batch_ids
    ):

        print(
            f"[SKIP] Candidate #{candidate_number} "
            f"already has batch evidence."
        )

        skipped_existing += 1

        continue

    try:

        process_candidate(
            candidate_number,
            row,
            force=args.force
        )

        processed += 1

    except KeyboardInterrupt:

        print()
        print(
            "Batch interrupted by user."
        )

        print(
            "Completed results have already "
            "been saved."
        )

        break

    except Exception as exc:

        print()
        print(
            f"[ERROR] Candidate "
            f"#{candidate_number}: {exc}"
        )

        # Continue to next case instead of losing
        # the entire batch.
        continue


# =========================================================
# Final summary
# =========================================================

print()
print()
print(
    "======================================================"
)
print(
    "BATCH TRIAGE FINISHED"
)
print(
    "======================================================"
)

print(
    f"Processed             : "
    f"{processed}"
)

print(
    f"Skipped manual        : "
    f"{skipped_manual}"
)

print(
    f"Skipped existing batch: "
    f"{skipped_existing}"
)

print(
    f"Results               : "
    f"{OUTPUT_FILE}"
)

print(
    f"Logs                  : "
    f"{LOG_DIR}"
)

print()
print(
    "IMPORTANT:"
)

print(
    "auto_triage is only an automated screening result."
)

print(
    "human_review_status remains "
    "PENDING_MANUAL_REVIEW."
)

print(
    "Do not use auto_triage directly as final "
    "research ground truth."
)
