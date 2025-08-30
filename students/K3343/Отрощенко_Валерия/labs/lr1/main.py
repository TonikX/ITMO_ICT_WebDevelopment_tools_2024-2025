from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from sqlmodel import select, Session
from connection import init_db, get_session
import jwt, hashlib, os
from datetime import datetime, timedelta

from models import (
    User,
    Hackathon, HackathonCreate, HackathonRead,
    Team, TeamCreate, TeamRead,
    Problem, ProblemCreate,
    Submission, SubmissionCreate, SubmissionRead, TeamMemberLink,
)

# JWT settings
SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
security = HTTPBearer()

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

# ---- Helpers ----
def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

# ---- Auth ----
@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(
    username: str,
    email: str,
    password: str,
    session: Session = Depends(get_session),
):
    hashed = get_password_hash(password)
    user = User(username=username, email=email, hashed_password=hashed)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"msg": "Registered"}

@app.post("/auth/login")
def login(
    username: str,
    password: str,
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or user.hashed_password != get_password_hash(password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials")
    token = create_access_token({"sub": username})
    return {"access_token": token}

@app.get("/users/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/users", response_model=List[User])
def list_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return session.exec(select(User)).all()

@app.post("/users/change-password")
def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user.hashed_password != get_password_hash(old_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong old password")
    current_user.hashed_password = get_password_hash(new_password)
    session.add(current_user)
    session.commit()
    return {"msg": "Password changed"}

# Hackathon CRUD
@app.post(
    "/hackathons",
    response_model=HackathonRead,
    status_code=status.HTTP_201_CREATED,
)
def create_hackathon(
    hack_in: HackathonCreate,
    session: Session = Depends(get_session),
):
    hack = Hackathon(**hack_in.model_dump())
    session.add(hack)
    session.commit()
    session.refresh(hack)
    return session.get(Hackathon, hack.id)

@app.get(
    "/hackathons",
    response_model=List[HackathonRead],
)
def read_hackathons(session: Session = Depends(get_session)):
    return session.exec(select(Hackathon)).all()

@app.get(
    "/hackathons/{hackathon_id}",
    response_model=HackathonRead,
)
def read_hackathon(
    hackathon_id: int,
    session: Session = Depends(get_session),
):
    hack = session.get(Hackathon, hackathon_id)
    if not hack:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    return hack

@app.patch(
    "/hackathons/{hackathon_id}",
    response_model=HackathonRead,
)
def update_hackathon(
    hackathon_id: int,
    hack_update: HackathonCreate,
    session: Session = Depends(get_session),
):
    hack = session.get(Hackathon, hackathon_id)
    if not hack:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    data = hack_update.model_dump(exclude_unset=True)
    for k, v in data.items(): setattr(hack, k, v)
    session.add(hack); session.commit(); session.refresh(hack)
    return hack

@app.delete(
    "/hackathons/{hackathon_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_hackathon(
    hackathon_id: int,
    session: Session = Depends(get_session),
):
    hack = session.get(Hackathon, hackathon_id)
    if not hack:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    session.delete(hack)
    session.commit()

# Team CRUD
@app.post(
    "/teams",
    response_model=Team,
    status_code=status.HTTP_201_CREATED,
)
def create_team(
    team_in: TeamCreate,
    session: Session = Depends(get_session),
):
    # 0) Проверяем, что такой хакатон существует
    hack = session.get(Hackathon, team_in.hackathon_id)
    if not hack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hackathon {team_in.hackathon_id} not found"
        )

    team = Team(name=team_in.name, hackathon_id=team_in.hackathon_id)
    session.add(team)
    session.commit()
    session.refresh(team)


    for user_id in team_in.members:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        link = TeamMemberLink(
            team_id=team.id,
            user_id=user_id,
            role="member"
        )
        session.add(link)

    session.commit()
    session.refresh(team)
    return team


@app.get(
    "/teams",
    response_model=List[TeamRead],
)
def read_teams(session: Session = Depends(get_session)):
    return session.exec(select(Team)).all()

@app.get(
    "/teams/{team_id}",
    response_model=TeamRead,
)
def read_team(
    team_id: int,
    session: Session = Depends(get_session),
):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return team

@app.patch(
    "/teams/{team_id}",
    response_model=TeamRead,
)
def update_team(
    team_id: int,
    team_update: TeamCreate,
    session: Session = Depends(get_session),
):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    data = team_update.model_dump(exclude_unset=True)
    for k, v in data.items(): setattr(team, k, v)
    session.add(team); session.commit(); session.refresh(team)
    return team

@app.delete(
    "/teams/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_team(
    team_id: int,
    session: Session = Depends(get_session),
):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    session.delete(team); session.commit()

# Problem CRUD
@app.post(
    "/problems",
    response_model=Problem,
    status_code=status.HTTP_201_CREATED,
)
def create_problem(
    prob_in: ProblemCreate,
    session: Session = Depends(get_session),
):
    prob = Problem(**prob_in.model_dump())
    session.add(prob); session.commit(); session.refresh(prob)
    return prob

@app.get(
    "/problems",
    response_model=List[Problem],
)
def read_problems(session: Session = Depends(get_session)):
    return session.exec(select(Problem)).all()

@app.get(
    "/problems/{problem_id}",
    response_model=Problem,
)
def read_problem(
    problem_id: int,
    session: Session = Depends(get_session),
):
    prob = session.get(Problem, problem_id)
    if not prob:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return prob

@app.patch(
    "/problems/{problem_id}",
    response_model=Problem,
)
def update_problem(
    problem_id: int,
    prob_update: ProblemCreate,
    session: Session = Depends(get_session),
):
    prob = session.get(Problem, problem_id)
    if not prob:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    data = prob_update.model_dump(exclude_unset=True)
    for k, v in data.items(): setattr(prob, k, v)
    session.add(prob); session.commit(); session.refresh(prob)
    return prob

@app.delete(
    "/problems/{problem_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_problem(
    problem_id: int,
    session: Session = Depends(get_session),
):
    prob = session.get(Problem, problem_id)
    if not prob:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    session.delete(prob); session.commit()

# Submission CRUD
@app.post(
    "/submissions",
    response_model=SubmissionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_submission(
    sub_in: SubmissionCreate,
    session: Session = Depends(get_session),
):
    sub = Submission(**sub_in.model_dump())
    session.add(sub); session.commit(); session.refresh(sub)
    return sub

@app.get(
    "/submissions",
    response_model=List[SubmissionRead],
)
def read_submissions(session: Session = Depends(get_session)):
    return session.exec(select(Submission)).all()

@app.get(
    "/submissions/{submission_id}",
    response_model=SubmissionRead,
)
def read_submission(
    submission_id: int,
    session: Session = Depends(get_session),
):
    sub = session.get(Submission, submission_id)
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    return sub

@app.patch(
    "/submissions/{submission_id}",
    response_model=SubmissionRead,
)
def update_submission(
    submission_id: int,
    sub_update: SubmissionCreate,
    session: Session = Depends(get_session),
):
    sub = session.get(Submission, submission_id)
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    data = sub_update.model_dump(exclude_unset=True)
    for k, v in data.items(): setattr(sub, k, v)
    session.add(sub); session.commit(); session.refresh(sub)
    return sub

@app.delete(
    "/submissions/{submission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_submission(
    submission_id: int,
    session: Session = Depends(get_session),
):
    sub = session.get(Submission, submission_id)
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    session.delete(sub); session.commit()
