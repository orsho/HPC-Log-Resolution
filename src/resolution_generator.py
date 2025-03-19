import os
import pandas as pd
import yaml
from groq import Groq
from log_classifier import classify_log_level
from log_parser import parse_logs, clean_template
from data_loader import read_logs

# Get the absolute path to the project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load configuration
CONFIG_PATH = os.path.join(BASE_DIR, "configs", "config.yaml")
with open(CONFIG_PATH, "r") as config_file:
    config = yaml.safe_load(config_file)

# Set API Key
GROQ_API_KEY = config["groq_api_key"]

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)


def construct_hpc_prompt(error_message):
    """
    Constructs a prompt to analyze an HPC error message and suggest resolutions.
    """
    return f"""
    You are an expert in high-performance computing (HPC) system troubleshooting.
    Given the following HPC error log message: '{error_message}', analyze possible causes first and then suggest precise remediation steps.

    **Issue Summary:**
    [Provide a concise summary of the issue]

    **Possible Causes:**
    - [List relevant causes based on the issue]

    **Resolution Steps:**
    - [List necessary steps to resolve the issue]

    Provide your response in the exact format above. Ensure the resolution steps are clear and actionable.
    """.strip()


def get_hpc_resolution(error_message):
    """
    Queries the Groq API to generate an HPC error resolution.
    """
    prompt = construct_hpc_prompt(error_message)
    messages = [{"role": "user", "content": prompt}]

    try:
        chat_completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            max_tokens=700,
        )

        return chat_completion.choices[
            0].message.content if chat_completion.choices else "Error: No response generated."

    except Exception as e:
        return f"Error querying Groq API: {str(e)}"


if __name__ == "__main__":
    # Load logs
    df = read_logs()

    # Parse logs using Drain3
    df = parse_logs(df)

    # Clean log templates
    df["Cleaned_Message"] = df["Message_After_Drain"].apply(clean_template)

    unique_log_df = df[["Cleaned_Message"]].drop_duplicates().reset_index(drop=True)

    # Classify logs
    unique_log_df["log_level"] = unique_log_df["Cleaned_Message"].apply(classify_log_level)

    # Filter only error logs
    error_log_df = unique_log_df[unique_log_df["log_level"] == "ERROR"].copy()

    # Apply resolution generation
    error_log_df["Resolution_Steps"] = error_log_df["Cleaned_Message"].apply(get_hpc_resolution)

    # Sample 2 random error messages and print in a formatted way
    sample_size = min(2, len(error_log_df))
    sampled_errors = error_log_df.sample(n=sample_size, random_state=42)

    print("\n🔍 Sample Error Logs with Resolutions:\n" + "=" * 80)
    for _, row in sampled_errors.iterrows():
        print(f"Log Message: {row['Cleaned_Message']}\n")
        print(f"Suggested Resolution: {row['Resolution_Steps']}\n")
        print("=" * 80)
