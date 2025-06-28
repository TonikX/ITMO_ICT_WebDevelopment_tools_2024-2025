# app/models/__init__.py
# Этот файл нужен, чтобы Alembic видел все модели

from .user import User
from .profile import Profile
from .skill import Skill
from .profile_skill import ProfileSkill
from .project import Project
from .team_member import TeamMember