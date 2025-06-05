import asyncio
import httpx
import json
import time
from typing import Dict, Any


class HockeyAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None

    async def authenticate(self, username: str = "admin", password: str = "admin123"):
        """Аутентификация в системе"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/token",
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                print(f"✅ Аутентификация успешна! Token: {self.token[:20]}...")
                return True
            else:
                print(f"❌ Ошибка аутентификации: {response.text}")
                return False

    def get_headers(self) -> Dict[str, str]:
        """Получение заголовков с токеном"""
        if not self.token:
            raise ValueError("Не выполнена аутентификация!")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def test_basic_endpoints(self):
        """Тестирование базовых эндпоинтов"""
        print("\n🔍 Тестирование базовых эндпоинтов")
        print("=" * 40)

        async with httpx.AsyncClient() as client:
            # Проверка основного API
            response = await client.get(f"{self.base_url}/health")
            print(f"FastAPI Health: {response.status_code} - {response.json()}")

            # Проверка парсера
            try:
                response = await client.get("http://localhost:8001/health")
                print(f"Parser Health: {response.status_code} - {response.json()}")
            except:
                print("Parser недоступен")

            # Профиль пользователя
            response = await client.get(
                f"{self.base_url}/users/profile",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                user_data = response.json()
                print(f"Пользователь: {user_data['username']} ({user_data['name']} {user_data['surname']})")

    async def test_parser_direct(self):
        """Тестирование прямого вызова парсера (Задача 2)"""
        print("\n🔄 Тестирование прямого парсера (Задача 2)")
        print("=" * 45)

        async with httpx.AsyncClient(timeout=60.0) as client:
            # Запуск парсинга
            parse_request = {
                "urls": [
                    "https://httpbin.org/json",  # Тестовый URL
                    "https://httpbin.org/user-agent"
                ],
                "parser_type": "async"
            }

            print("Запуск парсинга...")
            response = await client.post(
                f"{self.base_url}/parser/parse",
                headers=self.get_headers(),
                json=parse_request
            )

            if response.status_code == 200:
                task_data = response.json()
                task_id = task_data["task_id"]
                print(f"✅ Парсинг запущен! Task ID: {task_id}")

                # Мониторинг статуса
                for i in range(10):  # Максимум 10 попыток
                    await asyncio.sleep(2)

                    status_response = await client.get(
                        f"{self.base_url}/parser/status/{task_id}",
                        headers=self.get_headers()
                    )

                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"Статус: {status_data['status']} - {status_data['message']}")

                        if status_data['status'] in ['completed', 'failed']:
                            if status_data['status'] == 'completed':
                                print(f"✅ Парсинг завершен!")
                                print(f"   Команд: {status_data.get('teams_parsed', 0)}")
                                print(f"   Школ: {status_data.get('schools_created', 0)}")
                                print(f"   Турниров: {status_data.get('tournaments_created', 0)}")
                            break
                    else:
                        print(f"❌ Ошибка получения статуса: {status_response.text}")
                        break
            else:
                print(f"❌ Ошибка запуска парсинга: {response.text}")

    async def test_queue_system(self):
        """Тестирование системы очередей (Задача 3)"""
        print("\n⚡ Тестирование очередей Celery (Задача 3)")
        print("=" * 45)

        async with httpx.AsyncClient(timeout=60.0) as client:
            # Проверка статистики очередей
            response = await client.get(
                f"{self.base_url}/queue/stats",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                print("📊 Статистика очередей получена")

            # Запуск задачи в очереди
            queue_request = {
                "urls": [
                    "https://httpbin.org/json",
                    "https://httpbin.org/headers"
                ],
                "parser_type": "async"
            }

            print("Добавление задачи в очередь...")
            response = await client.post(
                f"{self.base_url}/queue/parse",
                headers=self.get_headers(),
                json=queue_request
            )

            if response.status_code == 200:
                task_data = response.json()
                task_id = task_data["task_id"]
                print(f"✅ Задача добавлена в очередь! Task ID: {task_id}")

                # Мониторинг статуса в очереди
                for i in range(15):  # Больше времени для очереди
                    await asyncio.sleep(3)

                    status_response = await client.get(
                        f"{self.base_url}/queue/status/{task_id}",
                        headers=self.get_headers()
                    )

                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"Статус очереди: {status_data['status']} - {status_data['message']}")

                        if status_data['status'] in ['success', 'failure']:
                            if status_data['status'] == 'success':
                                result = status_data.get('result', {})
                                print(f"✅ Задача из очереди завершена!")
                                print(f"   Результат: {result.get('status', 'unknown')}")
                                if 'teams_parsed' in result:
                                    print(f"   Команд: {result['teams_parsed']}")
                                    print(f"   Школ: {result['schools_created']}")
                                    print(f"   Турниров: {result['tournaments_created']}")
                            else:
                                print(f"❌ Задача завершилась с ошибкой: {status_data.get('message', 'Unknown error')}")
                            break
                    else:
                        print(f"❌ Ошибка получения статуса из очереди: {status_response.text}")
                        break

                # Проверка активных задач
                response = await client.get(
                    f"{self.base_url}/queue/active",
                    headers=self.get_headers()
                )
                if response.status_code == 200:
                    active_data = response.json()
                    print(f"📋 Активных задач: {len(active_data.get('active_tasks', {}))}")
            else:
                print(f"❌ Ошибка добавления в очередь: {response.text}")

    async def test_data_management(self):
        """Тестирование управления данными"""
        print("\n🏒 Тестирование управления данными")
        print("=" * 40)

        async with httpx.AsyncClient() as client:
            # Список команд
            response = await client.get(
                f"{self.base_url}/team/",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                teams = response.json()
                print(f"📋 Команд в системе: {len(teams)}")
                if teams:
                    print(f"   Первая команда: {teams[0].get('name', 'N/A')}")

            # Список игроков
            response = await client.get(f"{self.base_url}/players/")
            if response.status_code == 200:
                players = response.json()
                print(f"👥 Игроков в системе: {len(players)}")

            # Список турниров
            response = await client.get(
                f"{self.base_url}/tournaments/",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                tournaments = response.json()
                print(f"🏆 Турниров в системе: {len(tournaments)}")

    async def run_full_demo(self):
        """Запуск полной демонстрации"""
        print("🚀 Hockey API - Полная демонстрация")
        print("=" * 50)

        # Аутентификация
        if not await self.authenticate():
            return

        # Тестирование всех компонентов
        await self.test_basic_endpoints()
        await self.test_data_management()
        await self.test_parser_direct()
        await self.test_queue_system()

        print("\n🎉 Демонстрация завершена!")
        print("=" * 50)
        print("\n📋 Сводка возможностей:")
        print("✅ Docker контейнеризация")
        print("✅ Микросервисная архитектура")
        print("✅ HTTP интеграция сервисов")
        print("✅ Асинхронные очереди Celery")
        print("✅ Мониторинг и логирование")
        print("\n🌐 Доступные интерфейсы:")
        print("   API Docs:    http://localhost:8000/docs")
        print("   Flower:      http://localhost:5555")


async def main():
    """Главная функция"""
    client = HockeyAPIClient()
    await client.run_full_demo()


if __name__ == "__main__":
    print("Убедитесь, что все сервисы запущены:")
    print("  docker-compose up -d")
    print("  make up")
    print()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Демонстрация прервана пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("Проверьте, что все сервисы запущены и доступны")
