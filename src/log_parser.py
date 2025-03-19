import os
import pandas as pd
import re
import random
from drain3 import TemplateMiner
from data_loader import read_logs

# Initialize Drain3 log parser
template_miner = TemplateMiner()


def parse_logs(log_df):
    """
    Parses log messages using Drain3 and extracts structured templates.
    """
    log_templates = []

    for original in log_df["Message"]:
        result = template_miner.add_log_message(original)
        log_templates.append({
            "Cluster_ID": result["cluster_id"],
            "Message_After_Drain": result["template_mined"]
        })

    parsed_df = pd.DataFrame(log_templates)
    log_df = pd.concat([log_df, parsed_df], axis=1)

    return log_df


def clean_template(template):
    """
    Cleans and standardizes log templates by:
    - Removing hexadecimal numbers (e.g., 0x1fffffffe)
    - Replacing node IDs (e.g., node-254 → node-xxx)
    - Generalizing standalone numbers (e.g., 'error code 1234' → 'error code xxx')
    """
    if pd.isna(template):
        return ""

    template = re.sub(r'0x[0-9a-fA-F]+', '', template)  # Remove hex numbers
    template = re.sub(r'node-(\d+)', 'node-xxx', template, flags=re.IGNORECASE)  # Generalize node IDs
    template = re.sub(r'\b\d+\b', 'xxx', template)  # Replace numbers with 'xxx'
    template = re.sub(r'\b([a-zA-Z]+)(\d+)\b', r'\1-xxx', template)  # Normalize alphanumeric words

    return template.strip()


if __name__ == "__main__":
    # Load logs
    df = read_logs()

    # Parse logs using Drain3
    df = parse_logs(df)

    # Clean log templates
    df["Cleaned_Message"] = df["Message_After_Drain"].apply(clean_template)

    # Randomly sample 5 examples from Cleaned_Message
    sample_size = min(5, len(df))  # Ensure at least 5 exist
    sampled_messages = df["Cleaned_Message"].sample(n=sample_size, random_state=42)

    # Print the 5 sampled cleaned messages
    print("\nRandomly Sampled Cleaned Log Messages:\n" + "-" * 50)
    for i, message in enumerate(sampled_messages, 1):
        print(f"{i}. {message}\n")
