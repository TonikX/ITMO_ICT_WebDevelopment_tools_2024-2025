## **Задание**

Создать API и модели для умений воинов и их ассоциативной сущности, вложено отображать умения при запросе воина.

## **Решение**

Были реализованы модели для умений:

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
        back_populates="skills",
        link_model=SkillWarriorLink
    )
```

И реализованы дополнительные методы:

```python
@app.get("/skills_list")
def skills_list(session=Depends(get_session)) -> List[Skill]:
    return session.exec(select(Skill)).all()


@app.get("/skill/{skill_id}")
def skill_get(skill_id: int, session=Depends(get_session)) -> Skill:
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@app.post("/skill")
def skill_create(skill: SkillDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "data": Skill}):
    skill = Skill.model_validate(skill)
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return {"status": 200, "data": skill}


@app.patch("/skill/{skill_id}")
def skill_update(skill_id: int, skill: SkillDefault, session=Depends(get_session)) -> Skill:
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


@app.delete("/skill/delete/{skill_id}")
def skill_delete(skill_id: int, session=Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    session.delete(skill)
    session.commit()
    return {"ok": True}
```

## **Файлы**

`models.py`
```python
class RaceType(Enum):
    director = "director"
    worker = "worker"
    junior = "junior"


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
        back_populates="skills",
        link_model=SkillWarriorLink
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
    profession: Optional[Profession] = Relationship(back_populates="warriors_prof")
    skills: Optional[List[Skill]] = Relationship(back_populates="warriors", link_model=SkillWarriorLink)


class WarriorProfessions(WarriorDefault):
    profession: Optional[Profession] = None
    skills: Optional[List[Skill]] = None


class WarriorCreateOrUpdate(WarriorDefault):
    skills_ids: Optional[List[int]] = None
```

`connection.py`
```python
load_dotenv()
db_url = os.getenv("DB_ADMIN")
engine = create_engine(db_url, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```

`main.py`
```python
app = FastAPI()

temp_professions = [
    {
        "id": 1,
        "title": "Влиятельный человек",
        "description": "Эксперт по всем вопросам"
    },
    {
        "id": 2,
        "title": "Дельфист-гребец",
        "description": "Уважаемый сотрудник"
    }
]

temp_bd = [
    {
        "id": 1,
        "race": "director",
        "name": "Мартынов Дмитрий",
        "level": 12,
        "profession": temp_professions[0],
        "skills": [
            {
                "id": 1,
                "name": "Купле-продажа компрессоров",
                "description": ""
            },
            {
                "id": 2,
                "name": "Оценка имущества",
                "description": ""
            }
        ]
    },
    {
        "id": 2,
        "race": "worker",
        "name": "Андрей Косякин",
        "level": 12,
        "profession": temp_professions[1],
        "skills": []
    },
]


@app.get("/warriors_list")
def warriors_list() -> List[Warrior]:
    return temp_bd


@app.get("/warrior/{warrior_id}")
def warriors_get(warrior_id: int) -> List[Warrior]:
    return [warrior for warrior in temp_bd if warrior.get("id") == warrior_id]


@app.post("/warrior")
def warriors_create(warrior: Warrior) -> TypedDict('Response', {"status": int, "data": Warrior}):
    warrior_to_append = warrior.model_dump()
    temp_bd.append(warrior_to_append)
    return {"status": 200, "data": warrior}


@app.delete("/warrior/delete{warrior_id}")
def warrior_delete(warrior_id: int):
    for i, warrior in enumerate(temp_bd):
        if warrior.get("id") == warrior_id:
            temp_bd.pop(i)
            break
    return {"status": 201, "message": "deleted"}


@app.put("/warrior{warrior_id}")
def warrior_update(warrior_id: int, warrior: Warrior) -> List[Warrior]:
    for war in temp_bd:
        if war.get("id") == warrior_id:
            warrior_to_append = warrior.model_dump()
            temp_bd.remove(war)
            temp_bd.append(warrior_to_append)
    return temp_bd


@app.get("/professions_list")
def professions_list() -> List[Profession]:
    return temp_professions


@app.get("/profession/{profession_id}")
def profession_get(profession_id: int) -> List[Profession]:
    return [profession for profession in temp_professions if profession.get("id") == profession_id]


@app.post("/profession")
def profession_create(profession: Profession) -> TypedDict('Response', {"status": int, "data": Profession}):
    profession_to_append = profession.model_dump()
    temp_professions.append(profession_to_append)
    return {"status": 200, "data": profession}


@app.delete("/profession/delete{profession_id}")
def profession_delete(profession_id: int):
    for i, profession in enumerate(temp_professions):
        if profession.get("id") == profession_id:
            temp_professions.pop(i)
            break
    return {"status": 201, "message": "deleted"}


@app.put("/profession{profession_id}")
def profession_update(profession_id: int, profession: Profession) -> List[Profession]:
    for prof in temp_professions:
        if prof.get("id") == profession_id:
            profession_to_append = profession.model_dump()
            temp_professions.remove(prof)
            temp_professions.append(profession_to_append)
    return temp_professions
```