
import re
import csv
from pathlib import Path

# Find the main DRISHTI project directory
BASE_DIR = Path(__file__).resolve().parent.parent

LOG_FILE = BASE_DIR / "logs" / "application.log"
OUTPUT_FILE = BASE_DIR / "logs" / "log_features.csv"


# Each event category is represented separately.
EVENT_CATEGORIES = [
    "database",
    "prediction",
    "memory",
    "inference",
    "latency",
    "authentication",
    "model",
    "api",
    "other"
]


def parse_log_line(line):

    # Separate timestamp and message
    parts = line.strip().split(" | ", 1)

    if len(parts) != 2:
        return None

    timestamp, message = parts

    message = message.upper()

    # Identify severity
    if "CRITICAL" in message:
        severity = "CRITICAL"
    elif "ERROR" in message:
        severity = "ERROR"
    elif "WARNING" in message:
        severity = "WARNING"
    elif "INFO" in message:
        severity = "INFO"
    else:
        severity = "UNKNOWN"

    # Identify event category
    category = "other"

    if "DATABASE" in message:
        category = "database"
    elif "PREDICTION" in message:
        category = "prediction"
    elif "MEMORY" in message:
        category = "memory"
    elif "INFERENCE" in message:
        category = "inference"
    elif "LATENCY" in message:
        category = "latency"
    elif "AUTHENTICATED" in message:
        category = "authentication"
    elif "MODEL" in message:
        category = "model"
    elif "API" in message:
        category = "api"

    return timestamp, severity, category, message


def extract_features(timestamp, severity, category, message):

    # One-hot encode severity and event category.
    features = {
        "severity_INFO": int(severity == "INFO"),
        "severity_WARNING": int(severity == "WARNING"),
        "severity_ERROR": int(severity == "ERROR"),
        "severity_CRITICAL": int(severity == "CRITICAL"),
    }

    for event in EVENT_CATEGORIES:
        features[f"event_{event}"] = int(category == event)

    # Additional indicators for specific problems
    features["is_timeout"] = int("TIMEOUT" in message)
    features["is_failed"] = int("FAILED" in message)
    features["is_high_usage"] = int("HIGH" in message or "EXCEEDED" in message)

    # This label is for demonstration/evaluation only.
    # It will NOT be used to train our unsupervised detector.
    expected_label = int(
        severity in ["ERROR", "CRITICAL", "WARNING"]
    )

    return {
        "timestamp": timestamp,
        **features,
        "expected_label": expected_label
    }


def process_logs():

    if not LOG_FILE.exists():
        raise FileNotFoundError(f"Log file not found: {LOG_FILE}")

    records = []

    with open(LOG_FILE, "r", encoding="utf-8") as file:

        for line in file:

            parsed = parse_log_line(line)

            if parsed is None:
                continue

            timestamp, severity, category, message = parsed

            record = extract_features(
                timestamp,
                severity,
                category,
                message
            )

            records.append(record)

    if not records:
        raise ValueError("No valid log entries were found.")

    # Write processed features to CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=records[0].keys()
        )

        writer.writeheader()
        writer.writerows(records)

    try:
        from integration.metrics import record_batch_logs
        record_batch_logs(total_logs=len(records), anomalies=0, project_id="system_logs")
    except Exception:
        pass

    print("\n========== DRISHTI LOG PROCESSOR ==========")
    print(f"Raw logs processed: {len(records)}")
    print(f"Numerical features generated: {len(records[0]) - 2}")
    print(f"Output saved: {OUTPUT_FILE}")
    print("\nSample processed record:")
    print(records[0])
    print("\nLog processing completed successfully!")


if __name__ == "__main__":
    process_logs()
