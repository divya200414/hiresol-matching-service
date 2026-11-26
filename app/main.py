from contextlib import asynccontextmanager
from app.services.hiresol_api import get_students, get_jobs
from app.services.matching_service import rank_students
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import func, text
from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app.models.student import Student
from app.models.job import Job
from app.models.skill import Skill, StudentSkill, JobSkill
from app.services.scheduler import start_scheduler, scheduler


# Start scheduler when FastAPI starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(
    title="HireSol Matching Microservice",
    lifespan=lifespan
)


# Create database tables
Base.metadata.create_all(bind=engine)


# Create indexes
with engine.connect() as connection:

    connection.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS idx_student_skills_student "
        "ON student_skills(student_id)"
    )

    connection.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS idx_student_skills_skill "
        "ON student_skills(skill_id)"
    )

    connection.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS idx_job_skills_job "
        "ON job_skills(job_id)"
    )

    connection.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS idx_job_skills_skill "
        "ON job_skills(skill_id)"
    )

    connection.exec_driver_sql(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_student_skill "
        "ON student_skills(student_id, skill_id)"
    )

    connection.exec_driver_sql(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_job_skill "
        "ON job_skills(job_id, skill_id)"
    )

    connection.commit()


# Database connection
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# Home API
@app.get("/")
def home():
    return {
        "message": "HireSol Matching Microservice is running"
    }


# Add sample data
@app.post("/seed")
def seed_database(db: Session = Depends(get_db)):

    if db.query(Student).first():
        return {"message": "Sample data already exists"}

    # Create skills
    python = Skill(name="Python")
    flask = Skill(name="Flask")
    mysql = Skill(name="MySQL")
    django = Skill(name="Django")
    react = Skill(name="React")

    db.add_all([python, flask, mysql, django, react])
    db.commit()

    # Create students
    ayush = Student(name="Ayush")
    rahul = Student(name="Rahul")
    priya = Student(name="Priya")

    db.add_all([ayush, rahul, priya])
    db.commit()

    # Assign skills
    ayush.skills = [
        StudentSkill(skill=python),
        StudentSkill(skill=flask),
        StudentSkill(skill=mysql)
    ]

    rahul.skills = [
        StudentSkill(skill=python),
        StudentSkill(skill=django),
        StudentSkill(skill=react)
    ]

    priya.skills = [
        StudentSkill(skill=python),
        StudentSkill(skill=mysql),
        StudentSkill(skill=react)
    ]

    # Create job
    job = Job(title="Python Developer")

    db.add(job)
    db.commit()

    # Assign job skills
    job.required_skills = [
        JobSkill(skill=python),
        JobSkill(skill=flask),
        JobSkill(skill=mysql)
    ]

    db.commit()

    return {
        "message": "Sample data added successfully"
    }


# Matching API with pagination
@app.get("/match/{job_id}")
def match_students(
    job_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000)
):
    # Fetch jobs and students from HireSol API
    jobs = get_jobs()
    students = get_students()

    # Find the requested job
    job = next(
        (
            j for j in jobs
            if str(j.get("id", j.get("job_id"))) == str(job_id)
        ),
        None
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found in HireSol API"
        )

    # Match and rank all students
    ranked_students = rank_students(job, students)

    total_students = len(ranked_students)

    # Count eligible students (60% or above)
    eligible_students = sum(
        1 for student in ranked_students
        if student["eligible"]
    )

    # Apply pagination
    start = (page - 1) * page_size
    end = start + page_size

    results = ranked_students[start:end]

    total_pages = (
        (total_students + page_size - 1) // page_size
        if total_students else 0
    )

    return {
        "job_id": job_id,
        "job_title": job.get("title"),
        "total_students": total_students,
        "eligible_students": eligible_students,
        "not_eligible_students": total_students - eligible_students,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "ranked_students": results
    }


# Top matching students API
@app.get("/match/{job_id}/top")
def get_top_matches(
    job_id: int,
    top_n: int = Query(10, ge=1, le=1000)
):

    jobs = get_jobs()
    students = get_students()

    # Find the job from HireSol API
    job = next(
        (
            j for j in jobs
            if str(j.get("id", j.get("job_id"))) == str(job_id)
        ),
        None
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found in HireSol API"
        )

    # Match and rank students
    results = rank_students(job, students)

    # Get top matching students
    matches = results[:top_n]

    return {
        "job_id": job_id,
        "job_title": job.get("title"),
        "total_students": len(students),
        "top_n": top_n,
        "matches": matches
    }


# Health check API
@app.get("/health")
def health_check(db: Session = Depends(get_db)):

    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "service": "HireSol Matching Microservice",
            "database": "connected"
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )
