from typing import List, Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from pydantic import EmailStr


class UserBase(SQLModel):
    """Базовая модель пользователя системы."""
    name: str
    email: str
    phone: str
    bio: Optional[str] = None
    skills: Optional[str] = None  # Можно хранить как JSON или строкой через разделитель
    registration_date: datetime = Field(default_factory=datetime.now)


class User(UserBase, table=True):
    """Модель пользователя с отношениями."""
    id: Optional[int] = Field(default=None, primary_key=True)
    password: Optional[str] = None  # Добавляем поле для пароля
    # Отношения
    team_memberships: List["TeamMember"] = Relationship(back_populates="user")
    submissions: List["Submission"] = Relationship(back_populates="user")
    created_teams: List["Team"] = Relationship(back_populates="creator")


class HackathonBase(SQLModel):
    """Базовая модель хакатона."""
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    registration_deadline: datetime
    max_team_size: Optional[int] = None
    location: Optional[str] = None
    is_online: bool = True
    status: str = "upcoming"  # upcoming, active, completed, canceled


class Hackathon(HackathonBase, table=True):
    """Модель хакатона с отношениями."""
    id: Optional[int] = Field(default=None, primary_key=True)
    # Отношения
    challenges: List["Challenge"] = Relationship(back_populates="hackathon")
    teams: List["Team"] = Relationship(back_populates="hackathon")


class ChallengeBase(SQLModel):
    """Базовая модель задачи/вызова хакатона."""
    title: str
    description: str
    requirements: str
    evaluation_criteria: str
    hackathon_id: int = Field(foreign_key="hackathon.id")
    max_score: int = 100


class Challenge(ChallengeBase, table=True):
    """Модель задачи/вызова с отношениями."""
    id: Optional[int] = Field(default=None, primary_key=True)
    # Отношения
    hackathon: Hackathon = Relationship(back_populates="challenges")
    submissions: List["Submission"] = Relationship(back_populates="challenge")


class TeamBase(SQLModel):
    """Базовая модель команды."""
    name: str
    description: Optional[str] = None
    hackathon_id: int = Field(foreign_key="hackathon.id")
    creator_id: int = Field(foreign_key="user.id")
    creation_date: datetime = Field(default_factory=datetime.now)
    is_active: bool = True


class Team(TeamBase, table=True):
    """Модель команды с отношениями."""
    id: Optional[int] = Field(default=None, primary_key=True)
    # Отношения
    hackathon: Hackathon = Relationship(back_populates="teams")
    creator: User = Relationship(back_populates="created_teams")
    members: List["TeamMember"] = Relationship(back_populates="team")
    submissions: List["Submission"] = Relationship(back_populates="team")


class TeamMemberBase(SQLModel):
    """Базовая модель участника команды (ассоциативная таблица)."""
    user_id: int = Field(foreign_key="user.id")
    team_id: int = Field(foreign_key="team.id")
    role: str  # Роль в команде (капитан, разработчик, дизайнер и т.д.)
    join_date: datetime = Field(default_factory=datetime.now)
    is_approved: bool = False  # Подтверждение участия админом/капитаном команды


class TeamMember(TeamMemberBase, table=True):
    """Модель участника команды с отношениями."""
    id: Optional[int] = Field(default=None, primary_key=True)
    # Отношения
    user: User = Relationship(back_populates="team_memberships")
    team: Team = Relationship(back_populates="members")


class SubmissionBase(SQLModel):
    """Базовая модель для представления решения/проекта."""
    title: str
    description: str
    project_url: Optional[str] = None
    repository_url: Optional[str] = None
    presentation_url: Optional[str] = None
    team_id: int = Field(foreign_key="team.id")
    challenge_id: int = Field(foreign_key="challenge.id")
    user_id: int = Field(foreign_key="user.id")  # Пользователь, загрузивший решение
    submission_date: datetime = Field(default_factory=datetime.now)


class Submission(SubmissionBase, table=True):
    """Модель решения/проекта с отношениями."""
    id: Optional[int] = Field(default=None, primary_key=True)
    # Отношения
    team: Team = Relationship(back_populates="submissions")
    challenge: Challenge = Relationship(back_populates="submissions")
    user: User = Relationship(back_populates="submissions")
    evaluations: List["Evaluation"] = Relationship(back_populates="submission")


class EvaluationBase(SQLModel):
    """Базовая модель оценки проекта."""
    submission_id: int = Field(foreign_key="submission.id")
    judge_id: int = Field(foreign_key="user.id")  # ID судьи/эксперта
    score: float
    feedback: Optional[str] = None
    evaluation_date: datetime = Field(default_factory=datetime.now)


class Evaluation(EvaluationBase, table=True):
    """Модель оценки проекта с отношениями."""
    id: Optional[int] = Field(default=None, primary_key=True)
    # Отношения
    submission: Submission = Relationship(back_populates="evaluations")
    judge: User = Relationship()  # Односторонняя связь


# Модели для возврата в API с вложенными отношениями
class UserResponse(UserBase):
    id: int


class HackathonResponse(HackathonBase):
    id: int


class TeamWithMembers(TeamBase):
    id: int
    members: List[UserResponse] = []


class ChallengeResponse(ChallengeBase):
    id: int


class SubmissionWithEvaluations(SubmissionBase):
    id: int
    evaluations: List["Evaluation"] = []
    team: TeamBase = None
    challenge: ChallengeBase = None


class TeamMemberResponse(TeamMemberBase):
    id: int
    user: UserResponse = None
    team: TeamBase = None


# Модели для аутентификации
class Token(SQLModel):
    """Схема токена доступа."""
    access_token: str
    token_type: str


class TokenData(SQLModel):
    """Данные, хранимые в JWT-токене."""
    email: Optional[str] = None
    user_id: Optional[int] = None


class UserRegister(SQLModel):
    """Модель для регистрации нового пользователя."""
    name: str
    email: str
    phone: str
    password: str
    bio: Optional[str] = None
    skills: Optional[str] = None


class UserLogin(SQLModel):
    """Модель для входа пользователя."""
    email: str
    password: str