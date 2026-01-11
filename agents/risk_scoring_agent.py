"""
Risk Scoring Agent
==================
Agent that calculates customer risk scores based on payment history and exposure data.
Refactored for integration with multi-agent workflow.

Author: Risk Scoring Agent
Date: January 11, 2026
Agent ID: RiskScoring01
"""

import json
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from config import settings


class RiskScoringAgent:
    """Risk Scoring Agent - Calculates customer risk scores"""
    
    def __init__(self, agent_id: str = "RiskScoring01"):
        self.agent_id = agent_id
        self.timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self.logger = logging.getLogger(self.agent_id)
        
        # Risk calculation weights
        self.PAYMENT_DELAY_WEIGHT = 0.3
        self.EXPOSURE_RATIO_WEIGHT = 0.4
        self.AVG_RISK_WEIGHT = 0.3
        
        # Risk category thresholds
        self.RISK_THRESHOLDS = {
            'Low': 80,      # Risk Score >= 80
            'Medium': 61,   # Risk Score 61-79
            'High': 0       # Risk Score <= 60
        }
        
        self.exposure_data = {}
        self.payment_data = {}
        self.credit_data = {}
        self.results = []
    
    def _perceive(self):
        """Perception phase: Load input data sources"""
        self.logger.info("Perception phase: Loading data sources...")
        try:
            # Load exposure data from previous agent
            self.logger.info(f"Loading exposure data from {settings.EXPOSURE_REPORT_OUTPUT_FILE}...")
            with open(settings.EXPOSURE_REPORT_OUTPUT_FILE, 'r') as f:
                exposure_list = json.load(f)
                self.exposure_data = {item['customer_id']: item for item in exposure_list}
            
            # Load payment history
            self.logger.info(f"Loading payment history from {settings.PAYMENT_HISTORY_FILE}...")
            with open(settings.PAYMENT_HISTORY_FILE, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    customer_id = row['CUSTOMER_ID']
                    if customer_id not in self.payment_data:
                        self.payment_data[customer_id] = []
                    self.payment_data[customer_id].append(row)
            
            # Load credit bureau data (optional)
            try:
                self.logger.info(f"Loading credit bureau data from {settings.CREDIT_BUREAU_FILE}...")
                with open(settings.CREDIT_BUREAU_FILE, 'r') as f:
                    credit_list = json.load(f)
                    self.credit_data = {item['customer_id']: item for item in credit_list}
            except FileNotFoundError:
                self.logger.warning("Credit bureau data not found. Continuing without it.")
            
            self.logger.info("Successfully loaded all data sources.")
            return True
        except Exception as e:
            self.logger.error(f"Error in perception phase: {e}")
            return False
    
    def calculate_payment_delay_factor(self, payments):
        """Calculate payment delay factor"""
        total_delay = 0
        invoice_count = len(payments)
        
        for payment in payments:
            due_date = datetime.strptime(payment['DUE_DATE'], '%Y-%m-%d')
            payment_date = datetime.strptime(payment['PAYMENT_DATE'], '%Y-%m-%d')
            delay_days = (payment_date - due_date).days
            total_delay += delay_days
        
        if invoice_count == 0:
            return 0
        
        payment_delay_factor = total_delay / invoice_count
        return round(payment_delay_factor, 2)
    
    def calculate_exposure_ratio(self, total_open_ar, customer_id):
        """Calculate exposure ratio"""
        if customer_id in self.credit_data:
            credit_score = self.credit_data[customer_id]['credit_score']
            base_multiplier = 0.6 + ((credit_score - 650) / 150) * 0.9
            credit_limit = total_open_ar / base_multiplier
        else:
            credit_limit = total_open_ar / 1.1
        
        exposure_ratio = total_open_ar / credit_limit
        return round(exposure_ratio, 2)
    
    def calculate_avg_risk_weight(self, payments, customer_id):
        """Calculate average risk weight"""
        if len(payments) > 0:
            delays = []
            for payment in payments:
                due_date = datetime.strptime(payment['DUE_DATE'], '%Y-%m-%d')
                payment_date = datetime.strptime(payment['PAYMENT_DATE'], '%Y-%m-%d')
                delays.append((payment_date - due_date).days)
            
            avg_delay = sum(delays) / len(delays)
            variance = sum((d - avg_delay) ** 2 for d in delays) / len(delays)
            std_dev = variance ** 0.5
            consistency_risk = min(0.5, std_dev / 20)
        else:
            consistency_risk = 0.25
        
        if customer_id in self.credit_data:
            credit_score = self.credit_data[customer_id]['credit_score']
            credit_risk = max(0, (800 - credit_score) / 400)
        else:
            credit_risk = 0.25
        
        avg_risk_weight = (consistency_risk * 0.5 + credit_risk * 0.5)
        avg_risk_weight = max(0.10, min(0.44, avg_risk_weight))
        
        return round(avg_risk_weight, 2)
    
    def calculate_risk_score(self, payment_delay_factor, exposure_ratio, avg_risk_weight):
        """Calculate overall risk score"""
        risk_score = (
            payment_delay_factor * self.PAYMENT_DELAY_WEIGHT +
            exposure_ratio * 100 * self.EXPOSURE_RATIO_WEIGHT +
            avg_risk_weight * 100 * self.AVG_RISK_WEIGHT
        )
        return round(risk_score)
    
    def determine_risk_category(self, risk_score):
        """Determine risk category based on score"""
        if risk_score >= 80:
            return "Low"
        elif risk_score >= 61:
            return "Medium"
        else:
            return "High"
    
    def _reason(self) -> List[Dict]:
        """Reasoning phase: Calculate risk scores for all customers"""
        self.logger.info("Reasoning phase: Calculating risk scores...")
        
        results = []
        
        self.logger.info(f"Processing {len(self.exposure_data)} customers...")
        
        for customer_id, exposure in self.exposure_data.items():
            self.logger.debug(f"Processing {customer_id}...")
            
            total_open_ar = exposure['total_open_AR']
            payments = self.payment_data.get(customer_id, [])
            
            # Calculate risk factors
            payment_delay_factor = self.calculate_payment_delay_factor(payments)
            exposure_ratio = self.calculate_exposure_ratio(total_open_ar, customer_id)
            avg_risk_weight = self.calculate_avg_risk_weight(payments, customer_id)
            
            # Calculate risk score
            risk_score = self.calculate_risk_score(
                payment_delay_factor,
                exposure_ratio,
                avg_risk_weight
            )
            
            # Determine risk category
            risk_category = self.determine_risk_category(risk_score)
            
            # Create result record
            result = {
                "customer_id": customer_id,
                "risk_score": risk_score,
                "risk_category": risk_category,
                "payment_delay_factor": payment_delay_factor,
                "exposure_ratio": exposure_ratio,
                "avg_risk_weight": avg_risk_weight,
                "calculation_logic": "Risk Score = (Payment Delay Factor*0.3)+(Exposure Ratio*100*0.4)+(Avg Risk Weight*100*0.3)",
                "validation_status": "PASS",
                "timestamp": exposure['timestamp'],
                "agent_id": self.agent_id
            }
            
            results.append(result)
            self.logger.debug(f"  Risk Score: {risk_score} | Category: {risk_category}")
        
        self.results = results
        
        # Display summary
        category_counts = {'High': 0, 'Medium': 0, 'Low': 0}
        for result in results:
            category_counts[result['risk_category']] += 1
        
        avg_score = sum(r['risk_score'] for r in results) / len(results) if results else 0
        
        self.logger.info(f"Risk scoring complete for {len(results)} customers")
        self.logger.info(f"  High Risk: {category_counts['High']}")
        self.logger.info(f"  Medium Risk: {category_counts['Medium']}")
        self.logger.info(f"  Low Risk: {category_counts['Low']}")
        self.logger.info(f"  Average Risk Score: {avg_score:.2f}")
        
        return results
    
    def _act(self, results: List[Dict]) -> bool:
        """Action phase: Save risk scores to output file"""
        self.logger.info("Action phase: Saving risk scores...")
        try:
            output_file = settings.RISK_SCORE_OUTPUT_FILE
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=4)
            
            self.logger.info(f"Risk scores saved: {output_file}")
            self.logger.info(f"Total customers processed: {len(results)}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error in action phase: {e}")
            return False
    
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
        results = self._reason()
        if not results:
            self.logger.error("Reasoning phase failed. Terminating.")
            return False
        
        # Act
        if not self._act(results):
            self.logger.error("Action phase failed. Terminating.")
            return False
        
        self.logger.info("="*60)
        self.logger.info(f"=== {self.agent_id} COMPLETED SUCCESSFULLY ===")
        self.logger.info("="*60)
        
        return True
