.PHONY: build up down restart logs clean test

# Сборка всех образов
build:
	docker-compose build

# Запуск всех сервисов
up:
	docker-compose up -d

# Запуск с логами
up-logs:
	docker-compose up

# Остановка всех сервисов
down:
	docker-compose down

# Остановка с удалением volumes
down-volumes:
	docker-compose down -v

# Перезапуск всех сервисов
restart:
	docker-compose restart

# Просмотр логов
logs:
	docker-compose logs -f

# Логи конкретного сервиса
logs-fastapi:
	docker-compose logs -f fastapi

logs-parser:
	docker-compose logs -f parser

logs-postgres:
	docker-compose logs -f postgres

logs-redis:
	docker-compose logs -f redis

logs-celery:
	docker-compose logs -f celery_worker

# Очистка всех контейнеров и образов
clean:
	docker-compose down -v
	docker system prune -f
	docker volume prune -f

# Полная пересборка
rebuild:
	docker-compose down -v
	docker-compose build --no-cache
	docker-compose up -d

# Выполнение команд в контейнерах
shell-fastapi:
	docker-compose exec fastapi bash

shell-parser:
	docker-compose exec parser bash

shell-postgres:
	docker-compose exec postgres psql -U postgres -d hockey_db

shell-redis:
	docker-compose exec redis redis-cli

# Проверка статуса сервисов
status:
	docker-compose ps

# Тестирование API
test-api:
	curl -X GET http://localhost:8000/health

test-parser:
	curl -X GET http://localhost:8001/health

# Мониторинг Flower (Celery)
flower:
	@echo "Celery Flower доступен по адресу: http://localhost:5555"

# Инициализация базы данных
init-db:
	docker-compose exec postgres psql -U postgres -d hockey_db -f /docker-entrypoint-initdb.d/init.sql

# Помощь
help:
	@echo "Доступные команды:"
	@echo "  build         - Собрать все образы"
	@echo "  up            - Запустить все сервисы"
	@echo "  up-logs       - Запустить с показом логов"
	@echo "  down          - Остановить все сервисы"
	@echo "  down-volumes  - Остановить с удалением данных"
	@echo "  restart       - Перезапустить все сервисы"
	@echo "  logs          - Показать логи всех сервисов"
	@echo "  logs-*        - Показать логи конкретного сервиса"
	@echo "  clean         - Очистить все контейнеры и образы"
	@echo "  rebuild       - Полная пересборка"
	@echo "  shell-*       - Войти в контейнер"
	@echo "  status        - Статус контейнеров"
	@echo "  test-*        - Тестирование API"
	@echo "  flower        - Информация о Flower"
	@echo "  init-db       - Инициализация БД"