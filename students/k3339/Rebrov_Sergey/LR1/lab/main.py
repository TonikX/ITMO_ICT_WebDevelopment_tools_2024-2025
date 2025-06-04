from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import select, Session

from connecton import init_db, get_session
from models import *

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
