## **Задание**

Задача состоит в разработке программной системы, которая будет использоваться для организации и проведения хакатонов. Хакатон - это соревнование, на котором участники, как правило, программисты, дизайнеры и бизнес-специалисты, работают над проектами в течение определенного времени, решая поставленные задачи или разрабатывая новые идеи.

## **Решение**

Были созданы модели Participant, Team, Challenge, Submission, Evaluation (см. файл `models.py`), а также их подмодели для CRUD операций.

- **Participant** представляет участника хакатона или жюри. Участник может состоять в нескольких командах или выступать судьей, оценивая работы.
- **Team** представляет собой команду, состоящаую из нескольких участников.
- **Challenge** представляет собой задание или конкурс, на который команды подают свои решения, может включать описание и критерии оценки.
- **Submission** представляет собой решение, поданное командой на конкретный челлендж, может иметь привязанные оценки от судей.
- **Evaluation** представляет собой оценку на решения, выставленную судьей, включает балл и комментарии.

И были реализованы запросы по API  (см. файл `main.py`).

## **Файлы**

`models.py`
```python
class ParticipantTeamLink(SQLModel, table=True):
    participant_id: Optional[int] = Field(
        default=None, foreign_key="participant.id", primary_key=True
    )
    team_id: Optional[int] = Field(
        default=None, foreign_key="team.id", primary_key=True
    )
    role: str
    joined_at: datetime = Field(default_factory=datetime.utcnow)


class ParticipantDefault(SQLModel):
    name: str
    email: str
    phone: Optional[str] = None


class Participant(ParticipantDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    teams: List["Team"] = Relationship(
        back_populates="participants", link_model=ParticipantTeamLink
    )
    evaluations: List["Evaluation"] = Relationship(back_populates="judge")


class ParticipantRead(ParticipantDefault):
    id: int
    teams: Optional[List["TeamRead"]]
    evaluations: Optional[List["EvaluationRead"]]


class ParticipantCreateOrUpdate(ParticipantDefault):
    team_ids: Optional[List[int]] = None


class TeamDefault(SQLModel):
    name: str


class Team(TeamDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    participants: List[Participant] = Relationship(
        back_populates="teams", link_model=ParticipantTeamLink
    )
    submissions: List["Submission"] = Relationship(back_populates="team")


class TeamRead(TeamDefault):
    id: int
    participants: Optional[List[ParticipantRead]]


class TeamCreateOrUpdate(TeamDefault):
    participant_ids: Optional[List[int]] = None


class ChallengeDefault(SQLModel):
    title: str
    description: Optional[str] = None
    criteria: Optional[str] = None


class Challenge(ChallengeDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    submissions: List["Submission"] = Relationship(back_populates="challenge")


class ChallengeRead(ChallengeDefault):
    id: int
    submissions: Optional[List["SubmissionRead"]]


class ChallengeCreateOrUpdate(ChallengeDefault):
    pass


class SubmissionDefault(SQLModel):
    team_id: int
    challenge_id: int
    file_url: str


class Submission(SubmissionDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    team: Team = Relationship(back_populates="submissions")
    challenge: Challenge = Relationship(back_populates="submissions")
    evaluations: List["Evaluation"] = Relationship(back_populates="submission")


class SubmissionRead(SubmissionDefault):
    id: int
    submitted_at: datetime
    team: Optional[TeamRead]
    challenge: Optional[ChallengeRead]
    evaluations: Optional[List["EvaluationRead"]]


class SubmissionCreateOrUpdate(SubmissionDefault):
    pass


class EvaluationDefault(SQLModel):
    submission_id: int
    judge_id: int
    score: float
    comments: Optional[str] = None


class Evaluation(EvaluationDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
    submission: Submission = Relationship(back_populates="evaluations")
    judge: Participant = Relationship(back_populates="evaluations")


class EvaluationRead(EvaluationDefault):
    id: int
    evaluated_at: datetime
    submission: Optional[SubmissionRead]
    judge: Optional[ParticipantRead]


class EvaluationCreateOrUpdate(EvaluationDefault):
    pass
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


@app.get("/participants", response_model=List[ParticipantRead])
def list_participants(session: Session = Depends(get_session)):
    return session.exec(select(Participant)).all()


@app.post("/participants", response_model=ParticipantRead)
def create_participant(
    data: ParticipantCreateOrUpdate,
    session: Session = Depends(get_session)
):
    participant = Participant(**data.model_dump(exclude_unset=True, exclude={"team_ids"}))
    if data.team_ids:
        teams = session.exec(select(Team).where(Team.id.in_(data.team_ids))).all()
        participant.teams = teams
    session.add(participant)
    session.commit()
    session.refresh(participant)
    return participant


@app.get("/participants/{participant_id}", response_model=ParticipantRead)
def get_participant(
    participant_id: int,
    session: Session = Depends(get_session)
):
    participant = session.get(Participant, participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    return participant


@app.patch("/participants/{participant_id}", response_model=ParticipantRead)
def update_participant(
    participant_id: int,
    data: ParticipantCreateOrUpdate,
    session: Session = Depends(get_session)
):
    participant = session.get(Participant, participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    updates = data.model_dump(exclude_unset=True, exclude={"team_ids"})
    for k, v in updates.items():
        setattr(participant, k, v)
    if data.team_ids is not None:
        teams = session.exec(select(Team).where(Team.id.in_(data.team_ids))).all()
        participant.teams = teams
    session.add(participant)
    session.commit()
    session.refresh(participant)
    return participant


@app.delete("/participants/{participant_id}")
def delete_participant(
    participant_id: int,
    session: Session = Depends(get_session)
):
    participant = session.get(Participant, participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    session.delete(participant)
    session.commit()
    return {"ok": True}


@app.get("/teams", response_model=List[TeamRead])
def list_teams(session: Session = Depends(get_session)):
    return session.exec(select(Team)).all()


@app.post("/teams", response_model=TeamRead)
def create_team(
    data: TeamCreateOrUpdate,
    session: Session = Depends(get_session)
):
    team = Team(**data.model_dump(exclude_unset=True, exclude={"participant_ids"}))
    if data.participant_ids:
        participants = session.exec(select(Participant).where(Participant.id.in_(data.participant_ids))).all()
        team.participants = participants
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


@app.get("/teams/{team_id}", response_model=TeamRead)
def get_team(
    team_id: int,
    session: Session = Depends(get_session)
):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@app.patch("/teams/{team_id}", response_model=TeamRead)
def update_team(
    team_id: int,
    data: TeamCreateOrUpdate,
    session: Session = Depends(get_session)
):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    updates = data.model_dump(exclude_unset=True, exclude={"participant_ids"})
    for k, v in updates.items():
        setattr(team, k, v)
    if data.participant_ids is not None:
        participants = session.exec(select(Participant).where(Participant.id.in_(data.participant_ids))).all()
        team.participants = participants
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


@app.delete("/teams/{team_id}")
def delete_team(
    team_id: int,
    session: Session = Depends(get_session)
):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(team)
    session.commit()
    return {"ok": True}


@app.get("/challenges", response_model=List[ChallengeRead])
def list_challenges(session: Session = Depends(get_session)):
    return session.exec(select(Challenge)).all()


@app.post("/challenges", response_model=ChallengeRead)
def create_challenge(
    data: ChallengeCreateOrUpdate,
    session: Session = Depends(get_session)
):
    challenge = Challenge(**data.model_dump(exclude_unset=True))
    session.add(challenge)
    session.commit()
    session.refresh(challenge)
    return challenge


@app.get("/challenges/{challenge_id}", response_model=ChallengeRead)
def get_challenge(
    challenge_id: int,
    session: Session = Depends(get_session)
):
    challenge = session.get(Challenge, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return challenge


@app.patch("/challenges/{challenge_id}", response_model=ChallengeRead)
def update_challenge(
    challenge_id: int,
    data: ChallengeCreateOrUpdate,
    session: Session = Depends(get_session)
):
    challenge = session.get(Challenge, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    updates = data.model_dump(exclude_unset=True)
    for k, v in updates.items():
        setattr(challenge, k, v)
    session.add(challenge)
    session.commit()
    session.refresh(challenge)
    return challenge


@app.delete("/challenges/{challenge_id}")
def delete_challenge(
    challenge_id: int,
    session: Session = Depends(get_session)
):
    challenge = session.get(Challenge, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    session.delete(challenge)
    session.commit()
    return {"ok": True}


@app.get("/submissions", response_model=List[SubmissionRead])
def list_submissions(session: Session = Depends(get_session)):
    return session.exec(select(Submission)).all()


@app.post("/submissions", response_model=SubmissionRead)
def create_submission(
    data: SubmissionCreateOrUpdate,
    session: Session = Depends(get_session)
):
    submission = Submission(**data.model_dump(exclude_unset=True))
    session.add(submission)
    session.commit()
    session.refresh(submission)
    return submission


@app.get("/submissions/{submission_id}", response_model=SubmissionRead)
def get_submission(
    submission_id: int,
    session: Session = Depends(get_session)
):
    submission = session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


@app.patch("/submissions/{submission_id}", response_model=SubmissionRead)
def update_submission(
    submission_id: int,
    data: SubmissionCreateOrUpdate,
    session: Session = Depends(get_session)
):
    submission = session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    updates = data.model_dump(exclude_unset=True)
    for k, v in updates.items():
        setattr(submission, k, v)
    session.add(submission)
    session.commit()
    session.refresh(submission)
    return submission


@app.delete("/submissions/{submission_id}")
def delete_submission(
    submission_id: int,
    session: Session = Depends(get_session)
):
    submission = session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    session.delete(submission)
    session.commit()
    return {"ok": True}


@app.get("/evaluations", response_model=List[EvaluationRead])
def list_evaluations(session: Session = Depends(get_session)):
    return session.exec(select(Evaluation)).all()


@app.post("/evaluations", response_model=EvaluationRead)
def create_evaluation(
    data: EvaluationCreateOrUpdate,
    session: Session = Depends(get_session)
):
    evaluation = Evaluation(**data.model_dump(exclude_unset=True))
    session.add(evaluation)
    session.commit()
    session.refresh(evaluation)
    return evaluation


@app.get("/evaluations/{evaluation_id}", response_model=EvaluationRead)
def get_evaluation(
    evaluation_id: int,
    session: Session = Depends(get_session)
):
    evaluation = session.get(Evaluation, evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return evaluation


@app.patch("/evaluations/{evaluation_id}", response_model=EvaluationRead)
def update_evaluation(
    evaluation_id: int,
    data: EvaluationCreateOrUpdate,
    session: Session = Depends(get_session)
):
    evaluation = session.get(Evaluation, evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    updates = data.model_dump(exclude_unset=True)
    for k, v in updates.items():
        setattr(evaluation, k, v)
    session.add(evaluation)
    session.commit()
    session.refresh(evaluation)
    return evaluation


@app.delete("/evaluations/{evaluation_id}")
def delete_evaluation(
    evaluation_id: int,
    session: Session = Depends(get_session)
):
    evaluation = session.get(Evaluation, evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    session.delete(evaluation)
    session.commit()
    return {"ok": True}
```
