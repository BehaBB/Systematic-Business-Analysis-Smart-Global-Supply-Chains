# 🗃️ Схемы базы данных

## Основные таблицы

### Таблица: shipments (грузы)
```sql
CREATE TABLE shipments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tracking_number VARCHAR(50) UNIQUE NOT NULL,
    sender_company_id UUID NOT NULL REFERENCES companies(id),
    receiver_company_id UUID NOT NULL REFERENCES companies(id),
    description TEXT,
    weight_kg DECIMAL(10,2),
    volume_m3 DECIMAL(10,3),
    status shipment_status NOT NULL DEFAULT 'created',
    blockchain_hash VARCHAR(255),
    estimated_delivery TIMESTAMP,
    actual_delivery TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
Таблица: shipment_events (события груза)
sql
CREATE TABLE shipment_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shipment_id UUID NOT NULL REFERENCES shipments(id),
    event_type event_type NOT NULL,
    location VARCHAR(255),
    description TEXT,
    temperature DECIMAL(5,2),
    humidity DECIMAL(5,2),
    recorded_at TIMESTAMP DEFAULT NOW(),
    blockchain_tx_hash VARCHAR(255)
);
Таблица: customs_declarations (таможенные декларации)
sql
CREATE TABLE customs_declarations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shipment_id UUID NOT NULL REFERENCES shipments(id),
    declaration_number VARCHAR(100) UNIQUE,
    hs_code VARCHAR(20),
    customs_value DECIMAL(15,2),
    customs_duty DECIMAL(15,2),
    vat DECIMAL(15,2),
    status customs_status NOT NULL DEFAULT 'draft',
    submitted_at TIMESTAMP,
    approved_at TIMESTAMP,
    ftc_response JSONB
);
Индексы для оптимизации
sql
-- Для быстрого поиска по трек-номерам
CREATE INDEX idx_shipments_tracking ON shipments(tracking_number);

-- Для фильтрации по статусу
CREATE INDEX idx_shipments_status ON shipments(status);

-- Для поиска событий по грузу
CREATE INDEX idx_shipment_events_shipment ON shipment_events(shipment_id);

-- Для временных запросов
CREATE INDEX idx_shipments_dates ON shipments(created_at, estimated_delivery);
Миграции базы данных
Используется Flyway для управления миграциями:

V1__Initial_schema.sql

V2__Add_customs_tables.sql

V3__Add_iot_data.sql

text

## 🔌 **Создаем api/api-specification.md:**

```markdown
# 🔌 Спецификация API

## Базовые настройки

### Base URL
https://api.asialogistics.ru/v1

text

### Аутентификация
```http
Authorization: Bearer {jwt_token}
Форматы данных
Request/Response: JSON

Кодировка: UTF-8

Язык: Поддержка русской и китайской локали

Основные эндпоинты
Shipments API
http
GET    /shipments           # Список грузов
POST   /shipments           # Создать груз
GET    /shipments/{id}      # Детали груза
PUT    /shipments/{id}      # Обновить груз
GET    /shipments/{id}/events # События груза
Customs API
http
POST   /customs/declarations    # Создать декларацию
PUT    /customs/declarations/{id} # Обновить декларацию
POST   /customs/declarations/{id}/submit # Отправить в ФТС
Blockchain API
http
GET    /blockchain/transactions/{hash} # Информация о транзакции
POST   /blockchain/events             # Записать событие в блокчейн
Пример запроса
json
{
  "shipment": {
    "tracking_number": "ASIA2024001",
    "sender_company_id": "comp-12345",
    "receiver_company_id": "comp-67890",
    "description": "Электронные компоненты",
    "weight_kg": 500,
    "volume_m3": 2.5
  }
}
text

## 🎨 **Создаем ui-ux/wireframes.md:**

```markdown
# 🎨 Вайрфреймы интерфейса

## Главный дашборд
┌─────────────────────────────────────────────────────┐
│ 🏠 Asia Logistics • Дашборд [👤 User] │
├─────────────────────────────────────────────────────┤
│ 📊 Ключевые метрики │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│ │ 150 │ │ 85% │ │ 2.1д │ │ 98% │ │
│ │ Грузов │ │ В срок │ │ Ср.время│ │Успешных │ │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
│ │
│ 🗺️ Карта перемещений грузов │
│ ┌─────────────────────────────────────────────────┐ │
│ │ │ │
│ │ [Иконки грузов на карте] │ │
│ │ │ │
│ └─────────────────────────────────────────────────┘ │
│ │
│ 📋 Последние грузы [➕ Новый] │
│ ┌─────┬────────────┬──────────┬────────┬──────────┐ │
│ │Трек │ Отправитель│ Статус │ Срок │ Действия │ │
│ ├─────┼────────────┼──────────┼────────┼──────────┤ │
│ │A001 │ Huawei │ 🟢 В пути│ 2 дня │ [👁️] │ │
│ │A002 │ Xiaomi │ 🟡 Таможня│ 1 день│ [👁️] │ │
│ └─────┴────────────┴──────────┴────────┴──────────┘ │
└─────────────────────────────────────────────────────┘

text

## Детали груза
┌─────────────────────────────────────────────────────┐
│ ← Asia Logistics • Груз ASIA2024001 [🖨️] [📤] │
├─────────────────────────────────────────────────────┤
│ 📦 Основная информация │
│ • Трек-номер: ASIA2024001 │
│ • Статус: 🟢 В пути │
│ • Отправитель: Huawei Technologies (Китай) │
│ • Получатель: Asia Logistics (Улан-Удэ) │
│ │
│ 🗺️ Маршрут и прогресс │
│ Харбин ────✅───▶ Кяхта ────🟡───▶ Улан-Удэ ──⚪──▶ │
│ │
│ 📋 История событий │
│ ┌─────────────────────────────────────────────────┐ │
│ │ 2024-01-15 10:30 📍 Покинул склад в Харбине │ │
│ │ 2024-01-16 14:20 🛃 На таможне в Кяхте │ │
│ │ 2024-01-16 15:00 🌡️ Температура: +5°C │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘

text

## Мобильный интерфейс

Адаптивный дизайн для:
- **Водителей** - упрощенный трекинг и сканирование
- **Менеджеров** - уведомления и быстрый доступ
- **Клиентов** - отслеживание своих грузов
