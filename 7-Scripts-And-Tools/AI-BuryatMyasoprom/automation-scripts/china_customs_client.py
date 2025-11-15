#!/usr/bin/env python3
"""
China Customs API Client for BuryatMyasoprom
Handles integration with Chinese Customs electronic systems
"""

import json
import requests
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass
import asyncio
import aiohttp
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CustomsSubmission:
    submission_id: str
    status: str
    documents: List[Dict]
    submitted_at: datetime
    customs_reference: Optional[str] = None

class ChinaCustomsClient:
    def __init__(self, config_path: str = "config/customs_config.json"):
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.base_url = self.config["api"]["base_url"]
        self._setup_authentication()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load customs integration configuration"""
        default_config = {
            "api": {
                "base_url": "https://customs.china.gov/api/v1",
                "timeout": 30,
                "retry_attempts": 3,
                "retry_delay": 5
            },
            "authentication": {
                "method": "api_key",
                "key_header": "X-API-Key",
                "signature_required": True
            },
            "submission": {
                "max_documents_per_request": 10,
                "supported_formats": ["JSON", "XML"],
                "compression_enabled": True
            },
            "monitoring": {
                "status_check_interval": 300,  # 5 minutes
                "max_status_checks": 144,  # 24 hours
                "webhook_url": None
            }
        }
        
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                # Deep merge for nested dictionaries
                for key, value in user_config.items():
                    if isinstance(value, dict) and key in default_config:
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
        
        return default_config
    
    def _setup_authentication(self):
        """Setup authentication headers"""
        auth_config = self.config["authentication"]
        
        if auth_config["method"] == "api_key":
            api_key = self.config.get("credentials", {}).get("api_key")
            if api_key:
                self.session.headers.update({
                    auth_config["key_header"]: api_key
                })
        
        # Common headers for all requests
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "BuryatMyasoprom-Export-System/1.0",
            "Accept": "application/json"
        })
    
    def _generate_signature(self, data: str, timestamp: str) -> str:
        """Generate HMAC signature for request authentication"""
        secret_key = self.config.get("credentials", {}).get("secret_key", "")
        message = f"{timestamp}{data}"
        signature = hmac.new(
            secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def submit_documents(self, documents: List[Dict], order_data: Dict) -> Dict:
        """Submit documents to China Customs"""
        if not documents:
            return {"success": False, "error": "No documents provided"}
        
        # Prepare submission data
        submission_data = self._prepare_submission_data(documents, order_data)
        
        # Generate request signature if required
        if self.config["authentication"]["signature_required"]:
            timestamp = datetime.utcnow().isoformat()
            data_string = json.dumps(submission_data, sort_keys=True)
            signature = self._generate_signature(data_string, timestamp)
            
            self.session.headers.update({
                "X-Timestamp": timestamp,
                "X-Signature": signature
            })
        
        try:
            # Submit to customs API
            response = self._make_retry_request(
                "POST",
                f"{self.base_url}/submissions",
                json=submission_data
            )
            
            if response.status_code == 202:
                submission_result = response.json()
                return {
                    "success": True,
                    "submission_id": submission_result.get("submission_id"),
                    "customs_reference": submission_result.get("customs_reference"),
                    "status": submission_result.get("status", "SUBMITTED"),
                    "estimated_processing_time": submission_result.get("estimated_processing_time"),
                    "message": submission_result.get("message", "Documents submitted successfully")
                }
            else:
                error_detail = self._parse_error_response(response)
                return {
                    "success": False,
                    "error": f"Submission failed with status {response.status_code}",
                    "error_detail": error_detail
                }
                
        except Exception as e:
            logger.error(f"Document submission failed: {str(e)}")
            return {
                "success": False,
                "error": f"Submission error: {str(e)}"
            }
    
    def _prepare_submission_data(self, documents: List[Dict], order_data: Dict) -> Dict:
        """Prepare data for customs submission"""
        submission_data = {
            "submission_type": "MEAT_EXPORT",
            "exporter_info": {
                "name": "BuryatMyasoprom",
                "address": "Ulan-Ude, Republic of Buryatia, Russia",
                "tax_id": self.config.get("exporter", {}).get("tax_id", ""),
                "export_license": self.config.get("exporter", {}).get("export_license", "")
            },
            "importer_info": {
                "name": order_data.get("customer", {}).get("name"),
                "license_number": order_data.get("customer", {}).get("import_license"),
                "address": order_data.get("customer", {}).get("address")
            },
            "shipment_info": {
                "port_of_export": "Zabaikalsk",
                "port_of_entry": order_data.get("shipment", {}).get("port_of_entry"),
                "expected_arrival": order_data.get("shipment", {}).get("expected_departure"),
                "transport_method": order_data.get("shipment", {}).get("transport_method")
            },
            "products": [],
            "documents": [],
            "metadata": {
                "submission_date": datetime.utcnow().isoformat(),
                "system_version": "1.0",
                "order_id": order_data.get("order_id")
            }
        }
        
        # Add products information
        for product in order_data.get("products", []):
            submission_data["products"].append({
                "description": product.get("description"),
                "hs_code": self._get_hs_code(product.get("meat_type")),
                "quantity": product.get("quantity_kg"),
                "value": product.get("quantity_kg", 0) * product.get("unit_price", 0),
                "weight": product.get("quantity_kg"),
                "origin": "RUSSIA"
            })
        
        # Add documents
        for doc in documents:
            submission_data["documents"].append({
                "type": doc.get("type"),
                "content": doc.get("content", {}),
                "format": "JSON",
                "checksum": self._calculate_checksum(json.dumps(doc.get("content", {})))
            })
        
        return submission_data
    
    def _get_hs_code(self, meat_type: str) -> str:
        """Get HS code for meat type"""
        hs_codes = {
            "BEEF": "0201.10",
            "LAMB": "0204.10",
            "HORSE": "0205.00",
            "POULTRY": "0207.10"
        }
        return hs_codes.get(meat_type.upper(), "0201.10")
    
    def _calculate_checksum(self, data: str) -> str:
        """Calculate SHA-256 checksum for data validation"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def _make_retry_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make request with retry logic"""
        max_retries = self.config["api"]["retry_attempts"]
        retry_delay = self.config["api"]["retry_delay"]
        
        for attempt in range(max_retries + 1):
            try:
                response = self.session.request(method, url, **kwargs)
                
                # Retry on server errors (5xx) or rate limiting (429)
                if response.status_code in [429, 500, 502, 503, 504]:
                    if attempt < max_retries:
                        logger.warning(f"Request failed with status {response.status_code}, retrying in {retry_delay}s...")
                        asyncio.sleep(retry_delay)
                        continue
                
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    logger.warning(f"Request exception: {str(e)}, retrying in {retry_delay}s...")
                    asyncio.sleep(retry_delay)
                else:
                    raise e
        
        # This should never be reached due to the exception handling above
        raise Exception("Max retries exceeded")
    
    def _parse_error_response(self, response: requests.Response) -> Dict:
        """Parse error response from customs API"""
        try:
            error_data = response.json()
            return {
                "code": error_data.get("error_code"),
                "message": error_data.get("error_message"),
                "details": error_data.get("error_details"),
                "field_errors": error_data.get("field_errors", [])
            }
        except:
            return {
                "code": "UNKNOWN",
                "message": response.text,
                "details": None
            }
    
    def check_submission_status(self, submission_id: str) -> Dict:
        """Check status of a customs submission"""
        try:
            response = self._make_retry_request(
                "GET",
                f"{self.base_url}/submissions/{submission_id}"
            )
            
            if response.status_code == 200:
                status_data = response.json()
                return {
                    "success": True,
                    "submission_id": submission_id,
                    "status": status_data.get("status"),
                    "customs_reference": status_data.get("customs_reference"),
                    "last_updated": status_data.get("last_updated"),
                    "estimated_completion": status_data.get("estimated_completion"),
                    "issues": status_data.get("issues", []),
                    "actions_required": status_data.get("actions_required", [])
                }
            else:
                return {
                    "success": False,
                    "error": f"Status check failed with status {response.status_code}",
                    "error_detail": self._parse_error_response(response)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Status check error: {str(e)}"
            }
    
    async def monitor_submission(self, submission_id: str) -> Dict:
        """Monitor submission status until completion"""
        max_checks = self.config["monitoring"]["max_status_checks"]
        check_interval = self.config["monitoring"]["status_check_interval"]
        
        for check_count in range(max_checks):
            status_result = self.check_submission_status(submission_id)
            
            if not status_result["success"]:
                return status_result
            
            current_status = status_result["status"]
            
            # Check if processing is complete
            if current_status in ["APPROVED", "REJECTED", "CANCELLED"]:
                return {
                    "success": True,
                    "final_status": current_status,
                    "submission_id": submission_id,
                    "checks_performed": check_count + 1,
                    "completion_time": datetime.now().isoformat(),
                    "details": status_result
                }
            
            # If still processing, wait and check again
            logger.info(f"Submission {submission_id} status: {current_status} (check {check_count + 1}/{max_checks})")
            await asyncio.sleep(check_interval)
        
        # Max checks reached without completion
        return {
            "success": False,
            "error": f"Submission monitoring timeout after {max_checks} checks",
            "submission_id": submission_id,
            "last_status": status_result.get("status"),
            "checks_performed": max_checks
        }
    
    def get_regulation_updates(self, last_check: Optional[datetime] = None) -> List[Dict]:
        """Get latest regulation updates from China Customs"""
        params = {}
        if last_check:
            params["since"] = last_check.isoformat()
        
        try:
            response = self._make_retry_request(
                "GET",
                f"{self.base_url}/regulations",
                params=params
            )
            
            if response.status_code == 200:
                updates = response.json().get("updates", [])
                return {
                    "success": True,
                    "updates": updates,
                    "total_updates": len(updates),
                    "last_updated": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to fetch regulations: {response.status_code}",
                    "updates": []
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Regulation fetch error: {str(e)}",
                "updates": []
            }
    
    def validate_documents(self, documents: List[Dict]) -> Dict:
        """Pre-validate documents before submission"""
        validation_results = []
        
        for doc in documents:
            doc_type = doc.get("type")
            content = doc.get("content", {})
            
            # Basic validation
            validation_result = {
                "document_type": doc_type,
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Check required fields based on document type
            required_fields = self._get_required_fields(doc_type)
            for field in required_fields:
                if field not in content or not content[field]:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Missing required field: {field}")
            
            # Document-specific validation
            if doc_type == "health_certificate":
                self._validate_health_certificate(content, validation_result)
            elif doc_type == "customs_declaration":
                self._validate_customs_declaration(content, validation_result)
            
            validation_results.append(validation_result)
        
        overall_valid = all(result["valid"] for result in validation_results)
        
        return {
            "valid": overall_valid,
            "documents": validation_results,
            "summary": {
                "total_documents": len(documents),
                "valid_documents": sum(1 for r in validation_results if r["valid"]),
                "total_errors": sum(len(r["errors"]) for r in validation_results),
                "total_warnings": sum(len(r["warnings"]) for r in validation_results)
            }
        }
    
    def _get_required_fields(self, doc_type: str) -> List[str]:
        """Get required fields for document type"""
        required_fields = {
            "health_certificate": [
                "exporter_name", "product_description", "production_date",
                "veterinary_inspection", "china_importer"
            ],
            "customs_declaration": [
                "hs_code", "product_value", "weight_kg", "country_of_origin"
            ],
            "certificate_of_origin": [
                "manufacturer", "origin_criteria", "export_license"
            ],
            "veterinary_certificate": [
                "veterinary_authority", "inspection_date", "animal_health"
            ]
        }
        return required_fields.get(doc_type, [])
    
    def _validate_health_certificate(self, content: Dict, result: Dict):
        """Validate health certificate specific rules"""
        production_date = content.get("production_date")
        if production_date:
            try:
                prod_date = datetime.fromisoformat(production_date)
                if prod_date > datetime.now():
                    result["errors"].append("Production date cannot be in the future")
                
                # Check if certificate is too old
                if (datetime.now() - prod_date).days > 30:
                    result["warnings"].append("Health certificate may be expiring soon")
            except ValueError:
                result["errors"].append("Invalid production date format")
    
    def _validate_customs_declaration(self, content: Dict, result: Dict):
        """Validate customs declaration specific rules"""
        product_value = content.get("product_value", 0)
        if product_value <= 0:
            result["errors"].append("Product value must be greater than 0")
        
        weight_kg = content.get("weight_kg", 0)
        if weight_kg <= 0:
            result["errors"].append("Product weight must be greater than 0")
        
        # Check HS code format
        hs_code = content.get("hs_code", "")
        if not self._is_valid_hs_code(hs_code):
            result["errors"].append("Invalid HS code format")
    
    def _is_valid_hs_code(self, hs_code: str) -> bool:
        """Validate HS code format"""
        # Basic HS code validation (6-10 digits with optional periods)
        import re
        pattern = r'^\d{4}\.?\d{0,2}$'
        return bool(re.match(pattern, hs_code))
    
    def generate_submission_report(self, submission_id: str) -> Dict:
        """Generate comprehensive submission report"""
        status_result = self.check_submission_status(submission_id)
        
        if not status_result["success"]:
            return status_result
        
        report = {
            "report_id": f"CUSTOMS_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "submission_id": submission_id,
            "generated_at": datetime.now().isoformat(),
            "status_overview": status_result,
            "timeline": self._get_submission_timeline(submission_id),
            "compliance_analysis": self._analyze_submission_compliance(submission_id),
            "recommendations": self._generate_submission_recommendations(status_result),
            "next_steps": self._get_next_steps(status_result.get("status"))
        }
        
        return report
    
    def _get_submission_timeline(self, submission_id: str) -> List[Dict]:
        """Get submission timeline events"""
        # This would typically come from the customs API
        # For now, return mock timeline
        return [
            {
                "event": "SUBMITTED",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "description": "Documents submitted to China Customs"
            },
            {
                "event": "UNDER_REVIEW", 
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                "description": "Submission under customs review"
            }
        ]
    
    def _analyze_submission_compliance(self, submission_id: str) -> Dict:
        """Analyze submission compliance with regulations"""
        # Mock compliance analysis
        return {
            "overall_compliance_score": 95.5,
            "regulation_checks": [
                {"regulation": "GB Standard 123", "compliant": True, "details": "Meets all requirements"},
                {"regulation": "Customs Procedure 456", "compliant": True, "details": "Proper documentation"},
                {"regulation": "Import License Check", "compliant": True, "details": "Valid import license"}
            ],
            "risk_factors": [],
            "compliance_status": "COMPLIANT"
        }
    
    def _generate_submission_recommendations(self, status_result: Dict) -> List[str]:
        """Generate recommendations based on submission status"""
        status = status_result.get("status")
        recommendations = []
        
        if status == "UNDER_REVIEW":
            recommendations.append("Monitor status regularly for updates")
            recommendations.append("Prepare additional documentation if requested")
        elif status == "ADDITIONAL_INFO_REQUIRED":
            recommendations.append("Provide requested information within 48 hours")
            recommendations.append("Contact customs broker for assistance")
        elif status == "REJECTED":
            recommendations.append("Review rejection reasons and correct issues")
            recommendations.append("Resubmit with corrected documentation")
        
        return recommendations
    
    def _get_next_steps(self, status: str) -> List[str]:
        """Get next steps based on current status"""
        next_steps_map = {
            "SUBMITTED": ["Wait for customs review", "Monitor status updates"],
            "UNDER_REVIEW": ["Continue monitoring", "Prepare for possible additional requests"],
            "APPROVED": ["Proceed with shipment", "Update order status", "Notify customer"],
            "REJECTED": ["Analyze rejection reasons", "Correct issues", "Prepare resubmission"]
        }
        return next_steps_map.get(status, ["Contact support for guidance"])

# Example usage
if __name__ == "__main__":
    # Initialize customs client
    client = ChinaCustomsClient()
    
    # Sample documents for submission
    sample_documents = [
        {
            "type": "health_certificate",
            "content": {
                "exporter_name": "BuryatMyasoprom",
                "product_description": "Frozen Beef Carcass",
                "production_date": "2024-01-15",
                "veterinary_inspection": "APPROVED",
                "china_importer": "China Meat Import Co."
            }
        },
        {
            "type": "customs_declaration", 
            "content": {
                "hs_code": "0201.10",
                "product_value": 27500,
                "weight_kg": 5000,
                "country_of_origin": "RUSSIA"
            }
        }
    ]
    
    sample_order = {
        "order_id": "BO-2024-001",
        "customer": {
            "name": "China Meat Import Co.",
            "import_license": "CN-IMPORT-2024-001",
            "address": "Beijing, China"
        },
        "products": [
            {
                "description": "Frozen Beef Carcass",
                "meat_type": "BEEF", 
                "quantity_kg": 5000,
                "unit_price": 5.50
            }
        ],
        "shipment": {
            "port_of_entry": "Manzhouli",
            "transport_method": "REFRIGERATED_TRUCK",
            "expected_departure": "2024-02-20"
        }
    }
    
    # Test document validation
    print("Validating documents...")
    validation_result = client.validate_documents(sample_documents)
    print(f"Validation: {json.dumps(validation_result, indent=2)}")
    
    # Test submission (would require actual API credentials)
    if validation_result["valid"]:
        print("\nSubmitting documents...")
        submission_result = client.submit_documents(sample_documents, sample_order)
        print(f"Submission: {json.dumps(submission_result, indent=2)}")
        
        if submission_result["success"]:
            # Test status check
            print(f"\nChecking submission status...")
            status_result = client.check_submission_status(submission_result["submission_id"])
            print(f"Status: {json.dumps(status_result, indent=2)}")
    
    # Test regulation updates
    print("\nChecking regulation updates...")
    updates_result = client.get_regulation_updates()
    print(f"Regulation Updates: {json.dumps(updates_result, indent=2)}")
