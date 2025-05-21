from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Optional
from sqlmodel import Session, select, delete
from contextlib import asynccontextmanager
from datetime import timedelta

from models import (
    Project, Skill, Team, TeamMemberLink, User, UserSkillLink, SkillLevel, Task, 
    ProjectTeamLink, UserBase, SkillBase, TeamBase, ProjectBase, TeamRole, ProjectSkillLink,
    UserResponse, TeamResponse, ProjectResponse, TaskResponse, 
    UserCreate, UserLogin, Token, PasswordChange
)
from connection import get_session, init_db
from auth import (
    authenticate_user, create_access_token, get_current_user, 
    get_current_active_user, get_password_hash, verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize the database
    init_db()
    yield
    # Shutdown: cleanup operations can go here if needed

app = FastAPI(lifespan=lifespan)

@app.get("/")
def hello():
    return "Hello, World!"

# Authentication endpoints
@app.post("/register", response_model=User)
def register_user(user_create: UserCreate, session: Session = Depends(get_session)):
    # Check if username already exists
    existing_user = session.exec(
        select(User).where(User.username == user_create.username)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = session.exec(
        select(User).where(User.email == user_create.email)
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        username=user_create.username,
        email=user_create.email,
        full_name=user_create.full_name,
        hashed_password=hashed_password,
        bio=user_create.bio,
        years_of_experience=user_create.years_of_experience
    )
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.put("/users/me/password")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    # Verify current password
    if not verify_password(password_change.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_change.new_password)
    session.add(current_user)
    session.commit()
    return {"message": "Password updated successfully"}

# Update existing endpoints to use authentication
@app.get("/users/", response_model=List[User])
def get_users(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, 
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users/", response_model=User)
def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# Обновление пользователя
@app.patch("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: UserBase, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = user.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# Skills
@app.get("/skills/", response_model=List[Skill])
def get_skills(session: Session = Depends(get_session)):
    skills = session.exec(select(Skill)).all()
    return skills

@app.get("/skills/{skill_id}", response_model=Skill)
def get_skill(skill_id: int, session: Session = Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill

@app.post("/skills/", response_model=Skill)
def create_skill(skill: Skill, session: Session = Depends(get_session)):
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill

# Обновление навыка
@app.patch("/skills/{skill_id}", response_model=Skill)
def update_skill(skill_id: int, skill: SkillBase, session: Session = Depends(get_session)):
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

# Projects
@app.get("/projects/", response_model=List[Project])
def get_projects(session: Session = Depends(get_session)):
    projects = session.exec(select(Project)).all()
    return projects

@app.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.post("/projects/", response_model=Project)
def create_project(project: Project, session: Session = Depends(get_session)):
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

# Обновление проекта
@app.patch("/projects/{project_id}", response_model=Project)
def update_project(project_id: int, project: ProjectBase, session: Session = Depends(get_session)):
    db_project = session.get(Project, project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_data = project.model_dump(exclude_unset=True)
    for key, value in project_data.items():
        setattr(db_project, key, value)
    
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project

# Teams
@app.get("/teams/", response_model=List[Team])
def get_teams(session: Session = Depends(get_session)):
    teams = session.exec(select(Team)).all()
    return teams

@app.get("/teams/{team_id}", response_model=TeamResponse)
def get_team(team_id: int, session: Session = Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@app.get("/teams/{team_id}/members", response_model=List[TeamMemberLink])
def get_team_members(team_id: int, session: Session = Depends(get_session)):
    members = session.exec(select(TeamMemberLink).where(TeamMemberLink.team_id == team_id)).all()
    return members

# Обновление команды
@app.patch("/teams/{team_id}", response_model=Team)
def update_team(team_id: int, team: TeamBase, session: Session = Depends(get_session)):
    db_team = session.get(Team, team_id)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    team_data = team.model_dump(exclude_unset=True)
    for key, value in team_data.items():
        setattr(db_team, key, value)
    
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team

# Поиск пользователей по навыкам
@app.get("/users/search/", response_model=List[User])
def search_users_by_skills(
    skill_ids: List[int] = Query(None), 
    min_level: Optional[SkillLevel] = None,
    session: Session = Depends(get_session)
):
    if not skill_ids:
        return session.exec(select(User)).all()
    
    query = select(User).join(UserSkillLink)
    
    if min_level:
        query = query.where(
            UserSkillLink.skill_id.in_(skill_ids),
            UserSkillLink.level >= min_level
        )
    else:
        query = query.where(UserSkillLink.skill_id.in_(skill_ids))
    
    users = session.exec(query).all()
    return users

# Получение навыков пользователя
@app.get("/users/{user_id}/skills", response_model=List[UserSkillLink])
def get_user_skills(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_skills = session.exec(
        select(UserSkillLink).where(UserSkillLink.user_id == user_id)
    ).all()
    return user_skills

# Добавление навыка пользователю
@app.post("/users/{user_id}/skills", response_model=UserSkillLink)
def add_user_skill(user_id: int, user_skill: UserSkillLink, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    skill = session.get(Skill, user_skill.skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # Проверяем, есть ли уже такой навык у пользователя
    existing_skill = session.exec(
        select(UserSkillLink).where(
            UserSkillLink.user_id == user_id,
            UserSkillLink.skill_id == user_skill.skill_id
        )
    ).first()
    
    if existing_skill:
        raise HTTPException(status_code=400, detail="User already has this skill")
    
    user_skill.user_id = user_id
    session.add(user_skill)
    session.commit()
    session.refresh(user_skill)
    return user_skill

# Обновление связи пользователя и навыка
@app.patch("/users/{user_id}/skills/{skill_id}", response_model=UserSkillLink)
def update_user_skill(
    user_id: int, 
    skill_id: int, 
    user_skill: UserSkillLink, 
    session: Session = Depends(get_session)
):
    db_user_skill = session.exec(
        select(UserSkillLink).where(
            UserSkillLink.user_id == user_id,
            UserSkillLink.skill_id == skill_id
        )
    ).first()
    
    if not db_user_skill:
        raise HTTPException(status_code=404, detail="User skill link not found")
    
    user_skill_data = user_skill.model_dump(exclude_unset=True)
    for key, value in user_skill_data.items():
        if key not in ["user_id", "skill_id"]:  # Не обновляем первичные ключи
            setattr(db_user_skill, key, value)
    
    session.add(db_user_skill)
    session.commit()
    session.refresh(db_user_skill)
    return db_user_skill

@app.get("/teams/matching/{user_id}", response_model=List[Team])
def find_matching_teams(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Получаем навыки пользователя
    user_skills = session.exec(
        select(UserSkillLink).where(UserSkillLink.user_id == user_id)
    ).all()
    user_skill_ids = [us.skill_id for us in user_skills]
    
    # Находим команды, в которых пользователь еще не состоит
    user_teams = session.exec(
        select(TeamMemberLink.team_id).where(TeamMemberLink.user_id == user_id)
    ).all()
    
    # Получаем все команды
    teams = session.exec(select(Team)).all()
    matching_teams = []
    
    for team in teams:
        # Пропускаем команды, в которых пользователь уже состоит
        if team.id in user_teams:
            continue
        
        # Получаем навыки всех участников команды
        team_members = session.exec(
            select(TeamMemberLink.user_id).where(TeamMemberLink.team_id == team.id)
        ).all()
        
        team_skill_ids = []
        for member_id in team_members:
            member_skills = session.exec(
                select(UserSkillLink.skill_id).where(UserSkillLink.user_id == member_id)
            ).all()
            team_skill_ids.extend(member_skills)
        
        # Проверяем, есть ли у пользователя уникальные навыки для команды
        has_unique_skills = any(skill_id not in team_skill_ids for skill_id in user_skill_ids)
        
        # Проверяем, есть ли у пользователя навыки высокого уровня
        has_high_level_skills = session.exec(
            select(UserSkillLink).where(
                UserSkillLink.user_id == user_id,
                UserSkillLink.level.in_([SkillLevel.ADVANCED, SkillLevel.EXPERT])
            )
        ).first() is not None
        
        if has_unique_skills or has_high_level_skills:
            matching_teams.append(team)
    
    return matching_teams

# Add a recommended skill to a project
@app.post("/projects/{project_id}/skills", response_model=ProjectSkillLink)
def add_project_skill(
    project_id: int, 
    project_skill: ProjectSkillLink, 
    session: Session = Depends(get_session)
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    skill = session.get(Skill, project_skill.skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # Check if skill is already added to the project
    existing_skill = session.exec(
        select(ProjectSkillLink).where(
            ProjectSkillLink.project_id == project_id,
            ProjectSkillLink.skill_id == project_skill.skill_id
        )
    ).first()
    
    if existing_skill:
        raise HTTPException(status_code=400, detail="Skill already added to this project")
    
    project_skill.project_id = project_id
    session.add(project_skill)
    session.commit()
    session.refresh(project_skill)
    return project_skill

# Get recommended skills for a project
@app.get("/projects/{project_id}/skills", response_model=List[ProjectSkillLink])
def get_project_skills(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_skills = session.exec(
        select(ProjectSkillLink).where(ProjectSkillLink.project_id == project_id)
    ).all()
    return project_skills

# Find matching projects based on user skills
@app.get("/projects/matching/{user_id}", response_model=List[Project])
def find_matching_projects(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's skills
    user_skills = session.exec(
        select(UserSkillLink).where(UserSkillLink.user_id == user_id)
    ).all()
    user_skill_ids = [us.skill_id for us in user_skills]
    
    # Get all projects
    projects = session.exec(select(Project)).all()
    matching_projects = []
    
    for project in projects:
        # Get project's recommended skills
        project_skills = session.exec(
            select(ProjectSkillLink).where(ProjectSkillLink.project_id == project.id)
        ).all()
        project_skill_ids = [ps.skill_id for ps in project_skills]
        
        # Calculate match score based on how many of the user's skills match project requirements
        matching_skills = set(user_skill_ids).intersection(set(project_skill_ids))
        if matching_skills:
            # Calculate a match score (percentage of required skills that the user has)
            match_score = len(matching_skills) / len(project_skill_ids) if project_skill_ids else 0
            
            # Add project to matching list if there's at least one matching skill
            if match_score > 0:
                # We could add the match score to the project object if needed
                # For now, just add the project to the list
                matching_projects.append(project)
    
    return matching_projects

# Обновление связи команды и участника
@app.patch("/teams/{team_id}/members/{user_id}", response_model=TeamMemberLink)
def update_team_member(
    team_id: int, 
    user_id: int, 
    team_member: TeamMemberLink, 
    session: Session = Depends(get_session)
):
    db_team_member = session.exec(
        select(TeamMemberLink).where(
            TeamMemberLink.team_id == team_id,
            TeamMemberLink.user_id == user_id
        )
    ).first()
    
    if not db_team_member:
        raise HTTPException(status_code=404, detail="Team member link not found")
    
    team_member_data = team_member.model_dump(exclude_unset=True)
    for key, value in team_member_data.items():
        if key not in ["team_id", "user_id"]:  # Не обновляем первичные ключи
            setattr(db_team_member, key, value)
    
    session.add(db_team_member)
    session.commit()
    session.refresh(db_team_member)
    return db_team_member

@app.post("/teams/", response_model=Team)
def create_team(team: Team, session: Session = Depends(get_session)):
    # Set created_at to current time if not provided
    if not team.created_at:
        from datetime import datetime
        team.created_at = datetime.now()
    
    session.add(team)
    session.commit()
    session.refresh(team)
    return team

# Add a member to a team
@app.post("/teams/{team_id}/members", response_model=TeamMemberLink)
def add_team_member(
    team_id: int, 
    team_member: TeamMemberLink, 
    session: Session = Depends(get_session)
):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    user = session.get(User, team_member.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is already a member of the team
    existing_member = session.exec(
        select(TeamMemberLink).where(
            TeamMemberLink.team_id == team_id,
            TeamMemberLink.user_id == team_member.user_id
        )
    ).first()
    
    if existing_member:
        raise HTTPException(status_code=400, detail="User is already a member of this team")
    
    # Set team_id and joined_at if not provided
    team_member.team_id = team_id
    if not team_member.joined_at:
        from datetime import datetime
        team_member.joined_at = datetime.now()
    
    session.add(team_member)
    session.commit()
    session.refresh(team_member)
    return team_member

# Remove a member from a team (only leaders can do this)
@app.delete("/teams/{team_id}/members/{user_id}")
def remove_team_member(
    team_id: int,
    user_id: int,
    current_user_id: int = Query(..., description="ID of the user making the request"),
    session: Session = Depends(get_session)
):
    # Check if the team exists
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if the current user is a leader of the team
    current_user_role = session.exec(
        select(TeamMemberLink).where(
            TeamMemberLink.team_id == team_id,
            TeamMemberLink.user_id == current_user_id
        )
    ).first()
    
    if not current_user_role or current_user_role.role != TeamRole.LEADER:
        raise HTTPException(
            status_code=403, 
            detail="Only team leaders can remove members"
        )
    
    # Check if the user to be removed is a member of the team
    member_to_remove = session.exec(
        select(TeamMemberLink).where(
            TeamMemberLink.team_id == team_id,
            TeamMemberLink.user_id == user_id
        )
    ).first()
    
    if not member_to_remove:
        raise HTTPException(status_code=404, detail="User is not a member of this team")
    
    # Remove the member
    session.delete(member_to_remove)
    session.commit()
    
    return {"message": f"User {user_id} has been removed from team {team_id}"}

# Delete a user
@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Delete tasks assigned to this user
    tasks = session.exec(select(Task).where(Task.assigned_to == user_id)).all()
    for task in tasks:
        task.assigned_to = None
        session.add(task)
    
    # Delete the user
    session.delete(user)
    session.commit()
    
    return {"message": f"User {user_id} has been deleted"}

# Delete a skill
@app.delete("/skills/{skill_id}")
def delete_skill(skill_id: int, session: Session = Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # Delete the skill
    session.delete(skill)
    session.commit()
    
    return {"message": f"Skill {skill_id} has been deleted"}

# Delete a team
@app.delete("/teams/{team_id}")
def delete_team(team_id: int, session: Session = Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Delete the team
    session.delete(team)
    session.commit()
    
    return {"message": f"Team {team_id} has been deleted"}

# Delete a project
@app.delete("/projects/{project_id}")
def delete_project(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Delete the project
    session.delete(project)
    session.commit()
    
    return {"message": f"Project {project_id} has been deleted"}

# Delete a task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Delete the task
    session.delete(task)
    session.commit()
    
    return {"message": f"Task {task_id} has been deleted"}

# Add a team to a project
@app.post("/projects/{project_id}/teams", response_model=ProjectTeamLink)
def add_project_team(
    project_id: int, 
    project_team: ProjectTeamLink, 
    session: Session = Depends(get_session)
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    team = session.get(Team, project_team.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if team is already assigned to the project
    existing_link = session.exec(
        select(ProjectTeamLink).where(
            ProjectTeamLink.project_id == project_id,
            ProjectTeamLink.team_id == project_team.team_id
        )
    ).first()
    
    if existing_link:
        raise HTTPException(status_code=400, detail="Team is already assigned to this project")
    
    # Set project_id and start_date if not provided
    project_team.project_id = project_id
    if not project_team.start_date:
        from datetime import datetime
        project_team.start_date = datetime.now()
    
    session.add(project_team)
    session.commit()
    session.refresh(project_team)
    return project_team
