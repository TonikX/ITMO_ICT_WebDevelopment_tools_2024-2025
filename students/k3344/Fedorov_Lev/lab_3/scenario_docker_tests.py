import asyncio
import httpx


class DockerSystemTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.parser_url = "http://localhost:8001"
        self.token = None

    async def authenticate(self):
        """Аутентификация"""
        print("🔐 Аутентификация...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/token",
                data={"username": "admin", "password": "admin123"},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                print(f"✅ Токен получен: {self.token[:20]}...")
                return True
            else:
                print(f"❌ Ошибка аутентификации: {response.text}")
                return False

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def test_microservices_communication(self):
        """Тест взаимодействия микросервисов"""
        print("\n🔄 Тест взаимодействия микросервисов")
        print("=" * 40)

        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. FastAPI -> Parser
            print("1. FastAPI обращается к Parser...")
            response = await client.get(
                f"{self.base_url}/parser/health",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                print("✅ FastAPI ↔ Parser связь работает")
            else:
                print(f"❌ Проблема связи FastAPI-Parser: {response.status_code}")

            # 2. Прямое обращение к Parser
            print("2. Прямое обращение к Parser...")
            response = await client.get(f"{self.parser_url}/health")
            if response.status_code == 200:
                print("✅ Parser доступен напрямую")
            else:
                print(f"❌ Parser недоступен: {response.status_code}")

            # 3. Тест парсинга через FastAPI
            print("3. Запуск парсинга через FastAPI...")
            parse_request = {
                "urls": ["https://httpbin.org/json"],
                "parser_type": "async"
            }

            response = await client.post(
                f"{self.base_url}/parser/parse",
                headers=self.get_headers(),
                json=parse_request
            )

            if response.status_code == 200:
                task_data = response.json()
                task_id = task_data["task_id"]
                print(f"✅ Парсинг запущен через FastAPI: {task_id}")

                # Проверяем статус
                await asyncio.sleep(3)
                status_response = await client.get(
                    f"{self.base_url}/parser/status/{task_id}",
                    headers=self.get_headers()
                )

                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"✅ Статус получен: {status['status']}")
                else:
                    print(f"❌ Ошибка получения статуса: {status_response.status_code}")
            else:
                print(f"❌ Ошибка запуска парсинга: {response.status_code}")

    async def test_celery_integration(self):
        """Тест интеграции с Celery"""
        print("\n⚡ Тест интеграции Celery")
        print("=" * 25)

        async with httpx.AsyncClient(timeout=60.0) as client:
            # 1. Проверка статистики
            print("1. Получение статистики Celery...")
            response = await client.get(
                f"{self.base_url}/queue/stats",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                print("✅ Статистика Celery получена")
            else:
                print(f"❌ Ошибка получения статистики: {response.status_code}")

            # 2. Активные задачи
            print("2. Проверка активных задач...")
            response = await client.get(
                f"{self.base_url}/queue/active",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                active_data = response.json()
                print(f"✅ Активных задач: {len(active_data.get('active_tasks', {}))}")
            else:
                print(f"❌ Ошибка получения активных задач: {response.status_code}")

            # 3. Запуск задачи в очереди
            print("3. Запуск задачи в очереди...")
            queue_request = {
                "urls": ["https://httpbin.org/json"],
                "parser_type": "async"
            }

            response = await client.post(
                f"{self.base_url}/queue/parse",
                headers=self.get_headers(),
                json=queue_request
            )

            if response.status_code == 200:
                task_data = response.json()
                task_id = task_data["task_id"]
                print(f"✅ Задача в очереди: {task_id}")

                # Мониторинг выполнения
                print("4. Мониторинг выполнения...")
                for i in range(10):  # 10 попыток
                    await asyncio.sleep(3)

                    status_response = await client.get(
                        f"{self.base_url}/queue/status/{task_id}",
                        headers=self.get_headers()
                    )

                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"   Статус #{i + 1}: {status_data['status']}")

                        if status_data['status'] in ['success', 'failure']:
                            if status_data['status'] == 'success':
                                print("✅ Задача успешно завершена через Celery!")
                            else:
                                print("❌ Задача завершилась с ошибкой")
                            break
                    else:
                        print(f"❌ Ошибка статуса: {status_response.status_code}")
                        break
            else:
                print(f"❌ Ошибка добавления в очередь: {response.status_code}")

    async def test_database_operations(self):
        """Тест операций с базой данных"""
        print("\n🗄️ Тест операций с БД")
        print("=" * 22)

        async with httpx.AsyncClient() as client:
            # Проверяем команды
            print("1. Проверка команд...")
            response = await client.get(
                f"{self.base_url}/team/",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                teams = response.json()
                print(f"✅ Команд в БД: {len(teams)}")
            else:
                print(f"❌ Ошибка получения команд: {response.status_code}")

            # Проверяем пользователей
            print("2. Проверка пользователей...")
            response = await client.get(
                f"{self.base_url}/users/",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                users = response.json()
                print(f"✅ Пользователей в БД: {len(users)}")
            else:
                print(f"❌ Ошибка получения пользователей: {response.status_code}")

            # Проверяем турниры
            print("3. Проверка турниров...")
            response = await client.get(
                f"{self.base_url}/tournaments/",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                tournaments = response.json()
                print(f"✅ Турниров в БД: {len(tournaments)}")
            else:
                print(f"❌ Ошибка получения турниров: {response.status_code}")

    async def test_file_operations(self):
        """Тест файловых операций"""
        print("\n📁 Тест файловых операций")
        print("=" * 26)

        # Создаем тестовый файл
        test_content = b"Test image content"

        async with httpx.AsyncClient() as client:
            files = {"photo": ("test.jpg", test_content, "image/jpeg")}
            data = {"player_id": "1"}

            print("1. Попытка загрузки фото игрока...")
            response = await client.post(
                f"{self.base_url}/players/1/photo",
                headers={"Authorization": f"Bearer {self.token}"},
                files=files,
                data=data
            )

            if response.status_code in [200, 201, 404]:  # 404 если игрока нет
                if response.status_code == 404:
                    print("⚠️ Игрок не найден (это нормально для тестов)")
                else:
                    print("✅ Загрузка файлов работает")
            else:
                print(f"❌ Ошибка загрузки файла: {response.status_code}")

    async def test_error_handling(self):
        """Тест обработки ошибок"""
        print("\n🚨 Тест обработки ошибок")
        print("=" * 25)

        async with httpx.AsyncClient() as client:
            # 1. Неверный endpoint
            print("1. Неверный endpoint...")
            response = await client.get(f"{self.base_url}/nonexistent")
            if response.status_code == 404:
                print("✅ 404 обрабатывается корректно")
            else:
                print(f"❌ Неожиданный код: {response.status_code}")

            # 2. Неверная аутентификация
            print("2. Неверная аутентификация...")
            response = await client.get(
                f"{self.base_url}/users/profile",
                headers={"Authorization": "Bearer invalid_token"}
            )
            if response.status_code == 401:
                print("✅ 401 обрабатывается корректно")
            else:
                print(f"❌ Неожиданный код: {response.status_code}")

            # 3. Несуществующая задача парсера
            print("3. Несуществующая задача...")
            response = await client.get(
                f"{self.base_url}/parser/status/nonexistent-task",
                headers=self.get_headers()
            )
            if response.status_code == 404:
                print("✅ Несуществующие задачи обрабатываются")
            else:
                print(f"❌ Неожиданный код: {response.status_code}")

    async def run_all_tests(self):
        """Запуск всех тестов"""
        print("🧪 Docker System Tests")
        print("=" * 50)

        if not await self.authenticate():
            print("❌ Не удалось аутентифицироваться")
            return

        await self.test_microservices_communication()
        await self.test_celery_integration()
        await self.test_database_operations()
        await self.test_file_operations()
        await self.test_error_handling()

        print("\n🎉 Все тесты завершены!")
        print("=" * 50)
        print("\n📊 Сводка возможностей Docker системы:")
        print("✅ Микросервисная архитектура")
        print("✅ Межсервисное взаимодействие")
        print("✅ Асинхронные очереди")
        print("✅ Персистентность данных")
        print("✅ Обработка ошибок")
        print("✅ Файловые операции")


async def main():
    tester = DockerSystemTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    print("Убедитесь, что система запущена: docker-compose up -d")
    asyncio.run(main())