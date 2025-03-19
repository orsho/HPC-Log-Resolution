import os
import time
import yaml
import pandas as pd
from groq import Groq
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

# Initialize the Groq client
client = Groq(api_key=GROQ_API_KEY)


def construct_classification_prompt(log_message):
    """
    Constructs a prompt to determine whether a log message indicates an error.
    """
    return f"""
    You are an expert in log analysis. Your task is to determine whether the following log message indicates an error.

    Log Message: '{log_message}'

    If the message indicates an error, respond with "YES".
    If the message does not indicate an error, respond with "NO".

    Provide only "YES" or "NO" as the response.
    """.strip()


def classify_log_level(log_message):
    """
    Sends a log message to Groq API and classifies it as 'ERROR' or 'OTHER'.
    """
    prompt = construct_classification_prompt(log_message)
    messages = [{"role": "user", "content": prompt}]

    try:
        chat_completion = client.chat.completions.create(
            model="llama3-70b-8192",  # Change model if needed
            messages=messages,
            max_tokens=10,
        )
        response = chat_completion.choices[0].message.content.strip() if chat_completion.choices else "Error"
        return "ERROR" if response == "YES" else "OTHER"

    except Exception as e:
        return f"Error querying Groq API: {str(e)}"


if __name__ == "__main__":
    # Load logs
    df = read_logs()

    # Parse logs using Drain3
    df = parse_logs(df)

    # Clean log templates
    df["Cleaned_Message"] = df["Message_After_Drain"].apply(clean_template)

    # Extract unique log messages for classification
    unique_log_df = df[["Cleaned_Message"]].drop_duplicates().reset_index(drop=True)

    # Classify only unique messages
    unique_log_df["log_level"] = unique_log_df["Cleaned_Message"].apply(classify_log_level)

    # Merge classification results back to the original dataframe
    df = df.merge(unique_log_df, on="Cleaned_Message", how="left")

    # Print sample results
    print("\nSample Classified Logs:\n" + "-" * 50)
    print(df[["Cleaned_Message", "log_level"]].sample(n=min(5, len(df)), random_state=42))
