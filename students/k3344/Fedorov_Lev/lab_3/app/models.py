from datetime import date, time, datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, DateTime, JSON, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    name = Column(String)
    surname = Column(String)
    password_hash = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default='active')
    photo_url = Column(String(255), nullable=True)

    # Relationships
    roles = relationship("Role", secondary="users_roles", back_populates="users")
    teams = relationship("Team", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Role(Base):
    __tablename__ = 'roles'

    role_id = Column(Integer, primary_key=True)
    role_name = Column(String, unique=True, nullable=False)

    # Relationships
    users = relationship("User", secondary="users_roles", back_populates="roles")


class UsersRoles(Base):
    __tablename__ = 'users_roles'

    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.role_id'), primary_key=True)


class SportSchool(Base):
    __tablename__ = 'sport_schools'

    school_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String)
    city = Column(String)
    district = Column(String)
    contact_info = Column(String)

    # Relationships
    teams = relationship("Team", back_populates="school")


class Team(Base):
    __tablename__ = 'teams'

    team_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    school_id = Column(Integer, ForeignKey('sport_schools.school_id'))
    name = Column(String, nullable=False)
    coach = Column(String)
    country = Column(String)
    city = Column(String)
    additional_info = Column(String)
    photo_url = Column(String)

    # Relationships
    user = relationship("User", back_populates="teams")
    school = relationship("SportSchool", back_populates="teams")
    players = relationship("Player", back_populates="team")
    home_matches = relationship("Match", foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches = relationship("Match", foreign_keys="Match.away_team_id", back_populates="away_team")
    applications = relationship("TournamentApplication", back_populates="team")
    season_stats = relationship("TeamSeasonStat", back_populates="team")
    events = relationship("MatchEvent", back_populates="team")


class Season(Base):
    __tablename__ = 'seasons'

    season_id = Column(Integer, primary_key=True)
    year = Column(String, nullable=False, unique=True)  # "2023/2024", "2024/2025" и т.д.

    # Relationships
    tournaments = relationship("Tournament", back_populates="season")
    player_stats = relationship("PlayerSeasonStat", back_populates="season")
    team_stats = relationship("TeamSeasonStat", back_populates="season")
    matches = relationship("Match", back_populates="season")


class Tournament(Base):
    __tablename__ = 'tournaments'

    tournament_id = Column(Integer, primary_key=True)
    season_id = Column(Integer, ForeignKey('seasons.season_id'))
    name = Column(String, nullable=False)
    tournament_type = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    registration_deadline = Column(Date)
    description = Column(String)

    # Relationships
    season = relationship("Season", back_populates="tournaments")
    matches = relationship("Match", back_populates="tournament")
    applications = relationship("TournamentApplication", back_populates="tournament")


class TournamentApplication(Base):
    __tablename__ = 'tournament_applications'

    application_id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.tournament_id'))
    team_id = Column(Integer, ForeignKey('teams.team_id'))
    status = Column(String, default='pending')
    comment = Column(String)
    applied_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tournament = relationship("Tournament", back_populates="applications")
    team = relationship("Team", back_populates="applications")


class Player(Base):
    __tablename__ = 'players'

    player_id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id'))
    first_name = Column(String, nullable=False)
    middle_name = Column(String)
    last_name = Column(String, nullable=False)
    birth_date = Column(Date)
    country = Column(String)
    city = Column(String)
    gender = Column(String)
    position = Column(String)
    jersey_number = Column(Integer)
    additional_info = Column(String)
    photo_url = Column(String(255), nullable=True)
    snils = Column(String(11), nullable=False)
    birth_certificate = Column(String(255), nullable=False)
    consent = Column(Boolean, default=False, nullable=False)

    # Relationships
    team = relationship("Team", back_populates="players")
    season_stats = relationship("PlayerSeasonStat", back_populates="player")
    events = relationship("MatchEvent", back_populates="player")


class Match(Base):
    __tablename__ = 'matches'

    match_id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.tournament_id'))
    season_id = Column(Integer, ForeignKey('seasons.season_id'))
    match_date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    location = Column(String)
    home_team_id = Column(Integer, ForeignKey('teams.team_id'))
    away_team_id = Column(Integer, ForeignKey('teams.team_id'))
    status = Column(String, default='scheduled')
    additional_settings = Column(String)

    # Relationships
    tournament = relationship("Tournament", back_populates="matches")
    season = relationship("Season", back_populates="matches")
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    events = relationship("MatchEvent", back_populates="match")
    officials = relationship("MatchOfficial", back_populates="match")
    audit_logs = relationship("AuditLog", back_populates="match")


class MatchEvent(Base):
    __tablename__ = 'match_events'

    event_id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.match_id'))
    event_type = Column(String, nullable=False)
    event_time = Column(String)
    real_timestamp = Column(DateTime, default=datetime.utcnow)
    team_id = Column(Integer, ForeignKey('teams.team_id'))
    player_id = Column(Integer, ForeignKey('players.player_id'))
    additional_data = Column(JSON)

    # Relationships
    match = relationship("Match", back_populates="events")
    team = relationship("Team", back_populates="events")
    player = relationship("Player", back_populates="events")
    audit_logs = relationship("AuditLog", back_populates="event")


class PlayerSeasonStat(Base):
    __tablename__ = 'player_season_stats'

    player_id = Column(Integer, ForeignKey('players.player_id'), primary_key=True)
    season_id = Column(Integer, ForeignKey('seasons.season_id'), primary_key=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.tournament_id'), nullable=True)
    points = Column(Integer, default=0)
    matches_played = Column(Integer, default=0)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    shots_on_goal = Column(Integer, default=0)
    penalty_count = Column(Integer, default=0)
    penalty_minutes = Column(Integer, default=0)
    faceoffs_won = Column(Integer, default=0)
    possession_time = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    post_match_shots = Column(Integer, default=0)

    # Relationships
    player = relationship("Player", back_populates="season_stats")
    season = relationship("Season", back_populates="player_stats")
    tournament = relationship("Tournament")


class TeamSeasonStat(Base):
    __tablename__ = 'team_season_stats'

    team_id = Column(Integer, ForeignKey('teams.team_id'), primary_key=True)
    season_id = Column(Integer, ForeignKey('seasons.season_id'), primary_key=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.tournament_id'), nullable=True)
    points = Column(Integer, default=0)
    matches_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    overtime_wins = Column(Integer, default=0)
    overtime_losses = Column(Integer, default=0)
    bullit_wins = Column(Integer, default=0)
    bullit_losses = Column(Integer, default=0)
    total_goals_scored = Column(Integer, default=0)
    total_goals_conceded = Column(Integer, default=0)
    total_shots = Column(Integer, default=0)
    total_penalties_count = Column(Integer, default=0)
    total_penalty_minutes = Column(Integer, default=0)
    timeouts_used = Column(Integer, default=0)
    faceoffs_won = Column(Integer, default=0)
    possession_time = Column(Integer, default=0)
    period1_goals = Column(Integer, default=0)
    period2_goals = Column(Integer, default=0)
    period3_goals = Column(Integer, default=0)
    overtime_goals = Column(Integer, default=0)
    shootout_goals = Column(Integer, default=0)

    # Relationships
    team = relationship("Team", back_populates="season_stats")
    season = relationship("Season", back_populates="team_stats")
    tournament = relationship("Tournament")


class Official(Base):
    __tablename__ = 'officials'

    official_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    role_type = Column(String)
    additional_info = Column(String)

    # Relationships
    match_assignments = relationship("MatchOfficial", back_populates="official")


class MatchOfficial(Base):
    __tablename__ = 'match_officials'

    match_id = Column(Integer, ForeignKey('matches.match_id'), primary_key=True)
    official_id = Column(Integer, ForeignKey('officials.official_id'), primary_key=True)
    official_role = Column(String, nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    match = relationship("Match", back_populates="officials")
    official = relationship("Official", back_populates="match_assignments")


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    audit_id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.match_id'))
    event_id = Column(Integer, ForeignKey('match_events.event_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    action_type = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON)

    # Relationships
    match = relationship("Match", back_populates="audit_logs")
    event = relationship("MatchEvent", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")


async def init_db(connection_string: str):
    """Initialize database connection and create tables if they don't exist"""
    engine = create_async_engine(connection_string)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    return engine, async_session