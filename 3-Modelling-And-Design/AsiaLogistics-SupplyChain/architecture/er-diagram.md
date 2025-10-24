# 🗃️ ER-диаграмма базы данных

## Основные сущности

### Пользователи (users)
users
├── id (UUID, PK)
├── email (VARCHAR)
├── phone (VARCHAR)
├── company_id (UUID, FK)
├── role (ENUM: admin, manager, driver)
└── created_at (TIMESTAMP)

text

### Компании (companies)
companies
├── id (UUID, PK)
├── name (VARCHAR)
├── country (ENUM: Russia, China)
├── tax_id (VARCHAR)
└── address (JSONB)

text

### Грузы (shipments)
shipments
├── id (UUID, PK)
├── tracking_number (VARCHAR)
├── sender_company_id (UUID, FK)
├── receiver_company_id (UUID, FK)
├── status (ENUM: created, in_transit, customs, delivered)
├── blockchain_hash (VARCHAR)
└── created_at (TIMESTAMP)

text

### Таможенные декларации (customs_declarations)
customs_declarations
├── id (UUID, PK)
├── shipment_id (UUID, FK)
├── declaration_number (VARCHAR)
├── status (ENUM: draft, submitted, approved)
├── customs_duty (DECIMAL)
└── submitted_at (TIMESTAMP)

text

## Связи между сущностями

- **companies** (1) ─────── (N) **users**
- **companies** (1) ─────── (N) **shipments** (как отправитель)
- **companies** (1) ─────── (N) **shipments** (как получатель)
- **shipments** (1) ─────── (1) **customs_declarations**
