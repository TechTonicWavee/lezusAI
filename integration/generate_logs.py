
import random
from datetime import datetime
from pathlib import Path

# DRISHTI project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Where application logs will be stored
LOG_FILE = BASE_DIR / "logs" / "application.log"

normal_events = [
    "INFO: Database connected successfully",
    "INFO: Prediction request completed",
    "INFO: User authenticated successfully",
    "INFO: Model loaded successfully",
    "INFO: API request processed"
]

abnormal_events = [
    "ERROR: Database connection timeout",
    "ERROR: Prediction request failed",
    "CRITICAL: Memory usage exceeded limit",
    "ERROR: Model inference failed",
    "WARNING: API response latency too high"
]

def generate_application_logs():

    logs = []

    # Generate 40 normal events
    for _ in range(40):
        event = random.choice(normal_events)
        logs.append(event)

    # Generate 10 abnormal events
    for _ in range(10):
        event = random.choice(abnormal_events)
        logs.append(event)

    # Mix normal and abnormal events
    random.shuffle(logs)

    # Add timestamps
    with open(LOG_FILE, "w", encoding="utf-8") as file:

        for event in logs:
            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            file.write(f"{timestamp} | {event}\n")

    print("DRISHTI AI - Application Simulation")
    print("-----------------------------------")
    print(f"Total logs generated: {len(logs)}")
    print(f"Normal events: 40")
    print(f"Abnormal events: 10")
    print(f"Log file: {LOG_FILE}")

if __name__ == "__main__":
    generate_application_logs()
