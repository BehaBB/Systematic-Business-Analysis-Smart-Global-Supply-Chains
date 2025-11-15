# API Documentation
## AI BuryatMyasoprom Digital Transformation Platform

### Base Information
- **Base URL**: `https://api.buryatmyasoprom.com/v1`
- **Authentication**: JWT Bearer Token
- **Format**: JSON
- **Encoding**: UTF-8

### Authentication

#### Get Access Token
```http
POST /auth/token
Content-Type: application/json

{
  "username": "export_manager",
  "password": "********"
}
Response:

json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user_role": "export_manager"
}
Orders API
Create Export Order
http
POST /orders
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": "cust_12345",
  "products": [
    {
      "product_id": "beef_001",
      "quantity_kg": 5000,
      "unit_price": 5.50
    }
  ],
  "shipment": {
    "port_of_entry": "Manzhouli",
    "expected_departure": "2024-02-15",
    "transport_method": "REFRIGERATED_TRUCK"
  }
}
Response:

json
{
  "order_id": "order_67890",
  "status": "created",
  "documents_required": [
    "health_certificate",
    "customs_declaration",
    "certificate_of_origin"
  ],
  "estimated_processing_time": "8 hours"
}
Get Order Status
http
GET /orders/{order_id}
Authorization: Bearer {token}
Documents API
Generate Documents
http
POST /documents/generate
Authorization: Bearer {token}
Content-Type: application/json

{
  "order_id": "order_67890",
  "document_types": [
    "health_certificate",
    "customs_declaration",
    "certificate_of_origin"
  ],
  "language": "chinese"
}
Response:

json
{
  "documents": [
    {
      "document_id": "doc_health_123",
      "type": "health_certificate",
      "status": "generated",
      "download_url": "/documents/doc_health_123/download",
      "validation_errors": []
    }
  ],
  "compliance_score": 95.5
}
Submit to Customs
http
POST /documents/submit
Authorization: Bearer {token}
Content-Type: application/json

{
  "order_id": "order_67890",
  "documents": ["doc_health_123", "doc_customs_456"]
}
Compliance API
Check Compliance
http
POST /compliance/validate
Authorization: Bearer {token}
Content-Type: application/json

{
  "product_data": {
    "meat_type": "BEEF",
    "production_date": "2024-01-15",
    "storage_temperature": -18.5
  },
  "shipment_data": {
    "destination": "China",
    "port_of_entry": "Manzhouli"
  }
}
Response:

json
{
  "compliant": true,
  "violations": [],
  "risk_score": 12.5,
  "required_actions": [
    "Update health certificate with new regulation"
  ]
}
Real-time Monitoring API
Get Temperature Data
http
GET /monitoring/temperature/{batch_id}
Authorization: Bearer {token}
Response:

json
{
  "batch_id": "batch_789",
  "current_temperature": -17.8,
  "average_temperature": -18.2,
  "violations_today": 0,
  "alerts": []
}
Error Handling
Common HTTP Status Codes
200 OK - Request successful

400 Bad Request - Invalid input data

401 Unauthorized - Authentication required

403 Forbidden - Insufficient permissions

404 Not Found - Resource not found

422 Validation Error - Business logic validation failed

500 Internal Server Error - Server error

Error Response Format
json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Product quantity exceeds available stock",
    "details": {
      "available_stock": 4500,
      "requested_quantity": 5000
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
Rate Limiting
Limit: 1000 requests per hour per API key

Headers:

X-RateLimit-Limit: Request limit

X-RateLimit-Remaining: Remaining requests

X-RateLimit-Reset: Reset time

Webhooks
Available Webhooks
order.status_changed - Order status updated

document.generated - Document generation completed

compliance.violation - Compliance violation detected

shipment.delayed - Shipment delay detected

Webhook Payload Example
json
{
  "event": "order.status_changed",
  "data": {
    "order_id": "order_67890",
    "old_status": "processing",
    "new_status": "ready_for_shipment",
    "timestamp": "2024-01-15T14:30:00Z"
  }
}
SDK Examples
Python SDK
python
from buryat_sdk import BuryatClient

client = BuryatClient(api_key="your_api_key")

# Create order
order = client.orders.create({
    "customer_id": "cust_123",
    "products": [...]
})

# Generate documents
documents = client.documents.generate(order.id)

# Check compliance
compliance = client.compliance.validate(order.id)
JavaScript SDK
javascript
import { BuryatClient } from '@buryatmyasoprom/sdk';

const client = new BuryatClient({ apiKey: 'your_api_key' });

// Submit order
const order = await client.orders.create(orderData);

// Monitor temperature
const tempData = await client.monitoring.getTemperature(batchId);
Testing API
Sandbox Environment
URL: https://sandbox.buryatmyasoprom.com/v1

Test Data: Pre-configured test orders and products

Limits: No rate limiting in sandbox

Example Test Order
json
{
  "order_id": "test_order_001",
  "customer_id": "test_customer_001",
  "products": [
    {
      "product_id": "test_beef_001",
      "quantity_kg": 1000
    }
  ]
}
Changelog
Version 1.2.0 (2024-01-15)
Added real-time temperature monitoring endpoints

Enhanced compliance validation rules

Added webhook support for shipment tracking

Version 1.1.0 (2023-12-01)
Initial release with order and document management

Basic compliance checking

China Customs API integration

