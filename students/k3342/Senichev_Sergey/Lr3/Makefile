.PHONY: help build up down logs test clean

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build:
	docker-compose build

up: ## Запустить все сервисы
	docker-compose up -d

up-build: ## Собрать и запустить все сервисы
	docker-compose up -d --build

down: ## Остановить все сервисы
	docker-compose down

logs: ## Показать логи всех сервисов
	docker-compose logs -f

logs-app: ## Показать логи FastAPI приложения
	docker-compose logs -f app

logs-parser: ## Показать логи парсера
	docker-compose logs -f parser

logs-celery: ## Показать логи Celery воркера
	docker-compose logs -f celery-worker

test: ## Запустить тесты
	python run_tests.py

test-endpoints: ## Тестировать эндпоинты с помощью curl
	@echo "Testing Task Management API..."
	curl -X GET http://localhost:8000/ | jq .
	@echo "\nTesting Parser API..."
	curl -X GET http://localhost:8001/ | jq .
	@echo "\nTesting health endpoints..."
	curl -X GET http://localhost:8000/health | jq .
	curl -X GET http://localhost:8001/health | jq .

clean: ## Очистить Docker ресурсы
	docker-compose down -v
	docker system prune -f

restart: down up ## Перезапустить все сервисы

status: ## Показать статус сервисов
	docker-compose ps

shell-app: ## Подключиться к контейнеру приложения
	docker-compose exec app /bin/bash

shell-parser: ## Подключиться к контейнеру парсера
	docker-compose exec parser /bin/bash

db-shell: ## Подключиться к базе данных
	docker-compose exec postgres psql -U postgres -d lab_db

redis-cli: ## Подключиться к Redis
	docker-compose exec redis redis-cli

dev: ## Запустить в режиме разработки с перезагрузкой
	docker-compose -f docker-compose.yml up --build

prod: ## Запустить в продакшн режиме
	docker-compose -f docker-compose.yml up -d --build 