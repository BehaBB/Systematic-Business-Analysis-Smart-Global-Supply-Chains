# Data Models
## Baikal Fish Processing Plant Digital Transformation

## Core Database Schema

### 1. Production Domain

#### batches Table
```sql
CREATE TABLE batches (
    batch_id VARCHAR(50) PRIMARY KEY,
    product_type VARCHAR(20) NOT NULL,
    planned_quantity DECIMAL(10,2) NOT NULL,
    actual_quantity DECIMAL(10,2),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    equipment_used JSONB,
    status VARCHAR(20) DEFAULT 'PLANNED',
    yield_percentage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
production_schedules Table
sql
CREATE TABLE production_schedules (
    schedule_id VARCHAR(50) PRIMARY KEY,
    schedule_date DATE NOT NULL,
    shift_type VARCHAR(10) NOT NULL, -- MORNING, EVENING, NIGHT
    equipment_assignments JSONB NOT NULL,
    personnel_assignments JSONB NOT NULL,
    planned_output DECIMAL(10,2) NOT NULL,
    actual_output DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'DRAFT',
    created_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
2. Quality Domain
quality_checks Table
sql
CREATE TABLE quality_checks (
    check_id VARCHAR(50) PRIMARY KEY,
    batch_id VARCHAR(50) REFERENCES batches(batch_id),
    check_type VARCHAR(30) NOT NULL, -- RAW_MATERIAL, IN_PROCESS, FINAL
    inspector_id VARCHAR(50) NOT NULL,
    check_time TIMESTAMP NOT NULL,
    parameters JSONB NOT NULL, -- {appearance: 9, texture: 8, smell: 10}
    overall_score DECIMAL(3,1),
    status VARCHAR(20) NOT NULL, -- PASSED, FAILED, CONDITIONAL
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
laboratory_tests Table
sql
CREATE TABLE laboratory_tests (
    test_id VARCHAR(50) PRIMARY KEY,
    sample_id VARCHAR(50) NOT NULL,
    test_type VARCHAR(30) NOT NULL, -- BACTERIAL, CHEMICAL, PHYSICAL
    parameters JSONB NOT NULL, -- {total_bacteria: 1000, e_coli: 0}
    test_date TIMESTAMP NOT NULL,
    conducted_by VARCHAR(50) NOT NULL,
    results JSONB NOT NULL,
    compliance_status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
3. Inventory Domain
raw_materials Table
sql
CREATE TABLE raw_materials (
    material_id VARCHAR(50) PRIMARY KEY,
    fish_type VARCHAR(30) NOT NULL, -- OMUL, SIG, GRAYLING
    quantity DECIMAL(10,2) NOT NULL,
    unit VARCHAR(10) DEFAULT 'kg',
    received_date TIMESTAMP NOT NULL,
    supplier_id VARCHAR(50) NOT NULL,
    storage_temperature DECIMAL(4,1),
    freshness_grade VARCHAR(20), -- EXCELLENT, GOOD, FAIR
    location VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'AVAILABLE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
finished_products Table
sql
CREATE TABLE finished_products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_type VARCHAR(30) NOT NULL, -- SMOKED, FROZEN, DRIED
    fish_type VARCHAR(30) NOT NULL,
    batch_id VARCHAR(50) REFERENCES batches(batch_id),
    quantity DECIMAL(10,2) NOT NULL,
    unit VARCHAR(10) DEFAULT 'kg',
    production_date TIMESTAMP NOT NULL,
    expiry_date TIMESTAMP NOT NULL,
    storage_conditions JSONB, -- {temperature: -18, humidity: 70}
    location VARCHAR(50) NOT NULL,
    quality_grade VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
4. Equipment Domain
equipment Table
sql
CREATE TABLE equipment (
    equipment_id VARCHAR(50) PRIMARY KEY,
    equipment_name VARCHAR(100) NOT NULL,
    equipment_type VARCHAR(30) NOT NULL, -- SMOKER, FREEZER, PACKAGING
    status VARCHAR(20) DEFAULT 'OPERATIONAL',
    capacity DECIMAL(10,2),
    last_maintenance DATE,
    next_maintenance DATE,
    utilization_rate DECIMAL(5,2),
    location VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
maintenance_logs Table
sql
CREATE TABLE maintenance_logs (
    log_id VARCHAR(50) PRIMARY KEY,
    equipment_id VARCHAR(50) REFERENCES equipment(equipment_id),
    maintenance_type VARCHAR(30) NOT NULL, -- PREVENTIVE, CORRECTIVE
    description TEXT NOT NULL,
    performed_by VARCHAR(50) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    downtime_minutes INTEGER,
    parts_used JSONB,
    status VARCHAR(20) DEFAULT 'COMPLETED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
Data Relationships
erDiagram
    batches ||--o{ quality_checks : has
    batches ||--o{ finished_products : produces
    raw_materials }o--|| batches : consumed_by
    equipment ||--o{ batches : used_in
    equipment ||--o{ maintenance_logs : maintained_through
API Data Models
Production Schedule Request
python
class ProductionScheduleRequest(BaseModel):
    schedule_date: str
    shift_type: str
    available_equipment: List[str]
    available_personnel: List[str]
    raw_material_availability: Dict[str, float]
    product_demand: Dict[str, float]
Quality Check Data
python
class QualityCheckData(BaseModel):
    batch_id: str
    check_type: str
    parameters: Dict[str, Any]
    inspector_id: str
    check_time: datetime
Inventory Movement
python
class InventoryMovement(BaseModel):
    material_id: str
    movement_type: str  # RECEIPT, CONSUMPTION, TRANSFER
    quantity: float
    unit: str
    reference_id: str  # batch_id or transfer_id
    location: str
Data Validation Rules
Production Data Validation
python
PRODUCTION_RULES = {
    "batch_quantity": {
        "min": 0.1,
        "max": 10000.0,
        "unit": "kg"
    },
    "yield_percentage": {
        "min": 0.0,
        "max": 100.0
    },
    "equipment_utilization": {
        "min": 0.0,
        "max": 100.0
    }
}
Quality Data Validation
python
QUALITY_RULES = {
    "appearance_score": {
        "min": 0,
        "max": 10
    },
    "bacterial_count": {
        "max": 10000  # CFU/g
    },
    "temperature": {
        "min": -25.0,
        "max": 5.0
    }
}
Data Retention Policies
Operational Data
Production batches: 7 years

Quality records: 7 years (regulatory requirement)

Inventory transactions: 5 years

Equipment maintenance: 10 years

Analytical Data
Performance metrics: 3 years detailed, 10 years aggregated

Quality trends: 5 years

Production efficiency: 3 years

Data Migration Strategy
Phase 1: Historical Data Import
python
class DataMigrator:
    def migrate_historical_batches(self):
        # Import existing Excel production records
        pass
    
    def migrate_quality_data(self):
        # Convert paper quality logs to digital
        pass
    
    def migrate_inventory_records(self):
        # Import current inventory state
        pass
Phase 2: Data Cleansing
Remove duplicate records

Standardize measurement units

Validate data consistency

Fill missing required fields

Data Access Patterns
Frequent Reads
Current production schedule

Real-time inventory levels

Quality check results

Equipment status

Frequent Writes
Production progress updates

Quality inspection results

Inventory movements

Equipment utilization data

Batch Operations
Daily production reports

Weekly performance analytics

Monthly compliance reporting
