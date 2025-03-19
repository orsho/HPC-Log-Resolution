import os
from data_loader import read_logs
from log_parser import parse_logs, clean_template
from log_classifier import classify_log_level
from resolution_generator import get_hpc_resolution

# Get the absolute path to the project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Ensure results directory exists
RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Define output file
OUTPUT_FILE = os.path.join(RESULTS_DIR, "processed_logs.csv")


def run_pipeline():
    """
    Runs the full pipeline:
    1. Reads logs
    2. Parses logs using Drain3
    3. Cleans log templates
    4. Classifies logs as ERROR or OTHER
    5. Generates resolution steps for ERROR logs
    6. Merges results and saves to CSV
    """

    print("\nRunning HPC Log Analysis Pipeline...\n")

    # Step 1: Load logs
    print("[1/6] Loading logs...")
    df = read_logs()

    # Step 2: Parse logs using Drain3
    print("[2/6] Parsing logs with Drain3...")
    df = parse_logs(df)

    # Step 3: Clean log templates
    print("[3/6] Cleaning log templates...")
    df["Cleaned_Message"] = df["Message_After_Drain"].apply(clean_template)

    # Step 4: Classify logs as ERROR or OTHER
    print("[4/6] Classifying log severity...")
    unique_log_df = df[["Cleaned_Message"]].drop_duplicates().reset_index(drop=True)
    unique_log_df["log_level"] = unique_log_df["Cleaned_Message"].apply(classify_log_level)

    # Step 5: Generate resolutions for ERROR logs
    print("[5/6] Generating resolutions for errors...")
    error_log_df = unique_log_df[unique_log_df["log_level"] == "ERROR"].copy()
    error_log_df["Resolution_Steps"] = error_log_df["Cleaned_Message"].apply(get_hpc_resolution)

    # Step 6: Merge classification and resolution back into the main DataFrame
    print("[6/6] Merging results back into the main dataset...")
    # df = df.merge(unique_log_df, on="Cleaned_Message", how="left")
    df = df.merge(error_log_df[["Cleaned_Message", "log_level", "Resolution_Steps"]], on="Cleaned_Message", how="left")
    df = df.drop(columns=["Cluster_ID", "Message_After_Drain", "Cleaned_Message"])

    # Save processed logs with new columns (log_level and Resolution_Steps)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nPipeline completed! Processed logs saved to: {OUTPUT_FILE}\n")

    return df


if __name__ == "__main__":
    result_df = run_pipeline()

    # Sample 2 random error messages and print in a formatted way
    sample_size = min(2, len(result_df[result_df["log_level"] == "ERROR"]))
    sampled_errors = result_df[result_df["log_level"] == "ERROR"].sample(n=sample_size, random_state=42)

    print("\n🔍 Sample Error Logs with Resolutions:\n" + "=" * 80)
    for _, row in sampled_errors.iterrows():
        print(f"Log Message: {row['Message']}\n")
        print(f"Suggested Resolution: {row['Resolution_Steps']}\n")
        print("=" * 80)
