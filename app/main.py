from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import func
from app.database import Base, engine, SessionLocal
from app.models.student import Student
from app.models.job import Job
from app.models.skill import Skill, StudentSkill, JobSkill
from sqlalchemy.orm import Session
from sqlalchemy import text
app = FastAPI(title="HireSol Matching Microservice")

Base.metadata.create_all(bind=engine)
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

    connection.commit()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {
        "message": "HireSol Matching Microservice is running"
    }


@app.post("/seed")
def seed_database(db: Session = Depends(get_db)):

    if db.query(Student).first():
        return {"message": "Sample data already exists"}

    # Create Skills
    python = Skill(name="Python")
    flask = Skill(name="Flask")
    mysql = Skill(name="MySQL")
    django = Skill(name="Django")
    react = Skill(name="React")

    db.add_all([python, flask, mysql, django, react])
    db.commit()

    # Create Students
    ayush = Student(name="Ayush")
    rahul = Student(name="Rahul")
    priya = Student(name="Priya")

    db.add_all([ayush, rahul, priya])
    db.commit()

    # Assign Skills to Students
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

    # Create Job
    job = Job(title="Python Developer")

    db.add(job)
    db.commit()

    # Assign Required Skills to Job
    job.required_skills = [
        JobSkill(skill=python),
        JobSkill(skill=flask),
        JobSkill(skill=mysql)
    ]

    db.commit()

    return {
        "message": "Sample data added successfully"
    }


# Matching API with Pagination
# Matching API with Global Ranking and Pagination
@app.get("/match/{job_id}")
def match_students(
    job_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    required_skills = db.query(func.count(JobSkill.skill_id))\
        .filter(JobSkill.job_id == job_id)\
        .scalar()

    total_students = db.query(Student).count()

    if required_skills == 0:
        return {"message": "Job has no required skills"}

    ranked_query = (
        db.query(
            Student,
            func.count(JobSkill.skill_id).label("matched_skills")
        )
        .outerjoin(StudentSkill, Student.id == StudentSkill.student_id)
        .outerjoin(
            JobSkill,
            (JobSkill.job_id == job_id) &
            (JobSkill.skill_id == StudentSkill.skill_id)
        )
        .group_by(Student.id)
        .order_by(
            func.count(JobSkill.skill_id).desc(),
            Student.id.asc()
        )
    )

    ranked_students = ranked_query\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()

    student_ids = [student.id for student, _ in ranked_students]

    matched_skills_data = (
        db.query(StudentSkill.student_id, Skill.name)
        .join(Skill, StudentSkill.skill_id == Skill.id)
        .join(
            JobSkill,
            JobSkill.skill_id == StudentSkill.skill_id
        )
        .filter(
            JobSkill.job_id == job_id,
            StudentSkill.student_id.in_(student_ids)
        )
        .all()
    )

    skills_map = {}

    for student_id, skill_name in matched_skills_data:
        skills_map.setdefault(student_id, []).append(skill_name)

    results = []

    for student, matched_count in ranked_students:
        results.append({
            "student_id": student.id,
            "student_name": student.name,
            "match_percentage": round(
                matched_count / required_skills * 100, 2
            ),
            "matched_skills": sorted(
                skills_map.get(student.id, [])
            )
        })

    total_pages = (
        (total_students + page_size - 1) // page_size
        if total_students else 0
    )

    return {
        "job_id": job.id,
        "job_title": job.title,
        "total_students": total_students,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "ranked_students": results
    }


# Top Matching Students API
@app.get("/match/{job_id}/top")
def get_top_matches(
    job_id: int,
    top_n: int = Query(10, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    required_skills = db.query(func.count(JobSkill.skill_id))\
        .filter(JobSkill.job_id == job_id)\
        .scalar()

    if required_skills == 0:
        return {"message": "Job has no required skills"}

    results = (
        db.query(
            Student,
            func.count(JobSkill.skill_id).label("matched_skills")
        )
        .outerjoin(StudentSkill, Student.id == StudentSkill.student_id)
        .outerjoin(
            JobSkill,
            (JobSkill.job_id == job_id) &
            (JobSkill.skill_id == StudentSkill.skill_id)
        )
        .group_by(Student.id)
        .order_by(
            func.count(JobSkill.skill_id).desc(),
            Student.id.asc()
        )
        .limit(top_n)
        .all()
    )

    matches = []

    for student, matched_skills in results:
        percentage = round(
            (matched_skills / required_skills) * 100, 2
        )

        matches.append({
            "student_id": student.id,
            "student_name": student.name,
            "matched_skills": matched_skills,
            "total_required_skills": required_skills,
            "match_percentage": percentage
        })

    return {
        "job_id": job_id,
        "top_n": top_n,
        "matches": matches
    }

with engine.connect() as connection:
    connection.exec_driver_sql(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_student_skill "
        "ON student_skills(student_id, skill_id)"
    )
    connection.exec_driver_sql(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_job_skill "
        "ON job_skills(job_id, skill_id)"
    )
    connection.commit() 
    
     
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