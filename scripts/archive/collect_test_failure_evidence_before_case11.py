import pandas as pd
import subprocess
import time
from pathlib import Path


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BASE_DIR = Path(
    r"C:\Users\TASHEEN\Desktop\Research Implementation"
)

INPUT_FILE = BASE_DIR / "results" / "test_failure_candidates.csv"

OUTPUT_FILE = BASE_DIR / "results" / "test_failure_evidence.csv"

LOG_DIR = BASE_DIR / "logs" / "test_failure_evidence"

# For now, process ONLY ONE case
MAX_CASES = 1

# Maximum time for one breaking image
TIMEOUT_SECONDS = 45 * 60


# ---------------------------------------------------------
# Setup
# ---------------------------------------------------------

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)

df = pd.read_csv(INPUT_FILE)

print(f"Available TEST_FAILURE cases: {len(df)}")

# Only first case for learning/testing
df = df.head(MAX_CASES)

results = []


# ---------------------------------------------------------
# Run breaking Docker image
# ---------------------------------------------------------

def run_breaking_image(command, case_id):

    short_id = case_id[:8]

    log_file = LOG_DIR / f"{short_id}_breaking.log"

    command_parts = command.split()

    # Convert:
    # docker run image
    #
    # into:
    # docker run --rm image

    if (
        len(command_parts) >= 2
        and command_parts[0] == "docker"
        and command_parts[1] == "run"
    ):
        command_parts.insert(2, "--rm")

    print()
    print("==========================================")
    print(f"Running case: {case_id}")
    print(f"Log: {log_file}")
    print("==========================================")

    start_time = time.time()

    try:

        with open(
            log_file,
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
            "log_file": log_file
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
            "log_file": log_file
        }


# ---------------------------------------------------------
# Analyze Maven log
# ---------------------------------------------------------

def analyze_log(log_file):

    text = Path(log_file).read_text(
        encoding="utf-8",
        errors="ignore"
    )

    build_success = "BUILD SUCCESS" in text
    build_failure = "BUILD FAILURE" in text

    compilation_error = (
        "COMPILATION ERROR" in text
        or "Compilation failure" in text
    )

    test_indicators = [
        "Tests run:",
        "Failures:",
        "Errors:",
        "Failed tests:",
        "There are test failures",
        "maven-surefire-plugin"
    ]

    test_failure_detected = any(
        indicator in text
        for indicator in test_indicators
    )

    # Collect important lines
    important_lines = []

    keywords = [
        "Tests run:",
        "Failures:",
        "Errors:",
        "Failed tests:",
        "There are test failures",
        "COMPILATION ERROR",
        "BUILD SUCCESS",
        "BUILD FAILURE",
        "Caused by:",
        "AssertionError",
        "Exception"
    ]

    for line in text.splitlines():

        if any(
            keyword.lower() in line.lower()
            for keyword in keywords
        ):
            important_lines.append(line.strip())

    # Keep summary manageable
    important_lines = important_lines[:100]

    if compilation_error:
        evidence_status = "COMPILATION_FAILURE_FOUND"

    elif test_failure_detected and build_failure:
        evidence_status = "TEST_FAILURE_EVIDENCE_FOUND"

    elif build_success:
        evidence_status = "BREAKAGE_NOT_OBSERVED"

    else:
        evidence_status = "NEEDS_MANUAL_REVIEW"

    return {
        "build_success": build_success,
        "build_failure": build_failure,
        "compilation_error": compilation_error,
        "test_failure_detected": test_failure_detected,
        "evidence_status": evidence_status,
        "important_lines": "\n".join(important_lines)
    }


# ---------------------------------------------------------
# Process one case
# ---------------------------------------------------------

for _, row in df.iterrows():

    case_id = row["case_id"]

    print()
    print("==========================================")
    print(f"Project     : {row['project']}")
    print(
        f"Dependency  : "
        f"{row['dependency_group']}:"
        f"{row['dependency_artifact']}"
    )
    print(
        f"Version     : "
        f"{row['previous_version']} "
        f"-> "
        f"{row['new_version']}"
    )
    print(
        f"BUMP label  : "
        f"{row['failure_category']}"
    )
    print("==========================================")

    run_result = run_breaking_image(
        row["breaking_command"],
        case_id
    )

    analysis = analyze_log(
        run_result["log_file"]
    )

    result = {
        "case_id": case_id,
        "project": row["project"],
        "dependency_group": row["dependency_group"],
        "dependency_artifact": row["dependency_artifact"],
        "previous_version": row["previous_version"],
        "new_version": row["new_version"],
        "bump_failure_category": row["failure_category"],

        "docker_exit_code": run_result["exit_code"],
        "duration_seconds": run_result["duration_seconds"],
        "timeout": run_result["timeout"],

        "build_success": analysis["build_success"],
        "build_failure": analysis["build_failure"],

        "compilation_error":
            analysis["compilation_error"],

        "test_failure_detected":
            analysis["test_failure_detected"],

        "evidence_status":
            analysis["evidence_status"],

        "log_file":
            str(run_result["log_file"]),

        "important_log_lines":
            analysis["important_lines"]
    }

    results.append(result)

    pd.DataFrame(results).to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("==========================================")
    print("Evidence collection result")
    print("==========================================")
    print(
        f"Build failure: "
        f"{analysis['build_failure']}"
    )
    print(
        f"Compilation error: "
        f"{analysis['compilation_error']}"
    )
    print(
        f"Test failure evidence: "
        f"{analysis['test_failure_detected']}"
    )
    print(
        f"Evidence status: "
        f"{analysis['evidence_status']}"
    )
    print(
        f"Duration: "
        f"{run_result['duration_seconds']} seconds"
    )
    print()
    print("Important log lines:")
    print("------------------------------------------")
    print(analysis["important_lines"])
    print("------------------------------------------")


print()
print("==========================================")
print("Evidence collection completed")
print("==========================================")
print(f"Results: {OUTPUT_FILE}")
print(f"Logs: {LOG_DIR}")