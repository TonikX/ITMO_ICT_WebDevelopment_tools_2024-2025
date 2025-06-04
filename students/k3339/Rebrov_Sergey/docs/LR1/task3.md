## **Задание**

Разобраться как передать в alembic.ini URL базы данных с помощью.env-файла и реализовать подобную передачу.

## **Решение**

Был изменен файл `env.py`:

```python
import ...

env_path = Path(__file__).resolve().parents[3] / '.env'
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in the environment!")

...
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
    level: int | None


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


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/warriors_list")
def warriors_list(session=Depends(get_session)) -> List[Warrior]:
    return session.exec(select(Warrior)).all()


@app.post("/warrior")
def warriors_create(warrior: WarriorCreateOrUpdate, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "data": Warrior}):
    warrior_data = warrior.model_dump(exclude={"skills_ids"})
    warrior_obj = Warrior(**warrior_data)

    if warrior.skills_ids:
        skills = session.exec(select(Skill).where(Skill.id.in_(warrior.skills_ids))).all()
        warrior_obj.skills = skills

    session.add(warrior_obj)
    session.commit()
    session.refresh(warrior_obj)
    return {"status": 200, "data": warrior_obj}


@app.get("/warrior/{warrior_id}", response_model=WarriorProfessions)
def warriors_get(warrior_id: int, session=Depends(get_session)) -> Warrior:
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    return warrior


@app.patch("/warrior/{warrior_id}")
def warrior_update(warrior_id: int, warrior: WarriorCreateOrUpdate, session=Depends(get_session)) -> Warrior:
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")

    warrior_data = warrior.model_dump(exclude_unset=True, exclude={"skills_ids"})
    for key, value in warrior_data.items():
        setattr(db_warrior, key, value)

    # Если передали новые skills_ids — меняем
    if warrior.skills_ids is not None:
        skills = session.exec(select(Skill).where(Skill.id.in_(warrior.skills_ids))).all()
        db_warrior.skills = skills

    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior


@app.delete("/warrior/delete/{warrior_id}")
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
    prof = session.get(Profession, profession_id)
    if not prof:
        raise HTTPException(status_code=404, detail="Profession not found")
    return prof


@app.post("/profession")
def profession_create(prof: ProfessionDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "data": Profession}):
    prof = Profession.model_validate(prof)
    session.add(prof)
    session.commit()
    session.refresh(prof)
    return {"status": 200, "data": prof}


@app.patch("/profession/{profession_id}")
def profession_update(profession_id: int, prof: ProfessionDefault, session=Depends(get_session)) -> Profession:
    db_prof = session.get(Profession, profession_id)
    if not db_prof:
        raise HTTPException(status_code=404, detail="Profession not found")
    prof_data = prof.model_dump(exclude_unset=True)
    for key, value in prof_data.items():
        setattr(db_prof, key, value)
    session.add(db_prof)
    session.commit()
    session.refresh(db_prof)
    return db_prof


@app.delete("/profession/delete/{profession_id}")
def profession_delete(profession_id: int, session=Depends(get_session)):
    prof = session.get(Profession, profession_id)
    if not prof:
        raise HTTPException(status_code=404, detail="Profession not found")
    session.delete(prof)
    session.commit()
    return {"ok": True}


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