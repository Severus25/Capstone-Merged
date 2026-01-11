"""
Exposure Aggregator Agent
==========================
Agent that aggregates customer exposure data from multiple sources.
Refactored for integration with multi-agent workflow.

Author: Exposure Aggregator Agent
Date: January 11, 2026
Agent ID: ExposureAggregator01
"""

import json
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from openai import AzureOpenAI
from config import settings


class ExposureAggregatorAgent:
    """Exposure Aggregator Agent - Aggregates customer AR exposure data"""
    
    def __init__(self, agent_id: str = "ExposureAggregator01"):
        self.agent_id = agent_id
        self.timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self.logger = logging.getLogger(self.agent_id)
        self.customers = {}
        self.customer_names = {}
        self.invoice_details = []
        self.report_data = []
        
        # Initialize Azure OpenAI client if configured
        try:
            if settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT:
                self.llm_client = AzureOpenAI(
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION,
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
                )
                self.engine = settings.AZURE_OPENAI_DEPLOYMENT_NAME
                self.llm_enabled = True
                self.logger.info("Azure OpenAI initialized successfully")
            else:
                self.llm_enabled = False
                self.logger.warning("Azure OpenAI not configured")
        except Exception as e:
            self.logger.warning(f"Azure OpenAI initialization failed: {e}")
            self.llm_enabled = False
    
    def _perceive(self):
        """Perception phase: Load input data sources"""
        self.logger.info("Perception phase: Loading data sources...")
        try:
            # Load customer list
            self.logger.info(f"Loading customer list from {settings.CUSTOMER_LIST_FILE}...")
            self.load_customer_list(str(settings.CUSTOMER_LIST_FILE))
            
            # Load JSON AR extract
            self.logger.info(f"Loading JSON AR extract from {settings.JSON_EXTRACT_FILE}...")
            self.load_json_data(str(settings.JSON_EXTRACT_FILE))
            
            # Load CSV AR records
            self.logger.info(f"Loading CSV AR records from {settings.CSV_RECORDS_FILE}...")
            self.load_csv_data(str(settings.CSV_RECORDS_FILE))
            
            self.logger.info("Successfully loaded all data sources.")
            return True
        except Exception as e:
            self.logger.error(f"Error in perception phase: {e}")
            return False
    
    def load_customer_list(self, filepath: str) -> None:
        """Load customer ID list with names and countries"""
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                customer_id = row['CUSTOMER_ID']
                self.customer_names[customer_id] = {
                    'name': row['NAME'],
                    'country': row['COUNTRY']
                }
                if customer_id not in self.customers:
                    self.customers[customer_id] = 0.0
    
    def load_json_data(self, filepath: str) -> None:
        """Load AR data from JSON extract"""
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        for record in data['records']:
            customer_id = record['CUSTOMER_ID']
            amount = record['AMOUNT']
            
            if customer_id not in self.customers:
                self.customers[customer_id] = 0.0
            
            self.customers[customer_id] += amount
            self.invoice_details.append(record)
    
    def load_csv_data(self, filepath: str) -> None:
        """Load AR data from CSV records"""
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                customer_id = row['CUSTOMER_ID']
                amount = float(row['AMOUNT'])
                
                if customer_id not in self.customers:
                    self.customers[customer_id] = 0.0
                
                self.customers[customer_id] += amount
                self.invoice_details.append(dict(row))
    
    def validate_record(self, customer_id: str, total_amount: float) -> str:
        """Validate aggregated record"""
        if total_amount > 0:
            return "PASS"
        return "FAIL"
    
    def _reason(self) -> List[Dict]:
        """Reasoning phase: Generate aggregated exposure report"""
        self.logger.info("Reasoning phase: Aggregating exposure data...")
        
        report = []
        for customer_id in sorted(self.customers.keys()):
            total_amount = round(self.customers[customer_id], 2)
            validation_status = self.validate_record(customer_id, total_amount)
            
            customer_info = self.customer_names.get(customer_id, {})
            
            report.append({
                'customer_id': customer_id,
                'customer_name': customer_info.get('name', 'Unknown'),
                'country': customer_info.get('country', 'Unknown'),
                'total_open_AR': total_amount,
                'currency': 'USD',
                'validation_status': validation_status,
                'timestamp': self.timestamp,
                'agent_id': self.agent_id
            })
        
        self.report_data = report
        
        # Calculate statistics
        total_exposure = sum(r['total_open_AR'] for r in report)
        avg_exposure = total_exposure / len(report) if report else 0
        
        self.logger.info(f"Generated report for {len(report)} customers")
        self.logger.info(f"Total Exposure: ${total_exposure:,.2f}")
        self.logger.info(f"Average Exposure: ${avg_exposure:,.2f}")
        
        return report
    
    def _act(self, report: List[Dict]) -> bool:
        """Action phase: Save exposure report to output files"""
        self.logger.info("Action phase: Saving exposure report...")
        try:
            # Save JSON report (for next agent)
            json_path = settings.EXPOSURE_REPORT_OUTPUT_FILE
            Path(json_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Format for next agent (risk scoring)
            output_data = []
            for row in report:
                output_data.append({
                    'customer_id': row['customer_id'],
                    'total_open_AR': row['total_open_AR'],
                    'currency': row['currency'],
                    'validation_status': row['validation_status'],
                    'timestamp': row['timestamp'],
                    'agent_id': row['agent_id']
                })
            
            with open(json_path, 'w') as f:
                json.dump(output_data, f, indent=4)
            
            self.logger.info(f"JSON report saved: {json_path}")
            
            # Save CSV report (optional)
            csv_path = str(Path(json_path).parent / "exposure_report.csv")
            fieldnames = ['customer_id', 'total_open_AR', 'currency', 
                         'validation_status', 'timestamp', 'agent_id']
            
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in output_data:
                    writer.writerow(row)
            
            self.logger.info(f"CSV report saved: {csv_path}")
            
            # Generate AI insights if enabled
            if self.llm_enabled:
                self._generate_ai_insights(report)
            
            return True
        except Exception as e:
            self.logger.error(f"Error in action phase: {e}")
            return False
    
    def _generate_ai_insights(self, report: List[Dict]):
        """Generate AI-powered insights (optional)"""
        try:
            self.logger.info("Generating AI insights...")
            
            total_exposure = sum(r['total_open_AR'] for r in report)
            avg_exposure = total_exposure / len(report) if report else 0
            top_5_customers = sorted(report, key=lambda x: x['total_open_AR'], reverse=True)[:5]
            
            overdue_count = sum(1 for inv in self.invoice_details if inv.get('STATUS') == 'OVERDUE')
            total_invoices = len(self.invoice_details)
            
            context = f"""
            Customer Exposure Report Analysis:
            - Total Customers: {len(report)}
            - Total Exposure: ${total_exposure:,.2f}
            - Average Exposure per Customer: ${avg_exposure:,.2f}
            - Total Invoices: {total_invoices}
            - Overdue Invoices: {overdue_count}
            
            Top 5 Customers by Exposure:
            {json.dumps([{k: v for k, v in c.items() if k in ['customer_id', 'customer_name', 'total_open_AR']} for c in top_5_customers], indent=2)}
            """
            
            prompt = f"""Based on the following customer exposure data, generate a concise executive summary. Include overall financial position, key risk factors, and recommended actions.

Data:
{context}

Provide a professional summary in 200-300 words."""
            
            response = self.llm_client.chat.completions.create(
                model=self.engine,
                messages=[
                    {"role": "system", "content": "You are a financial analyst specializing in credit risk and accounts receivable management."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            insights = {
                "agent_id": self.agent_id,
                "timestamp": self.timestamp,
                "executive_summary": response.choices[0].message.content.strip(),
                "statistics": {
                    "total_customers": len(report),
                    "total_exposure": total_exposure,
                    "average_exposure": avg_exposure,
                    "total_invoices": total_invoices,
                    "overdue_invoices": overdue_count
                }
            }
            
            insights_path = str(Path(settings.EXPOSURE_REPORT_OUTPUT_FILE).parent / "ai_insights.json")
            with open(insights_path, 'w') as f:
                json.dump(insights, f, indent=4)
            
            self.logger.info(f"AI insights saved: {insights_path}")
        except Exception as e:
            self.logger.warning(f"Failed to generate AI insights: {e}")
    
    def run(self):
        """Main execution method following PAR-A pattern"""
        self.logger.info("="*60)
        self.logger.info(f"=== STARTING {self.agent_id} ===")
        self.logger.info("="*60)
        
        # Perceive
        if not self._perceive():
            self.logger.error("Perception phase failed. Terminating.")
            return False
        
        # Reason
        report = self._reason()
        if not report:
            self.logger.error("Reasoning phase failed. Terminating.")
            return False
        
        # Act
        if not self._act(report):
            self.logger.error("Action phase failed. Terminating.")
            return False
        
        self.logger.info("="*60)
        self.logger.info(f"=== {self.agent_id} COMPLETED SUCCESSFULLY ===")
        self.logger.info("="*60)
        
        return True
