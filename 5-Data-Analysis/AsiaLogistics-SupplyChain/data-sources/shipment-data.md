# 📦 Данные поставок

## Структура данных о грузах

### Основная таблица shipments
```sql
CREATE TABLE shipments (
    id UUID PRIMARY KEY,
    tracking_number VARCHAR(50) UNIQUE,
    sender_company_id UUID,
    receiver_company_id UUID,
    product_category VARCHAR(100),
    weight_kg DECIMAL(10,2),
    volume_m3 DECIMAL(10,3),
    declared_value_usd DECIMAL(15,2),
    status shipment_status,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    estimated_delivery TIMESTAMP,
    actual_delivery TIMESTAMP
);
Таблица событий shipment_events
sql
CREATE TABLE shipment_events (
    id UUID PRIMARY KEY,
    shipment_id UUID REFERENCES shipments(id),
    event_type event_type,
    location VARCHAR(255),
    description TEXT,
    timestamp TIMESTAMP,
    temperature DECIMAL(5,2),
    humidity DECIMAL(5,2),
    blockchain_tx_hash VARCHAR(255)
);
Ключевые показатели
Временные метрики
python
# Расчет времени доставки
def calculate_delivery_time(shipment_id):
    shipment = get_shipment(shipment_id)
    created = shipment.created_at
    delivered = shipment.actual_delivery
    
    if delivered:
        return delivered - created
    return None

# Время на таможне
def calculate_customs_time(shipment_id):
    events = get_shipment_events(shipment_id)
    customs_events = [e for e in events if 'customs' in e.event_type]
    
    if len(customs_events) >= 2:
        start = min(e.timestamp for e in customs_events)
        end = max(e.timestamp for e in customs_events)
        return end - start
    return None
Категории товаров
python
product_categories = {
    'electronics': 'Электроника и компоненты',
    'automotive': 'Автозапчасти',
    'consumer_goods': 'Потребительские товары',
    'industrial': 'Промышленное оборудование',
    'pharmaceutical': 'Фармацевтика',
    'food': 'Продукты питания'
}
Примеры данных
Статистика за последний месяц
json
{
  "total_shipments": 150,
  "delivered_on_time": 128,
  "delayed": 22,
  "average_delivery_time_days": 4.2,
  "customs_clearance_hours_avg": 6.5,
  "temperature_violations": 3
}
Распределение по категориям
python
category_distribution = {
    'electronics': 45,
    'automotive': 32,
    'consumer_goods': 28,
    'industrial': 25,
    'pharmaceutical': 12,
    'food': 8
}
Источники данных
Внутренние системы:
ERP система - данные о заказах

Трекер GPS - местоположение грузов

IoT датчики - температура, влажность

Блокчейн - события и транзакции

Внешние интеграции:
ФТС России - таможенное оформление

Погодные сервисы - условия на маршруте

Картографические сервисы - расстояние и время

text

## 📊 **Создаем analytics/kpi-dashboard.md:**

```markdown
# 📊 KPI Дашборд

## Ключевые показатели эффективности

### Операционные KPI

#### 1. Время доставки
```python
delivery_time_kpis = {
    'average_delivery_days': 4.2,
    'median_delivery_days': 3.8,
    'p95_delivery_days': 6.1,
    'on_time_delivery_rate': 0.85  # 85%
}
2. Эффективность таможни
python
customs_kpis = {
    'average_clearance_hours': 6.5,
    'clearance_success_rate': 0.92,
    'documents_auto_processed': 0.78,
    'customs_duty_accuracy': 0.95
}
3. Качество перевозки
python
quality_kpis = {
    'temperature_compliance': 0.98,
    'damage_rate': 0.002,
    'customer_satisfaction_score': 4.7,
    'incident_free_deliveries': 0.96
}
Финансовые KPI
1. Экономические показатели
python
financial_kpis = {
    'cost_per_kg': 2.5,  # USD за кг
    'revenue_per_shipment': 1250,
    'profit_margin': 0.28,
    'fuel_efficiency_kmpl': 3.2
}
Визуализация на дашборде
Главный экран дашборда
text
┌─────────────────────────────────────────────────────────┐
│ Asia Logistics - KPI Dashboard               [📅 Jan]  │
├─────────────────────────────────────────────────────────┤
│ 📊 Key Metrics                                          │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│ │    85%      │ │    4.2d     │ │   98%       │         │
│ │  On-Time    │ │ Avg Delivery│ │ Compliance  │         │
│ │  Delivery   │ │   Time      │ │   Rate      │         │
│ └─────────────┘ └─────────────┘ └─────────────┘         │
│                                                         │
│ 📈 Delivery Time Trend                                  │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 6d ┤    █████████▊                                  │ │
│ │ 5d ┤  ██████████████▋                               │ │
│ │ 4d ┤███████████████████▌                            │ │
│ │ 3d ┤██████████████████████▍                         │ │
│ │ 2d ┤████████████████████████▊                       │ │
│ │    └───────────────────────────────────────────────── │
│ │     Jan  Feb  Mar  Apr  May  Jun                     │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ 🗺️ Route Efficiency                                    │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Route           │ Time  │ Cost  │ Reliability       │ │
│ ├─────────────────┼───────┼───────┼───────────────────┤ │
│ │ Harbin-UlanUde  │ 4.2d  │ $1250 │ 85%               │ │
│ │ Beijing-Irkutsk │ 5.1d  │ $1400 │ 78%               │ │
│ │ Shanghai-Chita  │ 6.3d  │ $1650 │ 72%               │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
Метрики в реальном времени
Текущие операции
python
real_time_metrics = {
    'active_shipments': 45,
    'at_customs': 12,
    'in_transit': 28,
    'delayed': 5,
    'temperature_alerts': 2
}
Производительность за сегодня
python
today_metrics = {
    'shipments_created': 8,
    'shipments_delivered': 6,
    'customs_cleared': 7,
    'incidents_reported': 1
}
Аналитические отчеты
Еженедельный анализ
python
weekly_report = {
    'week': '2024-01-15',
    'total_shipments': 42,
    'on_time_rate': 0.88,
    'average_cost': 1280,
    'top_performing_route': 'Harbin-UlanUde',
    'issues_identified': ['weather_delays', 'customs_documentation']
}
Сравнительный анализ
python
comparison_analysis = {
    'current_month_vs_previous': {
        'delivery_time_change': -0.3,  # улучшение на 0.3 дня
        'cost_change': -50,            # снижение на $50
        'satisfaction_change': +0.2    # улучшение на 0.2 балла
    }
}
Алерт-система
Критические метрики
python
alert_thresholds = {
    'delivery_time_p95': 7.0,     # дней
    'temperature_violation': 3,    # случаев в день
    'customs_delay_hours': 24,     # часов
    'damage_rate': 0.01,           # 1%
    'customer_complaints': 5       # в день
}
Автоматические уведомления
python
def check_alerts():
    if current_delivery_time > alert_thresholds['delivery_time_p95']:
        send_alert('HIGH_DELIVERY_TIME')
    
    if temperature_violations_today > alert_thresholds['temperature_violation']:
        send_alert('TEMPERATURE_ISSUES')
