🛠️ Скрипты и инструменты

> **Утилиты для развертывания и управления системой**

## Быстрая установка

### Требования:
- Docker 20+
- Docker Compose 2+
- 4GB+ RAM
- 20GB+ свободного места

### Установка за 5 минут:
```bash
# Скачайте репозиторий
git clone https://github.com/asialogistics/platform.git
cd platform

# Запустите установку
chmod +x setup.sh
./setup.sh

# Система будет доступна по http://localhost:3000
Основные скрипты
Развертывание
setup.sh - автоматическая установка

docker-compose.yml - контейнеризация всех сервисов

deploy-prod.sh - развертывание в продакшен

Мониторинг
monitor-services.sh - проверка состояния сервисов

logs.sh - просмотр логов

backup.sh - резервное копирование

Утилиты
import-data.sh - импорт тестовых данных

health-check.sh - проверка здоровья системы

update.sh - обновление системы

Docker Compose
Основной файл docker-compose.yml включает:

Frontend - Vue.js приложение

Backend - Node.js API

Database - PostgreSQL

Cache - Redis

Blockchain - Hyperledger Fabric

AI Service - Python микросервис

Мониторинг
Система включает встроенный мониторинг:

Metrics - Prometheus

Dashboards - Grafana

Logging - ELK Stack

Alerts - автоматические уведомления

Безопасность
Автоматическое обновление безопасности

SSL сертификаты через Let's Encrypt

Firewall конфигурация

Регулярные security аудиты

text

## 🐳 **Создаем docker-compose.yml:**

```yaml
version: '3.8'

services:
  # Frontend приложение
  frontend:
    image: asialogistics/frontend:latest
    ports:
      - "3000:80"
    environment:
      - API_URL=http://backend:8000
    depends_on:
      - backend

  # Backend API
  backend:
    image: asialogistics/backend:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@database:5432/asialogistics
      - REDIS_URL=redis://cache:6379
      - BLOCKCHAIN_URL=fabric://blockchain:7054
    depends_on:
      - database
      - cache
      - blockchain

  # База данных
  database:
    image: postgres:14
    environment:
      - POSTGRES_DB=asialogistics
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - db_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Кэш Redis
  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # Блокчейн сеть
  blockchain:
    image: hyperledger/fabric-peer:2.4
    ports:
      - "7054:7054"
    environment:
      - CORE_PEER_ID=blockchain-peer
      - CORE_PEER_ADDRESS=blockchain:7054

  # AI сервис
  ai-service:
    image: asialogistics/ai-service:latest
    ports:
      - "5000:5000"
    environment:
      - MODEL_PATH=/app/models

volumes:
  db_data:
