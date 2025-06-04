# Практика 1.3: Миграции, ENV, GitIgnore и структура проекта

## Для выполнения лабораторной и всех практических работ рекомендуется использовать версию Python 3.10+

### Миграции. Alembic

При разработке проекта может возникнуть потребность добавлять новые таблицы или изменять уже существующие. Ввиду того, что ORM SQLModel не предусматривает встроенный механизм миграций, необходимо использовать готовые библиотеки, позволяющие вносить изменения БД проекта.
Alembic - позволяет делать нам это.

#### Установка Alembic

Для интеграции Alembic устанавливаем через пакетный менеджер:

```bash
pip install alembic  
```

#### Сгенерировать настройки Alembic

Реализация механизма миграций происходит через вызов:

```bash
alembic init migrations
```

В корне проекта, помимо ранее созданных файлов, сформировалась следующая структура:

```
migrations/
├─ versions/
├─ env.py
├─ README
├─ script.py.mako
alembic.ini
```

Сгенерировалась папка `migrations`, хранящая внутри себя папку с файлами миграций `versions`, файл окружения БД `env.py` и шаблон генерации миграций `script.py.mako`. В корне проекта добавился файл настроек `alembic.ini`.

#### Настройка Alembic для SQLModel

Для создания миграций в SQLModel необходимо добавить импорты моделей и настроить подключение к БД.

- В файле `alembic.ini` переменной `sqlalchemy.url` необходимо указать адрес БД, по аналогии с тем, что находится в файле `connection.py`.
- В файле `env.py` импортировать все из `models.py` и в переменной `target_metadata` указать значение `target_metadata=SQLModel.metadata`.

#### Создание миграций

## Добавляем код для добавления нового поля в модель `Notifications` в файле `models.py`:

```python
class NotificationType(str, Enum):
    over_budget = "over_budget"
    goal_achieved = "goal_achieved"
    info = "info"
```
## Тепрь создаем миграцию:

```bash
alembic revision --autogenerate -m "NotificationType added"
```
![Создаем миграцию](images/alem1.png)


## Применяем миграции с помощью команды

```bash
alembic upgrade head
```
![Применяем миграцию](images/alem2.png)
Полученные изменения можно увидеть, просмотрев поля таблицы через pgAdmin. Файлы миграций хранятся в `migrations/versions`.

### Переменные окружения и .gitignore

При разработке приложений часто необходимо хранить ключи и пароли от БД и различных API. В больших проектах часто используются специальные хранилища, но если разработка небольшая, прятать важные данные можно через `.env` файлы.

#### Создание .env файла

.env-файлы изолируют приложение от среды, где оно запускается, и не должны индексироваться системами контроля версий, так как хранят чувствительную информацию. Для создания .env файла в корне проекта, впишите туда переменные с чувствительными данными:

```env
DB_URL=postgresql+psycopg2://vllazebnyi:vllazebnyi@localhost:5432/financeDB
```

Чтобы получить данные из такого файла, установите пакет python-dotenv:

```bash
pip install python-dotenv
```

В файле `connection.py` адрес БД с использованием переменных окружения указывается следующим образом:

```python
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DB_URL')
```


## Пример файла `env.py` из алембика со скрытым URL

```python
from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlmodel import SQLModel
from alembic import context

from dotenv import load_dotenv
load_dotenv()
database_url = os.getenv('DB_URL') # так я прокинул URL БД из моего .env 
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option('sqlalchemy.url', database_url)
# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata
```
И так даллее...

#### Заключение

Были реализованы все улучшения, описанные в практике, включая интеграцию Alembic, переменные окружения.

