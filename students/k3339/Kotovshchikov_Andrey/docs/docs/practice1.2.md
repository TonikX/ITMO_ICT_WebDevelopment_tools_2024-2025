# Практика 1.2. Настройка БД, SQLModel и миграции через Alembic

#### [Ссылка](https://github.com/KotovshchikovAndrey/ITMOWeb/tree/master/Practice_2)

## Установка зависимостей

Для взаимодействия с базой данных **PostgreSQL** необходимо установить драйвер
**psycong2**. Однака писать сырые SQL запросы не всегда удобно, поэтому была установлена
библиотека sqlmodel, которая под копотом использует ORM **SQLAlchemy** и упрощает взаимодествие
с БД:

```python
pip install sqlmodel
pip install psycopg2-binary
```

## Соединение с БД

в файле `connection.py` представлен код подключения к базе данных PostgreSQL, которая
предварительно была запущена локально при помощи docker:

```python
from sqlmodel import SQLModel, Session, create_engine

db_url = "postgresql://postgres:postgres@localhost:5433/warriors_db"
engine = create_engine(db_url, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```

Функия **get_session** будет использоваться в качестве зависимости и предоставлять
сессию для каждого запроса. Так как в рамках данной практической работы не трбовалось настроить миграции, все
таблицы создаются при старте приложения посредством функции **init_db**:

```python
@app.on_event("startup")
def on_startup():
    init_db()
```

## Создание моделей

Все модели в файле `models.py` были переписаны на SQLModel вместо pydantic:

```python
class SkillWarriorLink(SQLModel, table=True):
    skill_id: Optional[int] = Field(
        default=None, foreign_key="skill.id", primary_key=True
    )
    warrior_id: Optional[int] = Field(
        default=None, foreign_key="warrior.id", primary_key=True
    )


class SkillDefault(SQLModel):
    name: str
    description: Optional[str] = ""


class Skill(SkillDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    warriors: Optional[List["Warrior"]] = Relationship(
        back_populates="skills", link_model=SkillWarriorLink
    )


class ProfessionDefault(SQLModel):
    title: str
    description: str


class Profession(ProfessionDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    warriors_prof: List["Warrior"] = Relationship(back_populates="profession")


class WarriorDefault(SQLModel):
    race: RaceType
    name: str
    level: int
    profession_id: Optional[int] = Field(default=None, foreign_key="profession.id")


class Warrior(WarriorDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    profession: Optional[Profession] = Relationship(
        back_populates="warriors_prof",
        sa_relationship_kwargs={"lazy": "joined"},
    )

    skills: Optional[List[Skill]] = Relationship(
        back_populates="warriors",
        link_model=SkillWarriorLink,
        sa_relationship_kwargs={"uselist": True, "lazy": "selectin"},
    )


class WarriorProfessions(WarriorDefault):
    profession: Optional[Profession] = None


class WarriorResponse(WarriorProfessions):
    id: int
    skills: List[Skill]
```

Все модели, которые являются таблицами помечены параметром `table=True`

## Создание API эндпоинтов

Теперь во всех эндпоинтах мы получаем / создаем / обновляем / удаляем объекты
при помощи объекта сессии и храним все информацию в базе данных PostgreSQL, вместо
оперативной памяти нашего приложения:

```python
@app.post("/warrior")
def warriors_create(warrior: WarriorDefault, session=Depends(get_session)):
    warrior = Warrior.model_validate(warrior)
    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return {"status": 200, "data": warrior}


@app.get("/warriors_list")
def warriors_list(session=Depends(get_session)) -> List[Warrior]:
    return session.exec(select(Warrior)).all()


@app.get("/warrior/{warrior_id}", response_model=WarriorResponse)
def warriors_get(warrior_id: int, session=Depends(get_session)) -> Warrior:
    warrior = session.get(Warrior, warrior_id)
    return warrior


@app.patch("/warrior/{warrior_id}")
def warrior_update(
    warrior_id: int, warrior: WarriorDefault, session=Depends(get_session)
) -> WarriorDefault:
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")

    warrior_data = warrior.model_dump(exclude_unset=True)
    for key, value in warrior_data.items():
        setattr(db_warrior, key, value)

    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior


@app.delete("/warrior/{warrior_id}")
def warrior_delete(warrior_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()
    return {"ok": True}


@app.get("/professions_list")
def professions_list(session=Depends(get_session)) -> List[Profession]:
    return session.exec(select(Profession)).all()


@app.get("/profession/{profession_id}")
def profession_get(profession_id: int, session=Depends(get_session)) -> Profession:
    return session.get(Profession, profession_id)


@app.post("/profession")
def profession_create(prof: ProfessionDefault, session=Depends(get_session)):
    prof = Profession.model_validate(prof)
    session.add(prof)
    session.commit()
    session.refresh(prof)
    return {"status": 200, "data": prof}
```

## Создание API для умений воинов и отображение умений при запросе война

В рамках практической работы номер два также были добалены API эндпоинты
для проведения CRUD операций над умениями воинов:

```python
@app.get("/skills")
def skills_list(session=Depends(get_session)) -> List[Skill]:
    return session.exec(select(Skill)).all()


@app.post("/skills")
def skill_create(skill: SkillDefault, session=Depends(get_session)):
    skill = Skill.model_validate(skill)
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return {"status": 200, "data": skill}


@app.patch("/skills/{skill_id}")
def skill_update(
    skill_id: int,
    skill: SkillDefault,
    session=Depends(get_session),
) -> SkillDefault:
    db_skill = session.get(Skill, skill_id)
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    skill_data = skill.model_dump(exclude_unset=True)
    for key, value in skill_data.items():
        setattr(db_skill, key, value)

    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return db_skill


@app.delete("/skills/{skill_id}")
def skill_delete(skill_id: int, session=Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    session.delete(skill)
    session.commit()
    return {"ok": True}
```

И отдельный эндпоинт для создания ассоциаций между воинами и умениями:

```python
@app.post("/skill_warriors")
def warrior_slill_add(skill_warrior: SkillWarriorLink, session=Depends(get_session)):
    skill = session.get(Skill, skill_warrior.skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    warrior = session.get(Warrior, skill_warrior.warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")

    if skill not in warrior.skills:
        session.add(skill_warrior)
        session.commit()

    return {"ok": True}
```
