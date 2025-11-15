## 🎯 **Creating Data Models: AI BuryatMyasoprom**

```markdown
# Data Models: AI BuryatMyasoprom

## Core Entities

### Product Entity
```json
{
  "product_id": "UUID",
  "name": "String",
  "type": "beef|lamb|horse",
  "quality_grade": "A|B|C",
  "origin_farm": "UUID",
  "production_date": "DateTime",
  "expiry_date": "DateTime",
  "storage_requirements": {
    "min_temperature": "Float",
    "max_temperature": "Float",
    "humidity_range": "Object"
  }
}
Export Order Entity
json
{
  "order_id": "UUID",
  "customer_id": "UUID",
  "products": ["UUID"],
  "destination_country": "String",
  "export_date": "DateTime",
  "customs_status": "pending|submitted|approved|rejected",
  "documents": ["Document"],
  "tracking_info": "Object"
}
Supply Chain Event Entity
json
{
  "event_id": "UUID",
  "batch_id": "UUID",
  "event_type": "production|inspection|shipment|storage",
  "location": "GPS Coordinates",
  "timestamp": "DateTime",
  "temperature_readings": ["Float"],
  "quality_metrics": "Object",
  "responsible_party": "UUID",
  "blockchain_hash": "String"
}
Database Schema Design
Main Tables
products: Product master data

batches: Production batch tracking

orders: Export order management

documents: Customs document storage

supply_chain_events: Real-time monitoring data

regulations: Compliance rule database

users: System access control

Relationships
text
products (1) ──────── (M) batches
batches (1) ──────── (M) supply_chain_events
orders (1) ──────── (M) documents
regulations (M) ────── (M) products
API Data Models
Document Generation Request
typescript
interface DocumentRequest {
  order_id: string;
  product_list: Product[];
  exporter_details: CompanyInfo;
  importer_details: CompanyInfo;
  shipment_details: ShipmentInfo;
}
Quality Alert
typescript
interface QualityAlert {
  batch_id: string;
  alert_type: 'temperature' | 'humidity' | 'time_delay';
  severity: 'low' | 'medium' | 'high' | 'critical';
  current_value: number;
  threshold_value: number;
  timestamp: string;
  location: string;
}
Data Retention Policies
Transaction Data: 7 years (regulatory requirement)

Sensor Data: 2 years (analytics purposes)

Audit Logs: 10 years (compliance requirement)

User Sessions: 90 days (security best practice)

