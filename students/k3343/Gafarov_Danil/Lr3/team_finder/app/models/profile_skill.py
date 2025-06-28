from sqlmodel import SQLModel, Field, Relationship


class ProfileSkill(SQLModel, table=True):
    profile_id: int = Field(foreign_key="profile.id", primary_key=True)
    skill_id: int = Field(foreign_key="skill.id", primary_key=True)
    level: int = Field(ge=1, le=5)

    profile: "Profile" = Relationship(back_populates="skills")
    skill: "Skill" = Relationship(back_populates="profiles")

