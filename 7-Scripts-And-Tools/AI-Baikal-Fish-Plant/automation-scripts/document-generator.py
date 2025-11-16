"""
Document Generator
AI Baikal Fish Plant
"""

class DocumentGenerator:
    def generate_health_certificate(self, product_data):
        return {
            'type': 'health_certificate',
            'product': product_data['name'],
            'batch_id': product_data['batch_id'],
            'issue_date': product_data['production_date'],
            'expiry_date': product_data['expiry_date']
        }
    
    def generate_customs_declaration(self, shipment_data):
        return {
            'type': 'customs_declaration',
            'hs_code': shipment_data['hs_code'],
            'value': shipment_data['value'],
            'weight': shipment_data['weight']
        }
