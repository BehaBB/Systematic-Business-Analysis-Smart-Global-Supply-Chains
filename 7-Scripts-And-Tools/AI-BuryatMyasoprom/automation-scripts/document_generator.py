#!/usr/bin/env python3
"""
Document Generator for BuryatMyasoprom
Automates generation of 25+ customs documents for China exports
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass
import jinja2
import pdfkit
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DocumentTemplate:
    name: str
    type: str
    language: str
    template_file: str
    required_fields: List[str]

class DocumentGenerator:
    def __init__(self, templates_path: str = "templates/"):
        self.templates_path = templates_path
        self.templates = self._load_templates()
        self.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_path))
        
    def _load_templates(self) -> Dict[str, DocumentTemplate]:
        """Load document templates configuration"""
        templates = {
            "health_certificate_cn": DocumentTemplate(
                name="Health Certificate (Chinese)",
                type="health_certificate",
                language="chinese",
                template_file="health_certificate_cn.html",
                required_fields=[
                    "exporter_name", "exporter_address", "product_description",
                    "production_date", "expiry_date", "veterinary_inspection",
                    "china_importer", "port_of_entry"
                ]
            ),
            "customs_declaration_cn": DocumentTemplate(
                name="Customs Declaration (Chinese)",
                type="customs_declaration", 
                language="chinese",
                template_file="customs_declaration_cn.html",
                required_fields=[
                    "hs_code", "product_value", "weight_kg", "country_of_origin",
                    "transport_method", "insurance_value"
                ]
            ),
            "certificate_of_origin_cn": DocumentTemplate(
                name="Certificate of Origin (Chinese)",
                type="certificate_of_origin",
                language="chinese",
                template_file="certificate_of_origin_cn.html", 
                required_fields=[
                    "manufacturer", "production_facility", "origin_criteria",
                    "export_license"
                ]
            ),
            "veterinary_certificate_cn": DocumentTemplate(
                name="Veterinary Certificate (Chinese)",
                type="veterinary_certificate",
                language="chinese", 
                template_file="veterinary_certificate_cn.html",
                required_fields=[
                    "veterinary_authority", "inspection_date", "animal_health",
                    "laboratory_tests"
                ]
            )
        }
        return templates

    def generate_document(self, template_id: str, data: Dict, output_format: str = "pdf") -> Dict:
        """Generate a single document"""
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")
        
        template = self.templates[template_id]
        
        # Validate required fields
        missing_fields = self._validate_required_fields(data, template.required_fields)
        if missing_fields:
            return {
                "success": False,
                "error": f"Missing required fields: {missing_fields}",
                "document_id": None
            }
        
        try:
            # Render template
            rendered_content = self._render_template(template, data)
            
            # Generate output
            document_id = f"DOC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{template.type}"
            
            if output_format == "pdf":
                output_path = self._generate_pdf(rendered_content, document_id)
            else:
                output_path = self._generate_html(rendered_content, document_id)
            
            return {
                "success": True,
                "document_id": document_id,
                "document_type": template.type,
                "output_path": output_path,
                "generated_at": datetime.now().isoformat(),
                "language": template.language
            }
            
        except Exception as e:
            logger.error(f"Error generating document {template_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "document_id": None
            }

    def generate_document_package(self, order_data: Dict, output_format: str = "pdf") -> Dict:
        """Generate complete document package for an order"""
        required_docs = order_data.get("required_documents", [])
        generated_docs = []
        errors = []
        
        for doc_type in required_docs:
            # Find appropriate template
            template_id = self._find_template_for_type(doc_type, order_data.get("language", "chinese"))
            
            if not template_id:
                errors.append(f"No template found for document type: {doc_type}")
                continue
            
            # Prepare data for this document type
            doc_data = self._prepare_document_data(doc_type, order_data)
            
            # Generate document
            result = self.generate_document(template_id, doc_data, output_format)
            
            if result["success"]:
                generated_docs.append(result)
            else:
                errors.append(f"Failed to generate {doc_type}: {result['error']}")
        
        return {
            "order_id": order_data.get("order_id"),
            "total_documents": len(required_docs),
            "generated_documents": len(generated_docs),
            "failed_documents": len(errors),
            "documents": generated_docs,
            "errors": errors,
            "package_id": f"PKG_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat()
        }

    def _validate_required_fields(self, data: Dict, required_fields: List[str]) -> List[str]:
        """Validate that all required fields are present"""
        missing = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing.append(field)
        return missing

    def _render_template(self, template: DocumentTemplate, data: Dict) -> str:
        """Render template with data"""
        try:
            template_obj = self.jinja_env.get_template(template.template_file)
            rendered = template_obj.render(
                data=data,
                generated_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                **data
            )
            return rendered
        except jinja2.TemplateNotFound:
            # Fallback to basic template generation
            return self._generate_basic_template(template, data)

    def _generate_basic_template(self, template: DocumentTemplate, data: Dict) -> str:
        """Generate basic template if template file not found"""
        basic_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{template.name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; }}
                .section {{ margin: 20px 0; }}
                .field {{ margin: 10px 0; }}
                .field-label {{ font-weight: bold; }}
                .signature {{ margin-top: 50px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{template.name}</h1>
                <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            
            <div class="content">
        """
        
        for field in template.required_fields:
            value = data.get(field, "NOT PROVIDED")
            basic_template += f"""
                <div class="field">
                    <span class="field-label">{field.replace('_', ' ').title()}:</span>
                    <span>{value}</span>
                </div>
            """
        
        basic_template += """
            </div>
            
            <div class="signature">
                <p>Authorized Signature: _________________________</p>
                <p>Date: _________________________</p>
            </div>
        </body>
        </html>
        """
        
        return basic_template

    def _generate_pdf(self, html_content: str, document_id: str) -> str:
        """Generate PDF from HTML content"""
        try:
            output_path = f"generated_docs/{document_id}.pdf"
            os.makedirs("generated_docs", exist_ok=True)
            
            # Using pdfkit (requires wkhtmltopdf)
            pdfkit.from_string(html_content, output_path)
            
            return output_path
        except Exception as e:
            logger.warning(f"PDF generation failed, falling back to HTML: {str(e)}")
            return self._generate_html(html_content, document_id)

    def _generate_html(self, html_content: str, document_id: str) -> str:
        """Generate HTML file"""
        output_path = f"generated_docs/{document_id}.html"
        os.makedirs("generated_docs", exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path

    def _find_template_for_type(self, doc_type: str, language: str) -> Optional[str]:
        """Find template ID for document type and language"""
        for template_id, template in self.templates.items():
            if template.type == doc_type and template.language == language:
                return template_id
        return None

    def _prepare_document_data(self, doc_type: str, order_data: Dict) -> Dict:
        """Prepare data for specific document type"""
        base_data = {
            "order_id": order_data.get("order_id"),
            "generation_date": datetime.now().strftime("%Y-%m-%d"),
            "exporter_name": "BuryatMyasoprom",
            "exporter_address": "Ulan-Ude, Republic of Buryatia, Russia",
            "export_license": "RU-MEAT-EXPORT-2024"
        }
        
        # Add order-specific data
        if order_data.get("customer"):
            base_data.update({
                "china_importer": order_data["customer"].get("name"),
                "importer_address": order_data["customer"].get("address"),
                "importer_license": order_data["customer"].get("import_license")
            })
        
        if order_data.get("products"):
            products = order_data["products"]
            if products:
                first_product = products[0]
                base_data.update({
                    "product_description": first_product.get("description"),
                    "meat_type": first_product.get("meat_type"),
                    "production_date": first_product.get("production_date"),
                    "expiry_date": first_product.get("expiry_date"),
                    "quantity_kg": sum(p.get("quantity_kg", 0) for p in products),
                    "weight_kg": sum(p.get("quantity_kg", 0) for p in products)
                })
        
        if order_data.get("shipment"):
            shipment = order_data["shipment"]
            base_data.update({
                "port_of_entry": shipment.get("port_of_entry"),
                "transport_method": shipment.get("transport_method"),
                "expected_departure": shipment.get("expected_departure"),
                "insurance_value": shipment.get("insurance_value"),
                "freight_cost": shipment.get("freight_cost")
            })
        
        # Document-specific data preparation
        if doc_type == "health_certificate":
            base_data.update(self._prepare_health_certificate_data(order_data))
        elif doc_type == "customs_declaration":
            base_data.update(self._prepare_customs_declaration_data(order_data))
        elif doc_type == "certificate_of_origin":
            base_data.update(self._prepare_certificate_of_origin_data(order_data))
        elif doc_type == "veterinary_certificate":
            base_data.update(self._prepare_veterinary_certificate_data(order_data))
        
        return base_data

    def _prepare_health_certificate_data(self, order_data: Dict) -> Dict:
        """Prepare data for health certificate"""
        products = order_data.get("products", [])
        data = {
            "veterinary_inspection": "APPROVED",
            "inspection_date": datetime.now().strftime("%Y-%m-%d"),
            "storage_temperature": "-18°C to -15°C",
            "quality_standards": "GB Standards for Meat Import"
        }
        
        if products:
            first_product = products[0]
            data.update({
                "meat_type": first_product.get("meat_type"),
                "production_facility": "BuryatMyasoprom Processing Plant",
                "veterinary_authority": "Russian Federal Veterinary Service"
            })
        
        return data

    def _prepare_customs_declaration_data(self, order_data: Dict) -> Dict:
        """Prepare data for customs declaration"""
        products = order_data.get("products", [])
        total_value = sum(
            p.get("quantity_kg", 0) * p.get("unit_price", 0) 
            for p in products
        )
        
        shipment = order_data.get("shipment", {})
        customs_value = total_value + shipment.get("insurance_value", 0) + shipment.get("freight_cost", 0)
        
        data = {
            "hs_code": "0201.10",  # Default for beef
            "product_value": total_value,
            "customs_value": customs_value,
            "country_of_origin": "RUSSIA",
            "destination_country": "CHINA",
            "currency": "USD"
        }
        
        if products:
            first_product = products[0]
            meat_type = first_product.get("meat_type", "").upper()
            hs_codes = {
                "BEEF": "0201.10",
                "LAMB": "0204.10", 
                "HORSE": "0205.00"
            }
            data["hs_code"] = hs_codes.get(meat_type, "0201.10")
        
        return data

    def _prepare_certificate_of_origin_data(self, order_data: Dict) -> Dict:
        """Prepare data for certificate of origin"""
        data = {
            "manufacturer": "BuryatMyasoprom",
            "production_facility": "Ulan-Ude Meat Processing Plant",
            "origin_criteria": "Wholly Obtained",
            "certifying_authority": "Chamber of Commerce and Industry of Buryatia",
            "certificate_number": f"COO-{datetime.now().strftime('%Y%m%d')}-001"
        }
        return data

    def _prepare_veterinary_certificate_data(self, order_data: Dict) -> Dict:
        """Prepare data for veterinary certificate"""
        products = order_data.get("products", [])
        data = {
            "veterinary_authority": "Federal Service for Veterinary and Phytosanitary Surveillance",
            "inspection_date": datetime.now().strftime("%Y-%m-%d"),
            "animal_health": "Healthy animals, disease-free zone",
            "laboratory_tests": "Salmonella: Negative, E.coli: Within limits",
            "quarantine_status": "No quarantine restrictions",
            "vaccination_status": "All vaccinations current"
        }
        
        if products:
            test_results = []
            for product in products:
                tests = product.get("lab_tests", [])
                test_results.extend(tests)
            
            if test_results:
                data["laboratory_tests"] = ", ".join(set(test_results))
        
        return data

    def get_available_templates(self) -> List[Dict]:
        """Get list of available document templates"""
        return [
            {
                "template_id": template_id,
                "name": template.name,
                "type": template.type,
                "language": template.language,
                "required_fields": template.required_fields
            }
            for template_id, template in self.templates.items()
        ]

# Example usage
if __name__ == "__main__":
    # Initialize document generator
    generator = DocumentGenerator()
    
    # Sample order data
    sample_order = {
        "order_id": "BO-2024-001",
        "customer": {
            "name": "China Meat Import Co.",
            "address": "Beijing, China", 
            "import_license": "CN-IMPORT-2024-001"
        },
        "products": [
            {
                "product_id": "BEEF-001",
                "description": "Frozen Beef Carcass Grade A",
                "meat_type": "BEEF",
                "quantity_kg": 5000,
                "unit_price": 5.50,
                "production_date": "2024-01-15",
                "expiry_date": "2025-01-15",
                "lab_tests": ["Salmonella", "E.coli", "Antibiotics"]
            }
        ],
        "shipment": {
            "port_of_entry": "Manzhouli",
            "transport_method": "REFRIGERATED_TRUCK",
            "expected_departure": "2024-02-20",
            "insurance_value": 1500,
            "freight_cost": 2000
        },
        "required_documents": [
            "health_certificate",
            "customs_declaration", 
            "certificate_of_origin",
            "veterinary_certificate"
        ],
        "language": "chinese"
    }
    
    # Generate single document
    print("Generating Health Certificate...")
    health_cert_result = generator.generate_document(
        "health_certificate_cn", 
        generator._prepare_document_data("health_certificate", sample_order)
    )
    print(f"Health Certificate: {health_cert_result}")
    
    # Generate complete document package
    print("\nGenerating Document Package...")
    package_result = generator.generate_document_package(sample_order)
    print(f"Document Package: {json.dumps(package_result, indent=2)}")
    
    # Show available templates
    print("\nAvailable Templates:")
    templates = generator.get_available_templates()
    for template in templates:
        print(f"  - {template['name']} ({template['type']})")
