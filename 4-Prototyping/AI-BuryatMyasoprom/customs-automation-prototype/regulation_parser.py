"""
China Import Regulation Parser for Meat Products
Automatically parses and validates compliance with Chinese import requirements
"""

import yaml
import requests
from datetime import datetime
from typing import Dict, List, Optional

class ChinaRegulationParser:
    def __init__(self):
        self.regulations = self._load_regulations()
        self.last_update = datetime.now()
    
    def _load_regulations(self) -> Dict:
        """Load China import regulations from YAML file"""
        base_regulations = {
            "meat_import_requirements": {
                "banned_products": [
                    "meat_from_quarantine_zones",
                    "meat_with_hormones",
                    "meat_with_antibiotics_above_limit"
                ],
                "temperature_requirements": {
                    "frozen_beef": {"min": -18, "max": -15},
                    "frozen_lamb": {"min": -18, "max": -15},
                    "frozen_horse": {"min": -20, "max": -18},
                    "chilled_meat": {"min": 0, "max": 4}
                },
                "documentation_requirements": {
                    "mandatory_documents": [
                        "health_certificate",
                        "veterinary_certificate", 
                        "certificate_of_origin",
                        "customs_declaration",
                        "quality_inspection_certificate"
                    ],
                    "additional_documents": {
                        "organic_products": "organic_certification",
                        "halal_products": "halal_certification",
                        "premium_grade": "quality_grade_certificate"
                    }
                },
                "labeling_requirements": {
                    "language": ["chinese", "russian"],
                    "required_information": [
                        "product_name",
                        "production_date",
                        "expiry_date",
                        "storage_conditions",
                        "net_weight",
                        "importer_information",
                        "country_of_origin"
                    ],
                    "font_size": {"chinese": "≥4mm", "russian": "≥3mm"}
                },
                "testing_requirements": {
                    "microbiological_tests": [
                        "total_bacterial_count",
                        "salmonella",
                        "listeria",
                        "e_coli"
                    ],
                    "chemical_tests": [
                        "antibiotic_residues",
                        "pesticide_residues", 
                        "heavy_metals",
                        "veterinary_drug_residues"
                    ],
                    "frequency": "each_batch"
                }
            },
            "customs_procedures": {
                "pre_approval_required": True,
                "quarantine_period": "3-7_days",
                "inspection_rate": "10%_of_shipments",
                "rejection_criteria": [
                    "temperature_violation",
                    "missing_documents",
                    "failed_lab_tests",
                    "labeling_non_compliance"
                ]
            }
        }
        return base_regulations
    
    def validate_product_compliance(self, product_data: Dict) -> Dict:
        """Validate product against China import regulations"""
        violations = []
        warnings = []
        
        # Check temperature compliance
        temp_status = self._check_temperature_compliance(product_data)
        if not temp_status["compliant"]:
            violations.extend(temp_status["violations"])
        
        # Check documentation
        doc_status = self._check_documentation_compliance(product_data)
        if not doc_status["compliant"]:
            violations.extend(doc_status["violations"])
        
        # Check labeling
        label_status = self._check_labeling_compliance(product_data)
        if not label_status["compliant"]:
            violations.extend(label_status["violations"])
        
        # Check for banned products
        if self._is_product_banned(product_data):
            violations.append("Product falls under banned categories")
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "required_actions": self._get_required_actions(violations),
            "validation_date": datetime.now().isoformat()
        }
    
    def _check_temperature_compliance(self, product_data: Dict) -> Dict:
        """Check if product meets temperature requirements"""
        meat_type = product_data.get("meat_type", "").lower()
        current_temp = product_data.get("current_temperature")
        requirements = self.regulations["meat_import_requirements"]["temperature_requirements"]
        
        violations = []
        
        # Find appropriate temperature range
        temp_key = None
        for key in requirements.keys():
            if meat_type in key:
                temp_key = key
                break
        
        if temp_key and current_temp is not None:
            min_temp = requirements[temp_key]["min"]
            max_temp = requirements[temp_key]["max"]
            
            if current_temp < min_temp or current_temp > max_temp:
                violations.append(
                    f"Temperature {current_temp}°C outside required range ({min_temp}°C to {max_temp}°C)"
                )
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations
        }
    
    def _check_documentation_compliance(self, product_data: Dict) -> Dict:
        """Check if all required documents are present"""
        required_docs = self.regulations["meat_import_requirements"]["documentation_requirements"]["mandatory_documents"]
        provided_docs = product_data.get("documents", [])
        
        violations = []
        
        for doc in required_docs:
            if doc not in provided_docs:
                violations.append(f"Missing required document: {doc}")
        
        # Check additional documents based on product attributes
        additional_docs = self.regulations["meat_import_requirements"]["documentation_requirements"]["additional_documents"]
        
        if product_data.get("organic_certified") and "organic_certification" not in provided_docs:
            violations.append("Organic certification required for organic products")
        
        if product_data.get("halal_certified") and "halal_certification" not in provided_docs:
            violations.append("Halal certification required for halal products")
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations
        }
    
    def _check_labeling_compliance(self, product_data: Dict) -> Dict:
        """Check labeling requirements"""
        label_info = product_data.get("labeling", {})
        required_info = self.regulations["meat_import_requirements"]["labeling_requirements"]["required_information"]
        
        violations = []
        
        for info in required_info:
            if info not in label_info:
                violations.append(f"Missing labeling information: {info}")
        
        # Check language requirements
        languages = label_info.get("languages", [])
        required_languages = self.regulations["meat_import_requirements"]["labeling_requirements"]["language"]
        
        for lang in required_languages:
            if lang not in languages:
                violations.append(f"Missing required language: {lang}")
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations
        }
    
    def _is_product_banned(self, product_data: Dict) -> bool:
        """Check if product falls under banned categories"""
        banned_categories = self.regulations["meat_import_requirements"]["banned_products"]
        
        # Check various ban criteria
        if product_data.get("from_quarantine_zone"):
            return True
        
        if product_data.get("hormones_used"):
            return True
        
        if product_data.get("antibiotics_above_limit"):
            return True
        
        return False
    
    def _get_required_actions(self, violations: List[str]) -> List[str]:
        """Generate required actions based on violations"""
        actions = []
        
        for violation in violations:
            if "temperature" in violation.lower():
                actions.append("Adjust storage temperature to required range")
            elif "missing document" in violation.lower():
                doc_name = violation.split(":")[-1].strip()
                actions.append(f"Prepare and include {doc_name}")
            elif "labeling" in violation.lower():
                actions.append("Update product labeling to meet requirements")
            elif "banned" in violation.lower():
                actions.append("Product cannot be exported to China - consider alternative markets")
        
        return actions
    
    def get_import_requirements(self, product_type: str) -> Dict:
        """Get specific import requirements for product type"""
        requirements = {}
        
        # Temperature requirements
        temp_req = self.regulations["meat_import_requirements"]["temperature_requirements"]
        for key, value in temp_req.items():
            if product_type in key:
                requirements["temperature"] = value
                break
        
        # Documentation requirements
        requirements["documents"] = self.regulations["meat_import_requirements"]["documentation_requirements"]
        
        # Labeling requirements
        requirements["labeling"] = self.regulations["meat_import_requirements"]["labeling_requirements"]
        
        return requirements

# Example usage
if __name__ == "__main__":
    parser = ChinaRegulationParser()
    
    # Test product data
    test_product = {
        "meat_type": "frozen_beef",
        "current_temperature": -17,
        "documents": [
            "health_certificate",
            "veterinary_certificate",
            "certificate_of_origin",
            "customs_declaration"
        ],
        "labeling": {
            "languages": ["chinese", "russian"],
            "product_name": "Frozen Beef",
            "production_date": "2024-01-15",
            "expiry_date": "2025-01-15",
            "storage_conditions": "Store at -18°C",
            "net_weight": "1000kg",
            "importer_information": "China Meat Import Co.",
            "country_of_origin": "Russia"
        },
        "organic_certified": False,
        "halal_certified": True,
        "from_quarantine_zone": False,
        "hormones_used": False,
        "antibiotics_above_limit": False
    }
    
    # Validate compliance
    compliance_result = parser.validate_product_compliance(test_product)
    print("Compliance Check Result:")
    print(f"Compliant: {compliance_result['compliant']}")
    print(f"Violations: {compliance_result['violations']}")
    print(f"Required Actions: {compliance_result['required_actions']}")
    
    # Get specific requirements
    requirements = parser.get_import_requirements("beef")
    print("\nImport Requirements for Beef:")
    print(f"Temperature: {requirements.get('temperature')}")
