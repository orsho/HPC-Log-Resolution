# HPC Log Analysis & Resolution Pipeline

### Overview

This project builds an end-to-end pipeline for analyzing HPC (High-Performance Computing) logs, identifying errors, and generating automated remediation steps using AI-driven classification and resolution generation.


### Key Features:

Log Parsing: Extracts structured information from HPC logs using Drain3.

Log Classification: Identifies errors using LLM-powered classification (Groq API).

Error Resolution: Provides actionable resolutions using AI-generated troubleshooting steps.

Automated Pipeline: Fully orchestrated workflow from log ingestion to remediation generation.


### Setup & Installation

1️⃣ Clone the Repository

```
git clone https://github.com/your-username/HPC-Log-Resolution.git
cd HPC-Log-Resolution
```

2️⃣ Set Up Virtual Environment (Optional, Recommended)

```
python -m venv venv  # Create virtual environment
source venv/bin/activate  # Activate (Mac/Linux)
venv\Scripts\activate  # Activate (Windows)
```

3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

4️⃣ Configure API Keys & Paths

Modify configs/config.yaml:

```
log_file_path: "data/HPC.log"
groq_api_key: "your_actual_api_key_here" 
```

Replace your_actual_api_key_here with your Groq API key.

Ensure data/HPC.log exists. If missing, create sample logs.


### Running the Full Pipeline

To execute the entire pipeline and generate structured logs with remediation steps:

```
python src/pipeline.py
```

The processed logs will be saved in: results/processed_logs.csv

The pipeline will print sample logs and their AI-generated resolutions.
