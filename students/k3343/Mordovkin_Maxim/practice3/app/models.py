from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


# ============================================================================

class RaceType(str, Enum):
    director = "director"
    worker = "worker"
    junior = "junior"


class SkillWarriorLink(SQLModel, table=True):
    """
    ассоциативная сущность для many to many
    """
    skill_id: Optional[int] = Field(
                                    default=None, 
                                    foreign_key="skill.id", 
                                    primary_key=True)
    warrior_id: Optional[int] = Field(
                                    default=None, 
                                    foreign_key="warrior.id", 
                                    primary_key=True)
    level: Optional[int] = Field(default=1)
    
# ============================================================================

class Skill(SQLModel, table=True):
    """
    сущность скилов
    """
    id:             Optional[int] = Field(default=None, primary_key=True)
    name:           str
    description:    Optional[str] = ""

    # все войны с таким навыком
    warriors: List["Warrior"] = Relationship(
        back_populates="skills", 
        link_model=SkillWarriorLink                         # связь M2M
    )

    

class SkillCreate(SQLModel):
    """
    dto для создания или обновления навыка
    """
    name:        str
    description: Optional[str] = ""

# ============================================================================

class Profession(SQLModel, table=True):
    """
    сущность профессий
    """
    id:             Optional[int] = Field(default=None, primary_key=True)
    title:          str
    description:    str

    # все воины с такой профессией
    warriors: List["Warrior"] = Relationship(back_populates="profession")

class ProfessionCreate(SQLModel):
    """
    dto для создания или обновления профессии
    """
    title:       str
    description: str

# ============================================================================

class WarriorDefault(SQLModel):
    """
    поля необходимые для создания или обновления воина
    """
    race:           RaceType
    name:           str
    level:          int
    profession_id:  Optional[int] = Field(default=None, foreign_key="profession.id")

class Warrior(WarriorDefault, table=True):
    """
    сущность воинов
    """
    id:             Optional[int] = Field(default=None, primary_key=True)

    # связь many to many на Skill через SkillWarriorLink
    skills:         List[Skill] = Relationship(
        back_populates="warriors", 
        link_model=SkillWarriorLink
    )

    # профессия воина (one to many)
    profession: Optional[Profession] = Relationship(back_populates="warriors")

class WarriorResponse(WarriorDefault):
    """
    dto ответ при выдаче воина
    """
    id:             int
    profession:     Optional[Profession]
    skills:         List[Skill]

# ============================================================================

