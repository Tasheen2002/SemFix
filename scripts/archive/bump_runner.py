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
OUTPUT_FILE = BASE_DIR / "results" / "bump_docker_results.csv"
LOG_DIR = BASE_DIR / "logs"

# For the first test, process only 3 cases.
MAX_CASES = 3

# Some BUMP projects can take around 20 minutes.
# Start with 45 minutes per image.
TIMEOUT_SECONDS = 45 * 60


# ---------------------------------------------------------
# Setup
# ---------------------------------------------------------

LOG_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

print(f"Available TEST_FAILURE candidates: {len(df)}")

# Only first 3 for initial testing
df = df.head(MAX_CASES)

results = []


# ---------------------------------------------------------
# Helper: run one Docker image
# ---------------------------------------------------------

def run_docker_image(command, case_id, image_type):

    short_id = case_id[:8]

    log_file = LOG_DIR / f"{short_id}_{image_type}.log"

    # Original BUMP command looks like:
    # docker run ghcr.io/...
    #
    # We insert --rm so the container is automatically deleted.

    command_parts = command.split()

    if len(command_parts) >= 3:
        command_parts.insert(2, "--rm")

    print()
    print("----------------------------------------")
    print(f"Case       : {case_id}")
    print(f"Image type : {image_type}")
    print(f"Log file   : {log_file}")
    print("----------------------------------------")

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
            "log_file": str(log_file),
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
            "log_file": str(log_file),
        }


# ---------------------------------------------------------
# Helper: inspect Maven result
# ---------------------------------------------------------

def detect_build_result(log_path):

    try:
        text = Path(log_path).read_text(
            encoding="utf-8",
            errors="ignore"
        )

        if "BUILD SUCCESS" in text:
            return "BUILD_SUCCESS"

        if "BUILD FAILURE" in text:
            return "BUILD_FAILURE"

        return "UNKNOWN"

    except Exception:
        return "LOG_READ_ERROR"


# ---------------------------------------------------------
# Process cases
# ---------------------------------------------------------

for _, row in df.iterrows():

    case_id = row["case_id"]

    print()
    print("========================================")
    print(f"Processing case: {case_id}")
    print(f"Project: {row['project']}")
    print(
        f"Dependency: "
        f"{row['dependency_group']}:"
        f"{row['dependency_artifact']}"
    )
    print(
        f"Version: "
        f"{row['previous_version']} "
        f"-> "
        f"{row['new_version']}"
    )
    print("========================================")

    # -----------------------------------------------------
    # PRE image
    # -----------------------------------------------------

    pre_result = run_docker_image(
        row["pre_command"],
        case_id,
        "pre"
    )

    pre_build = detect_build_result(
        pre_result["log_file"]
    )

    print(
        f"PRE result: "
        f"{pre_build}, "
        f"exit={pre_result['exit_code']}, "
        f"time={pre_result['duration_seconds']}s"
    )

    # -----------------------------------------------------
    # BREAKING image
    # -----------------------------------------------------

    breaking_result = run_docker_image(
        row["breaking_command"],
        case_id,
        "breaking"
    )

    breaking_build = detect_build_result(
        breaking_result["log_file"]
    )

    print(
        f"BREAKING result: "
        f"{breaking_build}, "
        f"exit={breaking_result['exit_code']}, "
        f"time={breaking_result['duration_seconds']}s"
    )

    # -----------------------------------------------------
    # Initial reproduction classification
    # -----------------------------------------------------

    if pre_result["timeout"] or breaking_result["timeout"]:

        reproduction_status = "TIMEOUT"

    elif pre_build != "BUILD_SUCCESS":

        reproduction_status = "INVALID_PRE_BASELINE"

    elif breaking_result["exit_code"] == 0:

        reproduction_status = "BREAKAGE_NOT_REPRODUCED"

    else:

        reproduction_status = "TEST_FAILURE_REPRODUCED"

    # -----------------------------------------------------
    # Store result
    # -----------------------------------------------------

    result = {
        "case_id": case_id,
        "project": row["project"],

        "dependency_group":
            row["dependency_group"],

        "dependency_artifact":
            row["dependency_artifact"],

        "previous_version":
            row["previous_version"],

        "new_version":
            row["new_version"],

        "failure_category":
            row["failure_category"],

        "pre_build_result":
            pre_build,

        "pre_exit_code":
            pre_result["exit_code"],

        "pre_duration_seconds":
            pre_result["duration_seconds"],

        "breaking_build_result":
            breaking_build,

        "breaking_exit_code":
            breaking_result["exit_code"],

        "breaking_duration_seconds":
            breaking_result["duration_seconds"],

        "reproduction_status":
            reproduction_status,

        "pre_log":
            pre_result["log_file"],

        "breaking_log":
            breaking_result["log_file"],
    }

    results.append(result)

    # Save after every case
    # so results are not lost if the script stops later.

    pd.DataFrame(results).to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"Reproduction status: "
        f"{reproduction_status}"
    )

    print(
        f"Results saved to: {OUTPUT_FILE}"
    )


print()
print("========================================")
print("Initial Docker experiment completed")
print("========================================")
print(f"Cases processed: {len(results)}")
print(f"Results file: {OUTPUT_FILE}")
print(f"Logs directory: {LOG_DIR}")