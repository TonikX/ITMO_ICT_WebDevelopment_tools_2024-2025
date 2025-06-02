#!/bin/bash

echo "🚀 Запуск Hockey API с Docker"
echo "==============================="

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен!"
    exit 1
fi

# Создаем .env если не существует
if [ ! -f .env ]; then
    echo "📝 Создание .env файла..."
    cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://postgres:tochange@postgres:5432/hockey_db
DB_HOST=postgres
DB_NAME=hockey_db
DB_USER=postgres
DB_PASSWORD=tochange
REDIS_URL=redis://redis:6379
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080
DEBUG=True
ENVIRONMENT=development
PARSER_URL=http://parser:8001
EOF
fi

# Создаем директории для uploads
echo "📁 Создание директорий..."
mkdir -p uploads/player_photos
mkdir -p uploads/player_certificates
mkdir -p uploads/team_logos

# Останавливаем предыдущие контейнеры
echo "🛑 Остановка предыдущих контейнеров..."
docker-compose down

# Собираем образы
echo "🔨 Сборка Docker образов..."
docker-compose build

# Запускаем сервисы
echo "🚀 Запуск сервисов..."
docker-compose up -d

# Ждем запуска PostgreSQL
echo "⏳ Ожидание запуска PostgreSQL..."
sleep 10

# Проверяем статус
echo "📊 Проверка статуса сервисов..."
docker-compose ps

echo ""
echo "✅ Сервисы запущены!"
echo ""
echo "🌐 Доступные URL:"
echo "   FastAPI:     http://localhost:8000"
echo "   Swagger:     http://localhost:8000/docs"
echo "   Parser:      http://localhost:8001"
echo "   Flower:      http://localhost:5555"
echo ""
echo "🔑 Данные для входа:"
echo "   Логин:       admin"
echo "   Пароль:      admin123"
echo ""
echo "📋 Полезные команды:"
echo "   make logs           - Показать логи"
echo "   make status         - Статус контейнеров"
echo "   make down           - Остановить сервисы"
echo "   make restart        - Перезапустить сервисы"
echo "   make test-api       - Тестировать API"
echo ""
echo "🧪 Тестирование API:"
echo "   curl http://localhost:8000/health"
echo "   curl http://localhost:8001/health"
echo ""

# Тестируем API
echo "🔍 Тестирование сервисов..."
sleep 5

if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ FastAPI работает"
else
    echo "❌ FastAPI недоступен"
fi

if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ Parser работает"
else
    echo "❌ Parser недоступен"
fi

echo ""
echo "🎉 Готово! Можете начинать работу с API"