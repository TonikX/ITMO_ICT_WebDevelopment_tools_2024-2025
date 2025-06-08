from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional
from sqlalchemy import Column, Integer

class Lab3Task(SQLModel, table=True):
    __tablename__ = "lab3_tasks"

    id: Optional[int] = Field(
        sa_column=Column(Integer, primary_key=True, autoincrement=True)
    )

    status: str = Field(
        default="pending",
        max_length=50,
        nullable=False,
        description="任务状态：pending/processing/completed"
    )

    # 确保存在 data 属性的定义
    data: str = Field(
        max_length=255,
        nullable=False,
        description="任务核心数据"
    )

    description: Optional[str] = Field(
        default="",
        max_length=255,
        nullable=True,
        description="任务描述"
    )

    created_at: datetime = Field(
        default_factory=datetime.now,
        nullable=False,
        description="任务创建时间"
    )

    completed_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        description="任务完成时间"
    )