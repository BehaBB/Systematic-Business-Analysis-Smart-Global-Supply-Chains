# 🔌 Эндпоинты API

## Аутентификация

### POST /auth/login
**Авторизация пользователя**
```http
POST /auth/login
Content-Type: application/json

{
  "email": "manager@asialogistics.ru",
  "password": "********"
}
Response:

json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-123",
    "email": "manager@asialogistics.ru",
    "role": "manager",
    "company_id": "comp-789"
  }
}
Управление грузами
GET /shipments
Получить список грузов с фильтрацией

http
GET /shipments?status=in_transit&page=1&limit=20
Authorization: Bearer {token}
POST /shipments
Создать новый груз

http
POST /shipments
Authorization: Bearer {token}
Content-Type: application/json

{
  "tracking_number": "ASIA2024001",
  "sender_company_id": "comp-123",
  "receiver_company_id": "comp-456",
  "description": "Электронные компоненты",
  "weight_kg": 500,
  "items": [
    {
      "description": "Микропроцессоры",
      "quantity": 1000,
      "value_usd": 50000
    }
  ]
}
GET /shipments/{id}/events
Получить события по грузу

http
GET /shipments/550e8400-e29b-41d4-a716-446655440000/events
Authorization: Bearer {token}
Таможенные операции
POST /customs/declarations
Создать таможенную декларацию

http
POST /customs/declarations
Authorization: Bearer {token}
Content-Type: application/json

{
  "shipment_id": "550e8400-e29b-41d4-a716-446655440000",
  "items": [
    {
      "hs_code": "8542310000",
      "description": "Микропроцессоры",
      "quantity": 1000,
      "customs_value": 50000
    }
  ]
}
POST /customs/declarations/{id}/submit
Отправить декларацию в ФТС

http
POST /customs/declarations/decl-123/submit
Authorization: Bearer {token}
AI сервисы
POST /ai/forecast
Получить прогноз спроса

http
POST /ai/forecast
Authorization: Bearer {token}
Content-Type: application/json

{
  "product_category": "electronics",
  "region": "siberia",
  "period_months": 3
}
POST /ai/optimize-route
Оптимизировать маршрут

http
POST /ai/optimize-route
Authorization: Bearer {token}
Content-Type: application/json

{
  "origin": "Harbin, China",
  "destination": "Irkutsk, Russia",
  "constraints": {
    "max_days": 14,
    "temperature_sensitive": true
  }
}
Блокчейн операции
GET /blockchain/transactions/{hash}
Получить информацию о транзакции

http
GET /blockchain/transactions/0x1234abcd...
Authorization: Bearer {token}
POST /blockchain/events
Записать событие в блокчейн

http
POST /blockchain/events
Authorization: Bearer {token}
Content-Type: application/json

{
  "shipment_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "customs_cleared",
  "location": "Kyakhta border",
  "description": "Таможенное оформление завершено"
}
Обработка ошибок
Стандартный формат ошибки:

json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Неверные данные запроса",
    "details": {
      "tracking_number": "Обязательное поле"
    }
  }
}
Коды ошибок:

AUTH_REQUIRED - Требуется аутентификация

PERMISSION_DENIED - Недостаточно прав

VALIDATION_ERROR - Ошибка валидации данных

SHIPMENT_NOT_FOUND - Груз не найден

BLOCKCHAIN_ERROR - Ошибка блокчейна

text

## 🎨 **Создаем ui-ux/user-interface.md:**

```markdown
# 🎨 Интерфейс пользователя

## Дизайн-система

### Цветовая палитра
```css
/* Основные цвета */
--primary: #1a365d;      /* Темно-синий - доверие */
--secondary: #e53e3e;    /* Красный - срочность */
--success: #38a169;      /* Зеленый - успех */
--warning: #d69e2e;      /* Желтый - предупреждение */

/* Нейтральные цвета */
--gray-50: #f7fafc;
--gray-100: #edf2f7;
--gray-800: #2d3748;
Типографика
Шрифт: Inter (кириллица + латиница)

Размеры: 14px (базовый), 16px (текст), 24px (заголовки)

Поддержка китайских иероглифов: Noto Sans SC

Компоненты интерфейса
Кнопки
html
<!-- Основная кнопка -->
<button class="btn btn-primary">Создать груз</button>

<!-- Вторичная кнопка -->
<button class="btn btn-secondary">Отмена</button>

<!-- Кнопка с иконкой -->
<button class="btn btn-icon">
  <i class="icon-plus"></i>
  Добавить
</button>
Карточки
html
<div class="card">
  <div class="card-header">
    <h3>Груз ASIA2024001</h3>
    <span class="status-badge status-in-transit">В пути</span>
  </div>
  <div class="card-body">
    <p><strong>От:</strong> Huawei, Китай</p>
    <p><strong>Кому:</strong> Asia Logistics, Улан-Удэ</p>
  </div>
</div>
Страницы интерфейса
Главный дашборд
Назначение: Обзор всех операций и ключевых метрик

Компоненты:

📊 Панель метрик - ключевые KPI

🗺️ Интерактивная карта - отслеживание грузов в реальном времени

📋 Таблица последних грузов - быстрый доступ

🔔 Панель уведомлений - важные события

Детали груза
Назначение: Подробная информация о конкретном грузе

Секции:

📦 Основная информация - трек-номер, статус, стороны

🗺️ Визуализация маршрута - прогресс на карте

📋 История событий - хронология перемещений

🌡️ Данные IoT - температура, влажность

🛃 Таможенная информация - статус декларации

Создание груза
Назначение: Добавление нового груза в систему

Шаги:

Основная информация - отправитель, получатель, описание

Детали товара - позиции, стоимость, вес

Маршрут - точки отправки и доставки

Подтверждение - проверка и создание

Таможенный модуль
Назначение: Управление таможенным оформлением

Функции:

🤖 AI-ассистент - автоматическое заполнение деклараций

📄 Шаблоны документов - быстрая подготовка

🔄 Интеграция с ФТС - электронная подача

📊 Отслеживание статуса - мониторинг обработки

Адаптивный дизайн
Breakpoints
css
/* Mobile */
@media (max-width: 768px) { ... }

/* Tablet */
@media (max-width: 1024px) { ... }

/* Desktop */
@media (min-width: 1025px) { ... }
Мобильные экраны
Упрощенная навигация - bottom navigation

Крупные кнопки - для touch-интерфейса

Оффлайн-режим - кэширование данных

Push-уведомления - важные события

Доступность (Accessibility)
ARIA-атрибуты для скринридеров

Высокий контраст для слабовидящих

Клавиатурная навигация для людей с ограниченной моторикой

Поддержка увеличения до 200% без потери функциональности

