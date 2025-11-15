#!/usr/bin/env python3
"""
Compliance Checker for BuryatMyasoprom
Validates export orders against China import regulations
"""

import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComplianceStatus(Enum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    CONDITIONAL = "CONDITIONAL"

class ComplianceChecker:
    def __init__(self, regulations_path: str = "config/china_regulations.yaml"):
        self.regulations = self._load_regulations(regulations_path)
        self.violation_history = []
    
    def _load_regulations(self, regulations_path: str) -> Dict:
        """Load China import regulations from YAML file"""
        base_regulations = {
            "general_requirements": {
                "allowed_meat_types": ["BEEF", "LAMB", "HORSE", "POULTRY"],
                "banned_categories": [
                    "meat_from_quarantine_zones",
                    "meat_with_growth_hormones",
                    "meat_with_antibiotic_residues_above_limit"
                ]
            },
            "temperature_requirements": {
                "frozen_beef": {"min": -18, "max": -15},
                "frozen_lamb": {"min": -18, "max": -15},
                "frozen_horse": {"min": -20, "max": -18},
                "monitoring_frequency": "continuous",
                "allowed_deviation": 0.5
            },
            "documentation_requirements": {
                "mandatory_documents": [
                    "health_certificate",
                    "veterinary_certificate",
                    "certificate_of_origin",
                    "customs_declaration"
                ],
                "conditional_documents": {
                    "organic_products": "organic_certificate",
                    "halal_products": "halal_certificate",
                    "premium_grade": "quality_grade_certificate"
                },
                "validity_periods": {
                    "health_certificate": 30,  # days
                    "veterinary_certificate": 7,
                    "customs_declaration": 15
                }
            },
            "labeling_requirements": {
                "languages": ["chinese", "russian"],
                "required_information": [
                    "product_name",
                    "production_date",
                    "expiry_date",
                    "storage_conditions",
                    "net_weight",
                    "country_of_origin"
                ]
            },
            "testing_requirements": {
                "microbiological_tests": {
                    "salmonella": "absent_in_25g",
                    "listeria": "absent_in_25g",
                    "e_coli": "100_cfu_g"
                },
                "chemical_tests": {
                    "antibiotic_residues": "below_established_limits",
                    "heavy_metals": "below_established_limits"
                }
            }
        }
        
        try:
            with open(regulations_path, 'r') as f:
                user_regulations = yaml.safe_load(f)
                if user_regulations:
                    base_regulations.update(user_regulations)
        except FileNotFoundError:
            logger.warning(f"Regulations file {regulations_path} not found, using defaults")
        
        return base_regulations
    
    def check_order_compliance(self, order_data: Dict) -> Dict:
        """Comprehensive compliance check for export order"""
        violations = []
        warnings = []
        
        # Check product compliance
        product_compliance = self._check_products_compliance(order_data.get("products", []))
        violations.extend(product_compliance["violations"])
        warnings.extend(product_compliance["warnings"])
        
        # Check documentation compliance
        doc_compliance = self._check_documentation_compliance(order_data)
        violations.extend(doc_compliance["violations"])
        warnings.extend(doc_compliance["warnings"])
        
        # Check shipment compliance
        shipment_compliance = self._check_shipment_compliance(order_data.get("shipment", {}))
        violations.extend(shipment_compliance["violations"])
        warnings.extend(shipment_compliance["warnings"])
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(violations, warnings)
        
        result = {
            "compliance_status": ComplianceStatus.COMPLIANT.value if not violations else ComplianceStatus.NON_COMPLIANT.value,
            "compliance_score": compliance_score,
            "violations": violations,
            "warnings": warnings,
            "required_actions": self._generate_required_actions(violations),
            "risk_level": self._assess_risk_level(violations, warnings),
            "checked_at": datetime.now().isoformat(),
            "regulation_version": "2024.1.0"
        }
        
        # Log violation if any
        if violations:
            self._log_violation(order_data.get("order_id", "UNKNOWN"), violations)
        
        return result
    
    def _check_products_compliance(self, products: List[Dict]) -> Dict:
        """Check product-level compliance"""
        violations = []
        warnings = []
        
        for i, product in enumerate(products):
            product_id = f"Product_{i+1}"
            
            # Check meat type
            meat_type = product.get("meat_type", "").upper()
            allowed_types = self.regulations["general_requirements"]["allowed_meat_types"]
            if meat_type not in allowed_types:
                violations.append(f"{product_id}: Meat type '{meat_type}' not allowed for China export")
            
            # Check for banned categories
            if product.get("from_quarantine_zone"):
                violations.append(f"{product_id}: Product from quarantine zone - banned for export")
            
            if product.get("hormones_used"):
                violations.append(f"{product_id}: Growth hormones used - banned for export")
            
            # Check temperature compliance
            temp_status = self._check_temperature_compliance(product)
            if not temp_status["compliant"]:
                violations.extend([f"{product_id}: {v}" for v in temp_status["violations"]])
            warnings.extend([f"{product_id}: {w}" for w in temp_status["warnings"]])
            
            # Check production dates
            date_status = self._check_production_dates(product)
            if not date_status["compliant"]:
                violations.extend([f"{product_id}: {v}" for v in date_status["violations"]])
        
        return {"violations": violations, "warnings": warnings}
    
    def _check_temperature_compliance(self, product: Dict) -> Dict:
        """Check temperature compliance for product"""
        violations = []
        warnings = []
        
        meat_type = product.get("meat_type", "").lower()
        current_temp = product.get("current_temperature")
        
        if current_temp is None:
            warnings.append("No current temperature data available")
            return {"compliant": True, "violations": violations, "warnings": warnings}
        
        # Find temperature requirements
        temp_key = f"frozen_{meat_type}"
        requirements = self.regulations["temperature_requirements"].get(temp_key)
        
        if not requirements:
            warnings.append(f"No specific temperature requirements found for {meat_type}")
            return {"compliant": True, "violations": violations, "warnings": warnings}
        
        min_temp = requirements["min"]
        max_temp = requirements["max"]
        allowed_deviation = self.regulations["temperature_requirements"]["allowed_deviation"]
        
        # Check temperature range
        if current_temp < (min_temp - allowed_deviation) or current_temp > (max_temp + allowed_deviation):
            violations.append(
                f"Temperature {current_temp}°C outside safe range ({min_temp}°C to {max_temp}°C)"
            )
        elif current_temp < min_temp or current_temp > max_temp:
            warnings.append(
                f"Temperature {current_temp}°C approaching limits ({min_temp}°C to {max_temp}°C)"
            )
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings
        }
    
    def _check_production_dates(self, product: Dict) -> Dict:
        """Check production and expiry dates"""
        violations = []
        
        production_date = product.get("production_date")
        expiry_date = product.get("expiry_date")
        
        if not production_date or not expiry_date:
            violations.append("Missing production or expiry date")
            return {"compliant": False, "violations": violations}
        
        try:
            prod_date = datetime.fromisoformat(production_date)
            exp_date = datetime.fromisoformat(expiry_date)
            today = datetime.now()
            
            # Check if production date is in future
            if prod_date > today:
                violations.append("Production date cannot be in the future")
            
            # Check if expired
            if exp_date < today:
                violations.append("Product has expired")
            
            # Check shelf life
            shelf_life = (exp_date - prod_date).days
            max_shelf_life = 365  # days for frozen meat
            
            if shelf_life > max_shelf_life:
                violations.append(f"Shelf life {shelf_life} days exceeds maximum {max_shelf_life} days")
                
        except ValueError:
            violations.append("Invalid date format")
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations
        }
    
    def _check_documentation_compliance(self, order_data: Dict) -> Dict:
        """Check documentation compliance"""
        violations = []
        warnings = []
        
        provided_docs = order_data.get("documents", [])
        mandatory_docs = self.regulations["documentation_requirements"]["mandatory_documents"]
        
        # Check mandatory documents
        for doc_type in mandatory_docs:
            if doc_type not in provided_docs:
                violations.append(f"Missing mandatory document: {doc_type}")
        
        # Check conditional documents
        conditional_docs = self.regulations["documentation_requirements"]["conditional_documents"]
        products = order_data.get("products", [])
        
        for product in products:
            if product.get("organic_certified") and "organic_certificate" not in provided_docs:
                violations.append("Organic certification required for organic products")
            
            if product.get("halal_certified") and "halal_certificate" not in provided_docs:
                violations.append("Halal certification required for halal products")
            
            if product.get("quality_grade") in ["A", "PREMIUM"] and "quality_grade_certificate" not in provided_docs:
                warnings.append("Quality grade certificate recommended for premium products")
        
        # Check document validity
        validity_status = self._check_document_validity(order_data)
        violations.extend(validity_status["violations"])
        warnings.extend(validity_status["warnings"])
        
        return {"violations": violations, "warnings": warnings}
    
    def _check_document_validity(self, order_data: Dict) -> Dict:
        """Check document validity periods"""
        violations = []
        warnings = []
        
        documents = order_data.get("documents_metadata", {})
        validity_periods = self.regulations["documentation_requirements"]["validity_periods"]
        
        for doc_type, validity_days in validity_periods.items():
            if doc_type in documents:
                issue_date = documents[doc_type].get("issue_date")
                if issue_date:
                    try:
                        issue_dt = datetime.fromisoformat(issue_date)
                        expiry_dt = issue_dt + timedelta(days=validity_days)
                        
                        if expiry_dt < datetime.now():
                            violations.append(f"{doc_type} has expired")
                        elif (expiry_dt - datetime.now()).days < 3:
                            warnings.append(f"{doc_type} expiring in {(expiry_dt - datetime.now()).days} days")
                    except ValueError:
                        warnings.append(f"Invalid issue date format for {doc_type}")
        
        return {"violations": violations, "warnings": warnings}
    
    def _check_shipment_compliance(self, shipment_data: Dict) -> Dict:
        """Check shipment compliance"""
        violations = []
        warnings = []
        
        if not shipment_data:
            violations.append("Missing shipment information")
            return {"violations": violations, "warnings": warnings}
        
        # Check port of entry
        port_of_entry = shipment_data.get("port_of_entry", "").lower()
        valid_ports = ["manzhouli", "suifenhe", "dalian", "tianjin"]
        
        if port_of_entry and port_of_entry not in valid_ports:
            warnings.append(f"Unusual port of entry: {port_of_entry}")
        
        # Check transport method
        transport_method = shipment_data.get("transport_method", "").upper()
        valid_methods = ["REFRIGERATED_TRUCK", "REFRIGERATED_CONTAINER"]
        
        if transport_method not in valid_methods:
            violations.append(f"Invalid transport method for meat: {transport_method}")
        
        # Check insurance
        insurance_value = shipment_data.get("insurance_value", 0)
        if insurance_value <= 0:
            warnings.append("No insurance value specified")
        
        return {"violations": violations, "warnings": warnings}
    
    def _calculate_compliance_score(self, violations: List[str], warnings: List[str]) -> float:
        """Calculate compliance score (0-100)"""
        base_score = 100.0
        
        # Deduct for violations
        violation_penalty = 10.0  # per violation
        base_score -= len(violations) * violation_penalty
        
        # Deduct for warnings
        warning_penalty = 2.0  # per warning
        base_score -= len(warnings) * warning_penalty
        
        return max(0.0, base_score)
    
    def _assess_risk_level(self, violations: List[str], warnings: List[str]) -> str:
        """Assess overall risk level"""
        total_issues = len(violations) + len(warnings)
        
        if violations:
            return "HIGH"
        elif total_issues >= 3:
            return "MEDIUM"
        elif total_issues >= 1:
            return "LOW"
        else:
            return "VERY_LOW"
    
    def _generate_required_actions(self, violations: List[str]) -> List[str]:
        """Generate required actions based on violations"""
        actions = []
        
        for violation in violations:
            if "temperature" in violation.lower():
                actions.append("Adjust storage temperature to required range")
            elif "missing document" in violation.lower():
                doc_name = violation.split(":")[-1].strip()
                actions.append(f"Prepare and include {doc_name}")
            elif "expired" in violation.lower():
                actions.append("Renew expired documents")
            elif "banned" in violation.lower():
                actions.append("Remove banned products from shipment")
        
        return actions
    
    def _log_violation(self, order_id: str, violations: List[str]):
        """Log compliance violations for auditing"""
        violation_record = {
            "order_id": order_id,
            "timestamp": datetime.now().isoformat(),
            "violations": violations,
            "resolved": False
        }
        
        self.violation_history.append(violation_record)
        logger.warning(f"Compliance violations detected for order {order_id}: {violations}")
    
    def get_compliance_history(self, days: int = 30) -> List[Dict]:
        """Get compliance violation history"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        return [
            record for record in self.violation_history
            if datetime.fromisoformat(record["timestamp"]) >= cutoff_date
        ]
    
    def generate_compliance_report(self, order_data: Dict) -> Dict:
        """Generate comprehensive compliance report"""
        compliance_check = self.check_order_compliance(order_data)
        
        report = {
            "order_id": order_data.get("order_id"),
            "compliance_summary": compliance_check,
            "regulation_references": self._get_relevant_regulations(order_data),
            "recommendations": self._generate_compliance_recommendations(compliance_check),
            "next_audit_date": (datetime.now() + timedelta(days=90)).isoformat(),
            "report_generated": datetime.now().isoformat()
        }
        
        return report
    
    def _get_relevant_regulations(self, order_data: Dict) -> List[str]:
        """Get list of relevant regulations for the order"""
        relevant_regs = []
        
        products = order_data.get("products", [])
        for product in products:
            meat_type = product.get("meat_type", "").lower()
            relevant_regs.append(f"GB Standard for {meat_type.upper()} Import")
            relevant_regs.append("China Customs Meat Import Procedures")
            
            if product.get("organic_certified"):
                relevant_regs.append("Organic Food Import Regulations")
            
            if product.get("halal_certified"):
                relevant_regs.append("Halal Food Certification Requirements")
        
        return list(set(relevant_regs))  # Remove duplicates
    
    def _generate_compliance_recommendations(self, compliance_check: Dict) -> List[str]:
        """Generate compliance improvement recommendations"""
        recommendations = []
        
        if compliance_check["compliance_score"] < 90:
            recommendations.append("Implement automated document validation system")
        
        if any("temperature" in violation.lower() for violation in compliance_check["violations"]):
            recommendations.append("Upgrade temperature monitoring system with real-time alerts")
        
        if len(compliance_check["violations"]) > 2:
            recommendations.append("Conduct staff training on China import regulations")
            recommendations.append("Establish pre-shipment compliance checklist")
        
        return recommendations

# Example usage
if __name__ == "__main__":
    # Initialize compliance checker
    checker = ComplianceChecker()
    
    # Sample order data
    sample_order = {
        "order_id": "BO-2024-001",
        "customer": {
            "name": "China Meat Import Co.",
            "import_license": "CN-IMPORT-2024-001"
        },
        "products": [
            {
                "product_id": "BEEF-001",
                "meat_type": "BEEF",
                "quantity_kg": 5000,
                "production_date": "2024-01-10",
                "expiry_date": "2025-01-10",
                "current_temperature": -16.5,
                "organic_certified": False,
                "halal_certified": True,
                "from_quarantine_zone": False,
                "hormones_used": False
            }
        ],
        "shipment": {
            "port_of_entry": "Manzhouli",
            "transport_method": "REFRIGERATED_TRUCK",
            "insurance_value": 1500
        },
        "documents": [
            "health_certificate",
            "customs_declaration",
            "certificate_of_origin",
            "halal_certificate"
        ],
        "documents_metadata": {
            "health_certificate": {
                "issue_date": "2024-01-12",
                "expiry_date": "2024-02-12"
            }
        }
    }
    
    # Run compliance check
    compliance_result = checker.check_order_compliance(sample_order)
    compliance_report = checker.generate_compliance_report(sample_order)
    
    print("Compliance Check Result:")
    print(json.dumps(compliance_result, indent=2))
    
    print("\nCompliance Report:")
    print(json.dumps(compliance_report, indent=2))
    
    # Show violation history
    history = checker.get_compliance_history()
    print(f"\nRecent Violation History ({len(history)} records):")
    for record in history[-3:]:  # Last 3 records
        print(f"  {record['order_id']}: {len(record['violations'])} violations")
