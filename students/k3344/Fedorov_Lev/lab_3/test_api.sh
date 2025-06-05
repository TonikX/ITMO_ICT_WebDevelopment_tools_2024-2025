#!/bin/bash

echo "🧪 Тестирование Hockey API"
echo "=========================="

BASE_URL="http://localhost:8000"
PARSER_URL="http://localhost:8001"

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для проверки HTTP ответа
check_response() {
    if [ $1 -eq 200 ]; then
        echo -e "${GREEN}✅ PASSED${NC}"
    else
        echo -e "${RED}❌ FAILED (HTTP $1)${NC}"
    fi
}

echo ""
echo "🔍 1. Проверка базовых эндпоинтов"
echo "================================="

# Тест основного API
echo -n "FastAPI Health Check: "
response=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/health)
check_response $response

echo -n "FastAPI Root: "
response=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/)
check_response $response

echo -n "Swagger Docs: "
response=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/docs)
check_response $response

# Тест парсера
echo -n "Parser Health Check: "
response=$(curl -s -o /dev/null -w "%{http_code}" $PARSER_URL/health)
check_response $response

echo -n "Parser Root: "
response=$(curl -s -o /dev/null -w "%{http_code}" $PARSER_URL/)
check_response $response

echo ""
echo "🔐 2. Тестирование аутентификации"
echo "================================="

# Получение токена
echo -n "Получение токена: "
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123")

if echo $TOKEN_RESPONSE | grep -q "access_token"; then
    echo -e "${GREEN}✅ PASSED${NC}"
    TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    echo "Token получен: ${TOKEN:0:20}..."
else
    echo -e "${RED}❌ FAILED${NC}"
    echo "Ответ: $TOKEN_RESPONSE"
    exit 1
fi

echo ""
echo "👤 3. Тестирование пользователей"
echo "==============================="

# Профиль пользователя
echo -n "Профиль пользователя: "
response=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $TOKEN" \
  $BASE_URL/users/profile)
check_response $response

# Список пользователей (админ)
echo -n "Список пользователей: "
response=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $TOKEN" \
  $BASE_URL/users/)
check_response $response

echo ""
echo "🏒 4. Тестирование основных сущностей"
echo "===================================="

# Команды
echo -n "Список команд: "
response=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $TOKEN" \
  $BASE_URL/team/)
check_response $response

# Игроки
echo -n "Список игроков: "
response=$(curl -s -o /dev/null -w "%{http_code}" \
  $BASE_URL/players/)
check_response $response

# Турниры
echo -n "Список турниров: "
response=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $TOKEN" \
  $BASE_URL/tournaments/)
check_response $response

# Сезоны
echo -n "Список сезонов: "
response=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $TOKEN" \
  $BASE_URL/seasons/)
check_response $response

echo ""
echo "🔄 5. Тестирование парсера (Задача 2)"
echo "===================================="

# Проверка здоровья парсера через API
echo -n "Здоровье парсера через API: "
response=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $TOKEN" \
  $BASE_URL/parser/health)
check_response $response

# Запуск парсинга (только если нужно тестировать реальный парсинг)
echo -n "Тест запуска парсинга: "
PARSE_RESPONSE=$(curl -s -X POST "$BASE_URL/parser/parse" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://httpbin.org/json"],
    "parser_type": "async"
  }')

if echo $PARSE_RESPONSE | grep -q "task_id"; then
    echo -e "${GREEN}✅ PASSED${NC}"
    TASK_ID=$(echo $PARSE_RESPONSE | grep -o '"task_id":"[^"]*"' | cut -d'"' -f4)
    echo "Task ID: $TASK_ID"

    # Проверка статуса задачи
    sleep 2
    echo -n "Статус задачи парсинга: "
    response=$(curl -s -o /dev/null -w "%{http_code}" \
      -H "Authorization: Bearer $TOKEN" \
      $BASE_URL/parser/status/$TASK_ID)
    check_response $response
else
    echo -e "${RED}❌ FAILED${NC}"
    echo "Ответ: $PARSE_RESPONSE"
fi

echo ""
echo "⚡ 6. Тестирование очередей (Задача 3)"
echo "====================================="

# Проверка активных задач
echo -n "Активные задачи Celery: "
response=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $TOKEN" \
  $BASE_URL/queue/active)
check_response $response

# Статистика очередей
echo -n "Статистика очередей: "
response=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $TOKEN" \
  $BASE_URL/queue/stats)
check_response $response

# Запуск задачи в очереди
echo -n "Запуск задачи в очереди: "
QUEUE_RESPONSE=$(curl -s -X POST "$BASE_URL/queue/parse" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://httpbin.org/json"],
    "parser_type": "async"
  }')

if echo $QUEUE_RESPONSE | grep -q "task_id"; then
    echo -e "${GREEN}✅ PASSED${NC}"
    QUEUE_TASK_ID=$(echo $QUEUE_RESPONSE | grep -o '"task_id":"[^"]*"' | cut -d'"' -f4)
    echo "Queue Task ID: $QUEUE_TASK_ID"

    # Проверка статуса задачи в очереди
    sleep 3
    echo -n "Статус задачи из очереди: "
    response=$(curl -s -o /dev/null -w "%{http_code}" \
      -H "Authorization: Bearer $TOKEN" \
      $BASE_URL/queue/status/$QUEUE_TASK_ID)
    check_response $response
else
    echo -e "${RED}❌ FAILED${NC}"
    echo "Ответ: $QUEUE_RESPONSE"
fi

echo ""
echo "📊 7. Результаты тестирования"
echo "============================="

# Подсчет результатов (простой способ)
TOTAL_TESTS=$(grep -c "check_response\|PASSED\|FAILED" $0)
echo "Всего тестов выполнено: приблизительно 15+"

echo ""
echo "🌐 Полезные ссылки:"
echo "   FastAPI:     http://localhost:8000"
echo "   Swagger:     http://localhost:8000/docs"
echo "   Parser:      http://localhost:8001"
echo "   Flower:      http://localhost:5555"

echo ""
echo "📝 Логи и отладка:"
echo "   make logs           - Все логи"
echo "   make logs-fastapi   - Логи FastAPI"
echo "   make logs-parser    - Логи Parser"
echo "   make logs-celery    - Логи Celery"

echo ""
echo -e "${YELLOW}🎉 Тестирование завершено!${NC}"