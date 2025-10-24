# 🖱️ Кликабельный прототип

## Обзор прототипа
Интерактивный прототип системы Asia Logistics, демонстрирующий ключевые пользовательские сценарии через кликабельные макеты.

## Ссылки на прототипы

### Figma Prototype (Основной)
**🔗 Ссылка:** `https://www.figma.com/proto/ASIALOGISTICS2024`

**Функциональность:**
- 📊 **Главный дашборд** - обзор операций
- 📦 **Управление грузами** - создание и отслеживание
- 🗺️ **Карта перемещений** - реальное время
- 📱 **Мобильная версия** - для водителей

### InVision Prototype (Альтернативный)
**🔗 Ссылка:** `https://invis.io/ASIA-LOGISTICS-PROTO`

## Ключевые сценарии прототипа

### Сценарий 1: Создание нового груза
Главный дашборд → Кнопка "Новый груз"

Шаг 1: Основная информация

Выбор отправителя (Huawei, Xiaomi, BYD)

Выбор получателя

Описание груза

Вес и объем

Шаг 2: Товарные позиции

AI-подбор кодов ТН ВЭД

Автозаполнение описания

Шаг 3: Маршрут

AI-оптимизация пути

Расчет сроков

Шаг 4: Подтверждение

Генерация трек-номера

Отправка уведомлений

text

### Сценарий 2: Отслеживание груза
Поисковая строка → Ввод ASIA2024001

Страница деталей груза:

Визуализация маршрута

История событий

IoT данные (температура)

Таможенный статус

Уведомления о изменениях статуса

text

### Сценарий 3: Таможенное оформление
Список грузов → Выбор груза на таможне

AI-ассистент:

Автозаполнение декларации

Расчет пошлин

Проверка документов

Интеграция с ФТС:

Электронная подача

Отслеживание статуса

text

## Интерактивные элементы

### Кликабельные зоны главного дашборда
```html
<!-- Панель метрик -->
<div class="metric-card" onclick="showShipmentsByStatus('active')">
    <div class="metric-value">150</div>
    <div class="metric-label">Активных грузов</div>
</div>

<!-- Карта грузов -->
<div class="map-marker" data-shipment="ASIA2024001" 
     onclick="showShipmentDetails('ASIA2024001')">
    🚚
</div>

<!-- Таблица грузов -->
<tr onclick="openShipmentDetails('ASIA2024001')">
    <td>ASIA2024001</td>
    <td>Huawei</td>
    <td>🟢 В пути</td>
</tr>
Навигация между экранами
javascript
// Переход к созданию груза
function createNewShipment() {
    showScreen('shipment-create-step1');
}

// Пошаговая форма
function nextStep(currentStep) {
    hideScreen(`shipment-create-step${currentStep}`);
    showScreen(`shipment-create-step${currentStep + 1}`);
}

// Быстрый поиск
function quickSearch(trackingNumber) {
    if (trackingNumber) {
        showScreen(`shipment-details-${trackingNumber}`);
    }
}
Тестовые данные для прототипа
Демо-груз 1: ASIA2024001
json
{
  "trackingNumber": "ASIA2024001",
  "status": "in_transit",
  "sender": "Huawei Technologies",
  "receiver": "Asia Logistics Ulan-Ude",
  "route": ["Harbin", "Manchuria", "Kyakhta", "Ulan-Ude"],
  "currentLocation": "Kyakhta border",
  "temperature": "+5°C",
  "eta": "2024-01-19 14:00"
}
Демо-груз 2: ASIA2024002
json
{
  "trackingNumber": "ASIA2024002",
  "status": "customs_check",
  "sender": "Xiaomi Corporation",
  "receiver": "Irkutsk Electronics",
  "route": ["Beijing", "Zabaikalsk", "Irkutsk"],
  "currentLocation": "Zabaikalsk customs",
  "temperature": "+3°C",
  "eta": "2024-01-20 10:00"
}
Инструкция по тестированию
Для менеджеров:
Создание груза: Дашборд → "Новый груз" → Заполнить форму

Отслеживание: Поиск → ASIA2024001 → Просмотр деталей

Таможенное оформление: Грузы → Выбрать → "Таможня" → Заполнить декларацию

Для водителей:
Принятие груза: Уведомление → "Принять" → Сканирование QR

Обновление статуса: В пути → "Прибыл на таможню" → Фото документов

Завершение: "Доставлен" → Электронная подпись получателя

Для клиентов:
Отслеживание: Главная → Ввести трек-номер → Просмотр статуса

Уведомления: Push-сообщения о ключевых событиях

Документы: Скачивание накладных и деклараций

Обратная связь по прототипу
Вопросы для тестировщиков:
❓ Насколько интуитивна навигация?

❓ Удобно ли заполнять формы?

❓ Достаточно ли информации на экранах?

❓ Какие функции отсутствуют?

Каналы обратной связи:
📧 Email: prototype-feedback@asialogistics.ru

💬 Slack: #asia-logistics-prototype

📋 Google Forms: Анкета обратной связи

text

## 🔧 **Создаем prototypes/technical-prototype.md:**

```markdown
# 🔧 Технический прототип

## Обзор технической реализации
Рабочий прототип системы с реальной бизнес-логикой, интегрированными сервисами и демонстрационными данными.

## Архитектура прототипа

### Микросервисная структура
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Frontend │ │ API Gateway │ │ Auth Service │
│ Vue.js SPA │◄──►│ Node.js │◄──►│ JWT Tokens │
└─────────────────┘ └─────────────────┘ └─────────────────┘
│
┌──────────────┼──────────────┐
│ │ │
┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
│ Logistics │ │ AI │ │ Blockchain│
│ Service │ │ Service │ │ Service │
│ Node.js │ │ Python │ │ Go │
└───────────┘ └───────────┘ └───────────┘

text

## Установка и запуск

### Предварительные требования
```bash
# Проверка установленных компонентов
node --version        # v18+
python --version      # 3.9+
docker --version      # 20+
docker-compose --version
Локальный запуск
bash
# 1. Клонирование репозитория
git clone https://github.com/asialogistics/prototype.git
cd prototype

# 2. Запуск инфраструктуры
docker-compose up -d

# 3. Установка зависимостей
cd backend && npm install
cd ../frontend && npm install

# 4. Запуск сервисов
npm run dev:backend    # Запуск бэкенда
npm run dev:frontend   # Запуск фронтенда
Ключевые endpoints прототипа
Аутентификация
javascript
// POST /api/auth/login
{
  "email": "demo@asialogistics.ru",
  "password": "demo123"
}

// Response
{
  "token": "eyJhbGci...",
  "user": {
    "id": "user-1",
    "email": "demo@asialogistics.ru",
    "role": "manager"
  }
}
Управление грузами
javascript
// GET /api/shipments
// Получение списка грузов с пагинацией

// POST /api/shipments
// Создание нового груза
{
  "sender": "Huawei Technologies",
  "receiver": "Asia Logistics Ulan-Ude",
  "description": "Электронные компоненты",
  "weight": 500
}

// GET /api/shipments/ASIA2024001
// Получение деталей груза

// PUT /api/shipments/ASIA2024001/status
// Обновление статуса
{
  "status": "customs_cleared",
  "location": "Kyakhta border"
}
AI сервисы
javascript
// POST /api/ai/predict-delivery
// Прогноз времени доставки
{
  "route": "Harbin-UlanUde",
  "productType": "electronics",
  "season": "winter"
}

// POST /api/ai/optimize-route
// Оптимизация маршрута
{
  "points": ["Harbin", "Manchuria", "Kyakhta", "UlanUde"]
}
Демонстрационные данные
База данных прототипа
sql
-- Таблица грузов
INSERT INTO shipments (tracking_number, sender, receiver, status) VALUES
('ASIA2024001', 'Huawei', 'Asia Logistics', 'in_transit'),
('ASIA2024002', 'Xiaomi', 'Irkutsk Electronics', 'customs_check'),
('ASIA2024003', 'BYD Auto', 'Novosibirsk Dealer', 'delivered');

-- Таблица событий
INSERT INTO shipment_events (shipment_id, event_type, location) VALUES
(1, 'departed', 'Harbin, China'),
(1, 'border_crossing', 'Manchuria border'),
(1, 'customs_check', 'Kyakhta customs');
Mock сервисы для демо
javascript
// Mock ФТС API для таможенного оформления
app.post('/mock/fts/declaration', (req, res) => {
  // Имитация обработки декларации
  setTimeout(() => {
    res.json({
      declaration_number: `1070${Date.now()}`,
      status: 'accepted',
      processing_time: '2 hours'
    });
  }, 2000);
});

// Mock IoT данные
app.get('/mock/iot/sensor/:shipmentId', (req, res) => {
  const temperature = 2 + Math.random() * 6; // +2°C to +8°C
  res.json({
    temperature: temperature.toFixed(1),
    humidity: (40 + Math.random() * 20).toFixed(1),
    battery: (80 + Math.random() * 20).toFixed(1)
  });
});
Интеграции прототипа
Блокчейн интеграция
javascript
// Hyperledger Fabric client
const fabricClient = new FabricClient({
  channel: 'asiachannel',
  chaincode: 'shipment',
  user: 'admin'
});

// Запись события в блокчейн
async function recordBlockchainEvent(trackingNumber, event) {
  try {
    await fabricClient.submitTransaction('RecordEvent', 
      trackingNumber, 
      JSON.stringify(event)
    );
    console.log('✅ Событие записано в блокчейн');
  } catch (error) {
    console.log('⚠️  Блокчейн недоступен, используется локальная запись');
    // Fallback на базу данных
  }
}
AI сервисы интеграция
python
# Flask сервер для AI моделей
from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)
model = joblib.load('delivery_time_model.pkl')

@app.route('/ai/predict', methods=['POST'])
def predict_delivery_time():
    data = request.json
    prediction = model.predict([[
        data['distance'],
        data['border_crossings'], 
        data['season_encoded']
    ]])
    return jsonify({'predicted_days': prediction[0]})
Тестирование функциональности
Автоматические тесты
bash
# Запуск тестов
npm test

# Тесты API
npm run test:api

# Тесты UI  
npm run test:ui

# Интеграционные тесты
npm run test:integration
Ручное тестирование сценариев
Сценарий 1: Полный цикл доставки

bash
# 1. Создание груза
curl -X POST http://localhost:3000/api/shipments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sender": "Huawei", "receiver": "Asia Logistics", "weight": 500}'

# 2. Обновление статусов
curl -X PUT http://localhost:3000/api/shipments/ASIA2024001/status \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status": "in_transit", "location": "Harbin"}'

# 3. Завершение доставки
curl -X PUT http://localhost:3000/api/shipments/ASIA2024001/status \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status": "delivered", "location": "Ulan-Ude"}'
Сценарий 2: AI прогнозирование

bash
# Прогноз времени доставки
curl -X POST http://localhost:3000/api/ai/predict-delivery \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"route": "Harbin-UlanUde", "productType": "electronics"}'
Мониторинг и логи
Логирование
javascript
// Структурированные логи
logger.info('Shipment created', {
  trackingNumber: 'ASIA2024001',
  userId: 'user-123',
  timestamp: new Date().toISOString()
});

logger.error('Blockchain connection failed', {
  error: error.message,
  service: 'fabric-client'
});
Метрики производительности
bash
# Просмотр метрик
curl http://localhost:3000/metrics

# Health check
curl http://localhost:3000/health
Деплой и демонстрация
Демо окружение
🔗 URL: https://demo.asialogistics.ru

Доступы:

Менеджер: manager@demo.ru / demo123

Водитель: driver@demo.ru / demo123

Клиент: client@demo.ru / demo123

Продакшен готовность
✅ Docker контейнеризация

✅ Environment переменные

✅ Health checks

✅ Мониторинг и логи

✅ Автоматическое тестирование

