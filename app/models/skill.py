from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy import UniqueConstraint


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)


class StudentSkill(Base):
    __tablename__ = "student_skills"
    __table_args__ = (
    UniqueConstraint("student_id", "skill_id", name="uq_student_skill"),
)

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), index=True, nullable=False)

    student = relationship("Student", back_populates="skills")
    skill = relationship("Skill")

class JobSkill(Base):
    __tablename__ = "job_skills"
    __table_args__ = (
    UniqueConstraint("job_id", "skill_id", name="uq_job_skill"),
)

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), index=True, nullable=False)

    job = relationship("Job", back_populates="required_skills")
    skill = relationship("Skill")