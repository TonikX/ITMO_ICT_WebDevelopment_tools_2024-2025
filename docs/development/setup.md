# Настройка среды разработки

Это руководство поможет вам настроить среду разработки для API Поиска Веб-Команд.

## Предварительные требования

- Python 3.10 или выше
- PostgreSQL 14 или выше
- Git

## Установка

1. Клонировать репозиторий:

```bash
git clone https://github.com/yourusername/ITMO_ICT_WebDevelopment_tools_2024-2025.git
cd ITMO_ICT_WebDevelopment_tools_2024-2025
```

2. Создать виртуальное окружение:

```bash
python -m venv .venv
source .venv/bin/activate  # На Windows: .venv\Scripts\activate
```

3. Установить зависимости:

```bash
pip install -r requirements.txt
```

4. Создать файл `.env` в корневом каталоге со следующим содержимым:

```
DB_USERNAME=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=web_team_finder
```

5. Создать базу данных:

```bash
createdb web_team_finder
```

6. Применить миграции:

```bash
alembic upgrade head
```

7. Запустить приложение:

```bash
uvicorn main:app --reload
```

API будет доступен по адресу [http://localhost:8000](http://localhost:8000).

Интерактивная документация API доступна по адресу [http://localhost:8000/docs](http://localhost:8000/docs).

## Рабочий процесс разработки

1. Создать новую ветку для вашей функции:

```bash
git checkout -b feature/название-вашей-функции
```

2. Внести изменения и зафиксировать их:

```bash
git add .
git commit -m "Добавить вашу функцию"
```

3. Отправить изменения:

```bash
git push origin feature/название-вашей-функции
```

4. Создать запрос на включение (pull request) на GitHub.

## Запуск тестов

```bash
pytest
```

## Сборка документации

```bash
mkdocs build
```

Для локального обслуживания документации:

```bash
mkdocs serve
```

Документация будет доступна по адресу [http://localhost:8000](http://localhost:8000).
