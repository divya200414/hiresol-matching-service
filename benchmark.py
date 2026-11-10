import time
from sqlalchemy import insert
from app.models.job import Job
from app.database import SessionLocal
from app.models.student import Student
from app.models.skill import Skill, StudentSkill

db = SessionLocal()

try:
    start = time.time()

    skills = db.query(Skill).all()
    skill_ids = [skill.id for skill in skills]

    if not skill_ids:
        print("Skills not found. Run /seed first.")
        exit()

    students_data = [
        {"name": f"TestStudent_{i}"}
        for i in range(1, 10001)
    ]

    student_ids = db.execute(
        insert(Student).returning(Student.id),
        students_data
    ).scalars().all()

    student_skills = []

    for student_id in student_ids:
        for skill_id in skill_ids[:3]:
            student_skills.append({
                "student_id": student_id,
                "skill_id": skill_id
            })

    db.execute(insert(StudentSkill), student_skills)
    db.commit()

    print("10,000 students added successfully!")
    print("Time taken:", round(time.time() - start, 2), "seconds")

finally:
    db.close()
