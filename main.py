"""
Main Orchestrator for Complete Customer Credit Assessment Process
==================================================================

This orchestrator runs all 4 agents in sequence:
1. Exposure Aggregator Agent - Aggregates customer AR exposure data
2. Risk Scoring Agent - Calculates customer risk scores
3. Limit Setter Agent - Determines credit limits based on risk
4. Audit Logger Agent - Creates final audit trail

Author: System Orchestrator
Date: January 11, 2026
"""

import logging
import os
from pathlib import Path
from agents.exposure_aggregator_agent import ExposureAggregatorAgent
from agents.risk_scoring_agent import RiskScoringAgent
from agents.limit_setter_agent import LimitSetterAgent
from agents.merger_agent import MergerAgent
from agents.audit_logger_agent import AuditLoggerAgent
from config import settings


def setup_logging():
    """Configure logging to output to both console and a file"""
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
        handlers=[
            logging.FileHandler(settings.LOG_FILE, mode='w'),  # Overwrite log file on each run
            logging.StreamHandler()
        ]
    )


def main():
    """
    Main function to orchestrate the complete credit assessment workflow.
    It runs all agents in a logical sequence to produce the final audit trail.
    """
    setup_logging()
    logger = logging.getLogger("WorkflowOrchestrator")
    
    logger.info("="*80)
    logger.info("=== STARTING COMPLETE CUSTOMER CREDIT ASSESSMENT PROCESS ===")
    logger.info("="*80)
    logger.info("")
    logger.info("Workflow Sequence:")
    logger.info("  1. Exposure Aggregator Agent")
    logger.info("  2. Risk Scoring Agent")
    logger.info("  3. Limit Setter Agent")
    logger.info("  4. Merger Agent")
    logger.info("  5. Audit Logger Agent")
    logger.info("")
    logger.info("="*80)
    
    # --- STAGE 1: Run the Exposure Aggregator Agent ---
    logger.info("\n>>> STAGE 1: EXECUTING EXPOSURE AGGREGATOR AGENT...")
    exposure_agent = ExposureAggregatorAgent()
    if not exposure_agent.run():
        logger.error(">>> STAGE 1 FAILED. Workflow terminated.")
        return False
    logger.info(">>> STAGE 1: EXPOSURE AGGREGATOR AGENT FINISHED.\n")
    
    # --- STAGE 2: Run the Risk Scoring Agent ---
    logger.info(">>> STAGE 2: EXECUTING RISK SCORING AGENT...")
    risk_agent = RiskScoringAgent()
    if not risk_agent.run():
        logger.error(">>> STAGE 2 FAILED. Workflow terminated.")
        return False
    logger.info(">>> STAGE 2: RISK SCORING AGENT FINISHED.\n")
    
    # --- STAGE 3: Run the Limit Setter Agent ---
    logger.info(">>> STAGE 3: EXECUTING LIMIT SETTER AGENT...")
    limit_agent = LimitSetterAgent()
    limit_agent.run()
    logger.info(">>> STAGE 3: LIMIT SETTER AGENT FINISHED.\n")
    
    # --- STAGE 4: Run the Merger Agent ---
    logger.info(">>> STAGE 4: EXECUTING MERGER AGENT to create unified log...")
    merger = MergerAgent()
    merger.run()
    logger.info(">>> STAGE 4: MERGER AGENT FINISHED.\n")
    
    # --- STAGE 5: Run the Audit Logger Agent ---
    logger.info(">>> STAGE 5: EXECUTING AUDIT LOGGER AGENT...")
    audit_agent = AuditLoggerAgent()
    audit_agent.run()
    logger.info(">>> STAGE 5: AUDIT LOGGER AGENT FINISHED.\n")
    
    logger.info("="*80)
    logger.info("=== WORKFLOW FINISHED. ALL STAGES EXECUTED SUCCESSFULLY ===")
    logger.info("="*80)
    logger.info("")
    logger.info("Output Files:")
    logger.info(f"  - Exposure Report: {settings.EXPOSURE_REPORT_OUTPUT_FILE}")
    logger.info(f"  - Risk Scores: {settings.RISK_SCORE_OUTPUT_FILE}")
    logger.info(f"  - Credit Limits: {settings.OUTPUT_FILE}")
    logger.info(f"  - Unified Log: {settings.UNIFIED_LOG_FILE}")
    logger.info(f"  - Audit Trail: {settings.AUDIT_TRAIL_FILE}")
    logger.info(f"  - System Log: {settings.LOG_FILE}")
    logger.info("")
    logger.info("="*80)
    
    return True


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
