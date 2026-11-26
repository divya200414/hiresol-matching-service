from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from app.services.hiresol_api import get_students, get_jobs
from app.services.matching_service import rank_students


scheduler = BackgroundScheduler(timezone="Asia/Kolkata")


def run_matching():

    print(f"\nMatching started at: {datetime.now()}")

    try:
        # Fetch actual data from HireSol
        students = get_students()
        jobs = get_jobs()

        print(f"Students fetched: {len(students)}")
        print(f"Live jobs fetched: {len(jobs)}")

        total_matches = 0

        for job in jobs:

            # Calculate student-job matching
            results = rank_students(job, students)

            # Select students with 60% or above match
            eligible_students = [
                student for student in results
                if student["eligible"]
            ]

            total_matches += len(eligible_students)

            print(
                f"Job: {job['title']} | "
                f"Eligible students: {len(eligible_students)}"
            )

        print(f"Total eligible matches: {total_matches}")
        print("Matching completed successfully.")

    except Exception as error:
        print(f"Matching failed: {error}")


def start_scheduler():

    if scheduler.running:
        return

    scheduler.add_job(
        run_matching,
        CronTrigger(hour=9, minute=0, timezone="Asia/Kolkata"),
        id="morning_matching",
        replace_existing=True
    )

    scheduler.add_job(
        run_matching,
        CronTrigger(hour=21, minute=0, timezone="Asia/Kolkata"),
        id="evening_matching",
        replace_existing=True
    )

    scheduler.start()

    print("Scheduler started successfully")


    for job in scheduler.get_jobs():
        print(f"Scheduled job: {job.id} | Next run: {job.next_run_time}")