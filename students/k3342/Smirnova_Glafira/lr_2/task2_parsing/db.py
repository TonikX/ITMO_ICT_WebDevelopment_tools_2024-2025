from sqlalchemy import text
from sqlmodel import create_engine, Session, SQLModel

from students.k3342.Smirnova_Glafira.lr_2.task2_parsing.logger import logger

DB_URL = "postgresql://postgres:password@localhost:5432/books"


def init_db():
    engine = create_engine(DB_URL)

    with engine.connect() as conn:
        if not engine.dialect.has_table(conn, "bookparsed"):
            SQLModel.metadata.create_all(engine)
            logger.info("Таблица bookparsed создана")
        else:
            logger.info("Таблица bookparsed уже существует")

    return engine


def clear_bookparsed_table():
    engine = create_engine(DB_URL)

    try:
        with Session(engine) as session:
            session.exec(text("DELETE FROM bookparsed"))
            session.commit()
            print("Таблица bookparsed успешно очищена")
    except Exception as e:
        session.rollback()
        print(f"Ошибка при очистке таблицы: {e}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    clear_bookparsed_table()