from sqlmodel import SQLModel, Session, create_engine, Field, Relationship, select
from enum import Enum
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Depends
from typing_extensions import TypedDict
from contextlib import asynccontextmanager
from fastapi import HTTPException


db_url = 'postgresql://postgres:12345678@localhost:5432/warriors_db'
engine = create_engine(db_url, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


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


class Skill(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = ""
    warriors: Optional[List["Warrior"]] = Relationship(back_populates="skills", link_model=SkillWarriorLink)


class ProfessionDefault(SQLModel, table=True):
    __tablename__ = "profession_default"
    id: int = Field(default=None, primary_key=True)
    title: str
    description: str
    warriors_prof: List["Warrior"] = Relationship(back_populates="profession")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)


class WarriorDefault(SQLModel):
    race: RaceType
    name: str
    level: int


class Warrior(WarriorDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    profession_id: Optional[int] = Field(default=None, foreign_key="profession_default.id")
    profession: Optional[ProfessionDefault] = Relationship(back_populates="warriors_prof")
    skills: Optional[List[Skill]] = Relationship(back_populates="warriors", link_model=SkillWarriorLink)


@app.post("/warrior")
def warriors_create(warrior: WarriorDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int,
                                                                                                     "data": Warrior}):
    warrior = Warrior.model_validate(warrior)
    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return {"status": 200, "data": warrior}


@app.get("/warriors_list")
def warriors_list(session=Depends(get_session)) -> List[Warrior]:
    return session.exec(select(Warrior)).all()


@app.get("/warrior/{warrior_id}")
def warriors_get(warrior_id: int, session: Session = Depends(get_session)) -> Optional[Warrior]:
    warrior = session.exec(select(Warrior).where(Warrior.id == warrior_id)).first()
    if warrior is None:
        return {"error": "Warrior not found"}
    return warrior.model_dump()


@app.patch("/warrior{warrior_id}")
def warrior_update(warrior_id: int, warrior: WarriorDefault, session=Depends(get_session)) -> WarriorDefault:
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


@app.get("/professions_list")
def professions_list(session=Depends(get_session)) -> List[ProfessionDefault]:
    return session.exec(select(ProfessionDefault)).all()


@app.get("/profession/{profession_id}")
def profession_get(profession_id: int, session=Depends(get_session)) -> ProfessionDefault:
    return session.get(ProfessionDefault, profession_id)


@app.post("/profession")
def profession_create(prof: ProfessionDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int,
                                                                                                       "data": ProfessionDefault}):
    prof = ProfessionDefault.model_validate(prof)
    session.add(prof)
    session.commit()
    session.refresh(prof)
    return {"status": 200, "data": prof}


@app.delete("/warrior/delete{warrior_id}")
def warrior_delete(warrior_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()
    return {"ok": True}


@app.get("/warriors", response_model=List[Warrior])
def get_warriors(session: Session = Depends(get_session)):
    return session.exec(select(Warrior)).all()


@app.get("/warrior/{warrior_id}", response_model=Warrior)
def get_warrior(warrior_id: int, db: Session = Depends(get_session)):
    warrior = db.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Воин не найден")
    return warrior


@app.post("/warrior", response_model=Warrior)
def create_warrior(warrior: WarriorDefault, db: Session = Depends(get_session)):
    db_warrior = Warrior.from_orm(warrior)
    db.add(db_warrior)
    db.commit()
    db.refresh(db_warrior)
    return db_warrior


@app.put("/warrior/{warrior_id}", response_model=Warrior)
def update_warrior(warrior_id: int, warrior: WarriorDefault, db: Session = Depends(get_session)):
    db_warrior = db.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Воин не найден")
    warrior_data = warrior.dict(exclude_unset=True)
    for key, value in warrior_data.items():
        setattr(db_warrior, key, value)
    db.add(db_warrior)
    db.commit()
    db.refresh(db_warrior)
    return db_warrior


@app.delete("/warrior/{warrior_id}")
def delete_warrior(warrior_id: int, db: Session = Depends(get_session)):
    warrior = db.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Воин не найден")
    db.delete(warrior)
    db.commit()
    return {"status": "success", "message": "Воин удалён"}


@app.post("/skill")
def create_skill(skill: Skill, session: Session = Depends(get_session)) -> Dict[str, Any]:
    skill_data = skill.model_dump(exclude={"id"})
    new_skill = Skill(**skill_data)
    session.add(new_skill)
    session.commit()
    session.refresh(new_skill)
    return {"status": 200, "data": new_skill.model_dump()}


@app.get("/skills", response_model=List[Skill])
def get_skills(db: Session = Depends(get_session)):
    skills = db.exec(select(Skill)).all()
    return skills


@app.post("/warrior/{warrior_id}/skill/{skill_id}")
def add_skill_to_warrior(warrior_id: int, skill_id: int, db: Session = Depends(get_session)):
    warrior = db.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Воин не найден")
    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Умение не найдено")
    warrior.skills.append(skill)
    db.add(warrior)
    db.commit()
    db.refresh(warrior)
    return {"status": "success", "message": "Умение добавлено воину"}
