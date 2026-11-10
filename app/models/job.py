from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)

    required_skills = relationship(
        "JobSkill",
        back_populates="job",
        cascade="all, delete-orphan"
    ) 
    