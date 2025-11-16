# API Documentation
## Baikal Fish Processing Plant Digital System

## Base Information

**Base URL:** `https://api.baikal-fish.ru/v1`

**Authentication:** Bearer Token
**Rate Limit:** 1000 requests per hour per API key

## Authentication

### Get Access Token

```http
POST /auth/token
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
Production API
Get Current Production Metrics
GET /production/current
Authorization: Bearer {token}
Response:
{
  "oee": 80.1,
  "availability": 92.5,
  "performance": 88.3,
  "quality": 96.2,
  "current_output": 8450,
  "target_output": 9000,
  "status": "running"
}
Submit Production Data
POST /production/batches
Authorization: Bearer {token}
Content-Type: application/json

{
  "batch_id": "BATCH-2024-001",
  "product_type": "smoked_omul",
  "start_time": "2024-01-15T08:00:00Z",
  "quantity": 1200,
  "equipment_id": "smokehouse_2"
}
Quality API
Submit Quality Measurements
POST /quality/measurements
Authorization: Bearer {token}
Content-Type: application/json

{
  "batch_id": "BATCH-2024-001",
  "parameter": "temperature",
  "value": 3.2,
  "unit": "celsius",
  "measured_at": "2024-01-15T10:30:00Z"
}
Get Quality Metrics
GET /quality/metrics?batch_id=BATCH-2024-001
Authorization: Bearer {token}
GET /quality/metrics?batch_id=BATCH-2024-001
Authorization: Bearer {token}
