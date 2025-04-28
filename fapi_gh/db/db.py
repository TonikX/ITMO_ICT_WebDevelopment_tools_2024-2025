from sqlmodel import SQLModel, Session, create_engine

db_url = 'postgresql://berulaa:123@localhost/hacks'
engine = create_engine(db_url, echo=True) #создают подключение к БД


def init_db(): #используется для инициализации всех таблиц в созданной базе данных, его использование будет представлено ниже
    SQLModel.metadata.create_all(engine)
    print("База и таблицы инициализированы")


def get_session(): #используется для получения сессий, необходимых при выполнении запросов к БД
    with Session(engine) as session:
        yield session



if __name__ == "__main__":
    init_db()
