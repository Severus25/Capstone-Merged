"""
Configuration settings for Complete Customer Credit Assessment System
Integrates all 4 agents: Exposure Aggregator -> Risk Scoring -> Limit Setter -> Audit Logger
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Load environment variables
dotenv_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=dotenv_path)

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# ==================== INPUT DATA PATHS ====================

# Agent 1 (Exposure Aggregator) - Input Files
CUSTOMER_LIST_FILE = BASE_DIR / 'data' / 'input' / 'customer_id_list.csv'
JSON_EXTRACT_FILE = BASE_DIR / 'data' / 'input' / 'ERP_AR_extract.json'
CSV_RECORDS_FILE = BASE_DIR / 'data' / 'input' / 'open_AR_records_sample.csv'

# Agent 2 (Risk Scoring) - Input Files
PAYMENT_HISTORY_FILE = BASE_DIR / 'data' / 'input' / 'payment_history.csv'
CREDIT_BUREAU_FILE = BASE_DIR / 'data' / 'input' / 'credit_bureau_api_response.json'

# Agent 3 (Limit Setter) - Input Files
ERP_CUSTOMER_FILE = BASE_DIR / 'data' / 'input' / 'ERP_customer_master.json'
CREDIT_POLICY_FILE = BASE_DIR / 'config' / 'credit_policy_rules.json'

# ==================== INTERMEDIATE OUTPUT PATHS ====================

# Agent 1 Output -> Agent 2 Input
EXPOSURE_REPORT_OUTPUT_FILE = BASE_DIR / 'data' / 'output' / 'exposure_report.json'
EXPOSURE_REPORT_FILE = EXPOSURE_REPORT_OUTPUT_FILE  # Alias for compatibility

# Agent 2 Output -> Agent 3 Input
RISK_SCORE_OUTPUT_FILE = BASE_DIR / 'data' / 'output' / 'risk_score_output.json'
RISK_SCORE_FILE = RISK_SCORE_OUTPUT_FILE  # Alias for compatibility

# Agent 3 Output
OUTPUT_FILE = BASE_DIR / 'data' / 'output' / 'credit_limit_update.json'

# ==================== FINAL OUTPUT PATHS ====================

# Unified log file (created by Merger Agent)
UNIFIED_LOG_FILE = BASE_DIR / 'data' / 'output' / 'all_agents_logs.json'

# Final audit trail (created by Audit Logger Agent)
AUDIT_TRAIL_FILE = BASE_DIR / 'data' / 'output' / 'audit_trail.json'

# ==================== LOGS ====================

LOG_FILE = BASE_DIR / 'logs' / 'agent.log'
