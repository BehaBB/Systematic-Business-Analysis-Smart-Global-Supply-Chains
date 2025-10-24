#!/bin/bash

# Asia Logistics - Setup Script
echo "🚀 Starting Asia Logistics Platform Setup..."

# Check dependencies
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/database
mkdir -p data/logs
mkdir -p data/blockchain

# Pull latest images
echo "📥 Pulling Docker images..."
docker-compose pull

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

# Run initial setup
echo "⚙️ Running initial setup..."
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py create_default_user

echo "✅ Setup completed!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "🗄️ Database: localhost:5432"
echo ""
echo "📧 Default admin credentials:"
echo "   Email: admin@asialogistics.ru"
echo "   Password: admin123"
echo ""
echo "⚠️  Please change default passwords after first login!"
