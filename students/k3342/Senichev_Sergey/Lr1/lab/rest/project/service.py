from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from .models import ProjectModel
from .schemas import ProjectCreate, Project

class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def create_project(self, project: ProjectCreate) -> ProjectModel:
        db_project = ProjectModel(
            title=project.title,
            description=project.description,
            start_at=project.start_at,
            end_at=project.end_at
        )
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def get_project(self, project_id: int) -> Optional[ProjectModel]:
        return self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()

    def get_projects(self, skip: int = 0, limit: int = 100) -> List[ProjectModel]:
        return self.db.query(ProjectModel).offset(skip).limit(limit).all()

    def update_project(self, project_id: int, project: ProjectCreate) -> Optional[ProjectModel]:
        db_project = self.get_project(project_id)
        if db_project:
            for key, value in project.dict().items():
                setattr(db_project, key, value)
            self.db.commit()
            self.db.refresh(db_project)
        return db_project

    def delete_project(self, project_id: int) -> bool:
        db_project = self.get_project(project_id)
        if db_project:
            self.db.delete(db_project)
            self.db.commit()
            return True
        return False 