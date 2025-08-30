from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

# Ассоц. таблица Team ↔ User с ролью
class TeamMemberLink(SQLModel, table=True):
    team_id: int = Field(foreign_key='team.id', primary_key=True)
    user_id: int = Field(foreign_key='user.id', primary_key=True)
    role: str

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True)
    hashed_password: str
    teams: List['Team'] = Relationship(back_populates='members', link_model=TeamMemberLink)
    submissions: List['Submission'] = Relationship(back_populates='user')

class Hackathon(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    teams: List['Team'] = Relationship(back_populates='hackathon')
    problems: List['Problem'] = Relationship(back_populates='hackathon')

class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    hackathon_id: Optional[int] = Field(foreign_key='hackathon.id')
    hackathon: Optional[Hackathon] = Relationship(back_populates='teams')
    members: List[User] = Relationship(back_populates='teams', link_model=TeamMemberLink)
    submissions: List['Submission'] = Relationship(back_populates='team')

class Problem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str]
    hackathon_id: int = Field(foreign_key='hackathon.id')
    hackathon: Hackathon = Relationship(back_populates='problems')
    submissions: List['Submission'] = Relationship(back_populates='problem')

class Submission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key='user.id')
    team_id: int = Field(foreign_key='team.id')
    hackathon_id: int = Field(foreign_key='hackathon.id')
    problem_id: int = Field(foreign_key='problem.id')
    timestamp: Optional[str]
    result: Optional[str]
    user: User = Relationship(back_populates='submissions')
    team: Team = Relationship(back_populates='submissions')
    problem: Problem = Relationship(back_populates='submissions')

#--
class HackathonCreate(SQLModel):
    title:       str
    description: Optional[str] = None
    start_date:  Optional[str] = None
    end_date:    Optional[str] = None

class TeamCreate(SQLModel):
    name:          str
    hackathon_id: int
    members: List[int]


class ProblemCreate(SQLModel):
    title:        str
    description:  Optional[str] = None
    hackathon_id: int

class SubmissionCreate(SQLModel):
    user_id: int
    team_id:    int
    hackathon_id: int
    problem_id: int
    timestamp:  Optional[str] = None
    result:     Optional[str] = None

#--
class SubmissionRead(SQLModel):
    id:      int
    user_id:    int
    team_id:    int
    hackathon_id: int
    problem_id: int
    timestamp:  Optional[str]
    result:     Optional[str]

class TeamRead(SQLModel):
    id:          int
    name:        str
    submissions: List['SubmissionRead']  # вложенные сабмишны

class HackathonRead(SQLModel):
    id:          int
    title:       str
    description: Optional[str]
    start_date:  Optional[str]
    end_date:    Optional[str]
    teams:       List['TeamRead']
