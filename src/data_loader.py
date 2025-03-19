import os
import re
import pandas as pd
import yaml

# Get the absolute path to the project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load configuration
CONFIG_PATH = os.path.join(BASE_DIR, "configs", "config.yaml")

with open(CONFIG_PATH, "r") as config_file:
    config = yaml.safe_load(config_file)

# Ensure the log file path is absolute
LOG_FILE_PATH = os.path.join(BASE_DIR, config["log_file_path"])

def read_logs():
    """
    Reads the HPC log file, extracts relevant fields, and returns a DataFrame.
    """
    log_data = []

    if not os.path.exists(LOG_FILE_PATH):
        raise FileNotFoundError(f"Log file not found: {LOG_FILE_PATH}")

    with open(LOG_FILE_PATH, "r") as file:
        for line in file:
            match = re.match(r'(\d+) (\S+) (\S+) (\S+) (\d+) (\d+) (.+)', line.strip())
            if match:
                log_data.append(match.groups())

    columns = ["ID", "Node", "Subsystem", "Event", "Timestamp", "Unknown", "Message"]
    log_df = pd.DataFrame(log_data, columns=columns)

    # Convert timestamp to human-readable format
    log_df["Timestamp"] = pd.to_datetime(log_df["Timestamp"].astype(int), unit="s", errors="coerce")

    return log_df

if __name__ == "__main__":
    df = read_logs()
    print(df.head())  # Display first 5 rows for testing
