#!/usr/bin/env python3
"""
Order Data Processor for BuryatMyasoprom
Processes export orders and prepares data for document generation
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OrderProcessor:
    def __init__(self, config_path: str = "config/order_processing.json"):
        self.config = self._load_config(config_path)
        self.products_db = self._load_products_database()
        self.customers_db = self._load_customers_database()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load order processing configuration"""
        default_config = {
            "processing_rules": {
                "min_order_quantity": 100,  # kg
                "max_order_quantity": 50000,  # kg
                "lead_time_days": 3,
                "temperature_ranges": {
                    "BEEF": {"min": -18, "max": -15},
                    "LAMB": {"min": -18, "max": -15},
                    "HORSE": {"min": -20, "max": -18}
                }
            },
            "validation_rules": {
                "required_customer_fields": ["name", "import_license", "address"],
                "required_product_fields": ["meat_type", "quantity_kg", "production_date"],
                "document_requirements": {
                    "china": ["health_certificate", "customs_declaration", "certificate_of_origin"]
                }
            }
        }
        
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
        
        return default_config
    
    def _load_products_database(self) -> pd.DataFrame:
        """Load product catalog from database or file"""
        products_data = {
            "product_id": ["BEEF-001", "LAMB-001", "HORSE-001", "BEEF-002"],
            "name": ["Frozen Beef Carcass Grade A", "Frozen Lamb Carcass", "Frozen Horse Meat", "Frozen Beef Carcass Grade B"],
            "meat_type": ["BEEF", "LAMB", "HORSE", "BEEF"],
            "hs_code": ["0201.10", "0204.10", "0205.00", "0201.10"],
            "unit_price_usd": [5.50, 6.80, 4.20, 4.80],
            "shelf_life_days": [365, 180, 365, 365],
            "storage_temperature": [-18, -18, -20, -18],
            "quality_grade": ["A", "B", "A", "B"]
        }
        return pd.DataFrame(products_data)
    
    def _load_customers_database(self) -> pd.DataFrame:
        """Load customer database"""
        customers_data = {
            "customer_id": ["CUST-CN-001", "CUST-CN-002", "CUST-CN-003"],
            "name": ["China Meat Import Co.", "Shanghai Food Distributors", "Guangzhou Meat Market"],
            "import_license": ["CN-IMPORT-2024-001", "CN-IMPORT-2024-002", "CN-IMPORT-2024-003"],
            "address": ["Beijing, China", "Shanghai, China", "Guangzhou, China"],
            "preferred_ports": ["Manzhouli", "Suifenhe", "Dalian"]
        }
        return pd.DataFrame(customers_data)
    
    def validate_order(self, order_data: Dict) -> Dict:
        """Validate order data against business rules"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "required_documents": []
        }
        
        # Validate customer
        customer_validation = self._validate_customer(order_data.get("customer", {}))
        if not customer_validation["valid"]:
            validation_result["valid"] = False
            validation_result["errors"].extend(customer_validation["errors"])
        
        # Validate products
        products_validation = self._validate_products(order_data.get("products", []))
        if not products_validation["valid"]:
            validation_result["valid"] = False
            validation_result["errors"].extend(products_validation["errors"])
        validation_result["warnings"].extend(products_validation["warnings"])
        
        # Validate shipment
        shipment_validation = self._validate_shipment(order_data.get("shipment", {}))
        if not shipment_validation["valid"]:
            validation_result["valid"] = False
            validation_result["errors"].extend(shipment_validation["errors"])
        
        # Determine required documents
        if validation_result["valid"]:
            validation_result["required_documents"] = self._determine_required_documents(order_data)
        
        return validation_result
    
    def _validate_customer(self, customer_data: Dict) -> Dict:
        """Validate customer information"""
        result = {"valid": True, "errors": []}
        
        required_fields = self.config["validation_rules"]["required_customer_fields"]
        for field in required_fields:
            if field not in customer_data or not customer_data[field]:
                result["valid"] = False
                result["errors"].append(f"Missing required customer field: {field}")
        
        # Check if customer exists in database
        if "customer_id" in customer_data:
            customer_exists = self.customers_db[
                self.customers_db["customer_id"] == customer_data["customer_id"]
            ].shape[0] > 0
            if not customer_exists:
                result["valid"] = False
                result["errors"].append(f"Customer ID not found: {customer_data['customer_id']}")
        
        return result
    
    def _validate_products(self, products: List[Dict]) -> Dict:
        """Validate product information"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        if not products:
            result["valid"] = False
            result["errors"].append("No products in order")
            return result
        
        total_quantity = 0
        
        for i, product in enumerate(products):
            # Check required fields
            required_fields = self.config["validation_rules"]["required_product_fields"]
            for field in required_fields:
                if field not in product:
                    result["valid"] = False
                    result["errors"].append(f"Product {i+1}: Missing required field: {field}")
            
            # Validate quantity
            quantity = product.get("quantity_kg", 0)
            if quantity < self.config["processing_rules"]["min_order_quantity"]:
                result["valid"] = False
                result["errors"].append(
                    f"Product {i+1}: Quantity {quantity}kg below minimum {self.config['processing_rules']['min_order_quantity']}kg"
                )
            
            if quantity > self.config["processing_rules"]["max_order_quantity"]:
                result["valid"] = False
                result["errors"].append(
                    f"Product {i+1}: Quantity {quantity}kg exceeds maximum {self.config['processing_rules']['max_order_quantity']}kg"
                )
            
            total_quantity += quantity
            
            # Check product existence
            if "product_id" in product:
                product_exists = self.products_db[
                    self.products_db["product_id"] == product["product_id"]
                ].shape[0] > 0
                if not product_exists:
                    result["warnings"].append(f"Product ID not found: {product['product_id']}")
        
        # Check total order quantity
        if total_quantity > 100000:  # 100 tons
            result["warnings"].append(f"Large order detected: {total_quantity}kg")
        
        return result
    
    def _validate_shipment(self, shipment_data: Dict) -> Dict:
        """Validate shipment information"""
        result = {"valid": True, "errors": []}
        
        if not shipment_data:
            result["valid"] = False
            result["errors"].append("Missing shipment information")
            return result
        
        # Check departure date
        departure_date = shipment_data.get("expected_departure")
        if departure_date:
            try:
                dep_date = datetime.fromisoformat(departure_date.replace('Z', '+00:00'))
                min_departure = datetime.now() + timedelta(days=self.config["processing_rules"]["lead_time_days"])
                if dep_date < min_departure:
                    result["valid"] = False
                    result["errors"].append(
                        f"Departure date {departure_date} is too soon. Minimum lead time: {self.config['processing_rules']['lead_time_days']} days"
                    )
            except ValueError:
                result["valid"] = False
                result["errors"].append(f"Invalid departure date format: {departure_date}")
        
        # Check transport method
        transport_method = shipment_data.get("transport_method", "").upper()
        valid_methods = ["REFRIGERATED_TRUCK", "REFRIGERATED_CONTAINER", "AIR_FREIGHT"]
        if transport_method and transport_method not in valid_methods:
            result["warnings"].append(f"Unusual transport method: {transport_method}")
        
        return result
    
    def _determine_required_documents(self, order_data: Dict) -> List[str]:
        """Determine which documents are required for this order"""
        base_documents = self.config["validation_rules"]["document_requirements"]["china"]
        required_documents = base_documents.copy()
        
        # Add conditional documents based on products
        products = order_data.get("products", [])
        for product in products:
            if product.get("organic_certified"):
                if "organic_certificate" not in required_documents:
                    required_documents.append("organic_certificate")
            
            if product.get("halal_certified"):
                if "halal_certificate" not in required_documents:
                    required_documents.append("halal_certificate")
            
            if product.get("quality_grade") in ["A", "PREMIUM"]:
                if "quality_grade_certificate" not in required_documents:
                    required_documents.append("quality_grade_certificate")
        
        return required_documents
    
    def calculate_order_value(self, order_data: Dict) -> float:
        """Calculate total order value"""
        total_value = 0.0
        
        for product in order_data.get("products", []):
            product_id = product.get("product_id")
            quantity = product.get("quantity_kg", 0)
            
            # Get price from database or use provided price
            if product_id:
                product_info = self.products_db[self.products_db["product_id"] == product_id]
                if not product_info.empty:
                    unit_price = product_info.iloc[0]["unit_price_usd"]
                else:
                    unit_price = product.get("unit_price", 0)
            else:
                unit_price = product.get("unit_price", 0)
            
            total_value += quantity * unit_price
        
        # Add shipment costs if provided
        shipment = order_data.get("shipment", {})
        total_value += shipment.get("insurance_value", 0)
        total_value += shipment.get("freight_cost", 0)
        
        return round(total_value, 2)
    
    def generate_order_summary(self, order_data: Dict) -> Dict:
        """Generate comprehensive order summary"""
        validation = self.validate_order(order_data)
        order_value = self.calculate_order_value(order_data)
        
        summary = {
            "order_id": order_data.get("order_id", f"ORDER-{datetime.now().strftime('%Y%m%d-%H%M%S')}"),
            "customer": order_data.get("customer", {}).get("name", "Unknown"),
            "total_quantity_kg": sum(p.get("quantity_kg", 0) for p in order_data.get("products", [])),
            "total_value_usd": order_value,
            "validation_result": validation,
            "processing_timeline": self._estimate_processing_timeline(order_data),
            "risk_assessment": self._assess_order_risk(order_data),
            "generated_at": datetime.now().isoformat()
        }
        
        return summary
    
    def _estimate_processing_timeline(self, order_data: Dict) -> Dict:
        """Estimate order processing timeline"""
        base_time = datetime.now()
        
        return {
            "document_preparation": (base_time + timedelta(hours=2)).isoformat(),
            "compliance_check": (base_time + timedelta(hours=4)).isoformat(),
            "ready_for_shipment": (base_time + timedelta(hours=6)).isoformat(),
            "customs_submission": (base_time + timedelta(hours=8)).isoformat()
        }
    
    def _assess_order_risk(self, order_data: Dict) -> Dict:
        """Assess order risk level"""
        risk_score = 0
        risk_factors = []
        
        products = order_data.get("products", [])
        
        # Quantity risk
        total_quantity = sum(p.get("quantity_kg", 0) for p in products)
        if total_quantity > 20000:
            risk_score += 2
            risk_factors.append("Large order quantity")
        
        # Product type risk
        for product in products:
            if product.get("meat_type") == "HORSE":
                risk_score += 1
                risk_factors.append("Horse meat - special handling required")
            
            if product.get("organic_certified"):
                risk_score += 1
                risk_factors.append("Organic certification requirements")
        
        # Determine risk level
        if risk_score >= 3:
            risk_level = "HIGH"
        elif risk_score >= 1:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "recommendations": self._generate_risk_recommendations(risk_score)
        }
    
    def _generate_risk_recommendations(self, risk_score: int) -> List[str]:
        """Generate recommendations based on risk score"""
        recommendations = []
        
        if risk_score >= 2:
            recommendations.append("Perform additional quality checks")
            recommendations.append("Verify all certifications are current")
        
        if risk_score >= 3:
            recommendations.append("Consult with compliance team before shipment")
            recommendations.append("Consider splitting large orders")
        
        return recommendations

# Example usage and testing
if __name__ == "__main__":
    # Initialize processor
    processor = OrderProcessor()
    
    # Sample order data
    sample_order = {
        "order_id": "BO-2024-001",
        "customer": {
            "customer_id": "CUST-CN-001",
            "name": "China Meat Import Co.",
            "import_license": "CN-IMPORT-2024-001",
            "address": "Beijing, China"
        },
        "products": [
            {
                "product_id": "BEEF-001",
                "quantity_kg": 5000,
                "meat_type": "BEEF",
                "production_date": "2024-01-15",
                "organic_certified": False,
                "halal_certified": True
            }
        ],
        "shipment": {
            "port_of_entry": "Manzhouli",
            "expected_departure": "2024-02-20",
            "transport_method": "REFRIGERATED_TRUCK",
            "insurance_value": 1500,
            "freight_cost": 2000
        }
    }
    
    # Process order
    validation = processor.validate_order(sample_order)
    summary = processor.generate_order_summary(sample_order)
    
    print("Order Validation Result:")
    print(json.dumps(validation, indent=2))
    print("\nOrder Summary:")
    print(json.dumps(summary, indent=2))
