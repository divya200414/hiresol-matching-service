# HireSol Matching Microservice

This project helps HireSol find suitable students for different job opportunities based on their skills and profiles.

It fetches student and job details from HireSol APIs, compares their skills, calculates match percentages, and ranks students based on how well they fit each job.

## Features

- Fetches student and job details from HireSol APIs.
- Compares student skills with job requirements.
- Calculates match percentages.
- Supports exact and related skill matching.
- Ranks students based on their match scores.
- Shortlists students with a match of 60% or above.
- Supports pagination and top student matching results.
- Runs the matching process automatically twice a day.
- Includes API health checks and error handling.

## Technologies Used

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Docker
- Docker Compose
- APScheduler
- RapidFuzz
- Pydantic

## How It Works

The matching service works with data from HireSol APIs.

1. Fetches student profiles and live job details.
2. Extracts skills from student profiles and job requirements.
3. Compares the skills to find suitable matches.
4. Calculates a match percentage for each student.
5. Ranks students based on their scores.
6. Shortlists students who have at least a 60% match.

The service uses HireSol APIs for student and job data instead of maintaining separate copies of that data.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check service status |
| GET | `/health` | Check database connection |
| POST | `/seed` | Add sample data for testing |
| GET | `/match/{job_id}` | Get ranked students with pagination |
| GET | `/match/{job_id}/top` | Get top matching students |

## Matching Logic

The match percentage is calculated using:

**Match Percentage = (Matched Skills / Required Skills) × 100**

For example, if a job requires 5 skills and a student has 4 matching skills, the match percentage will be 80%.

Students with a match percentage of 60% or above are considered eligible.

The matching process also handles related skills, different skill formats, and duplicate matches.

## Automatic Matching

The service uses APScheduler to run the matching process twice a day.

- Morning: 9:00 AM IST
- Evening: 9:00 PM IST

During each run, it fetches the latest student and job details, checks the matches for every live job, and prints the eligible student counts in the logs.

## Running with Docker

Build and start the services:

```bash
docker compose up -d --build
```

Check running containers:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs api
```

## Running Locally

Install the required packages:

```bash
pip install -r requirements.txt
```

Add the required HireSol API credentials to your `.env` file.

Start the application:

```bash
uvicorn app.main:app --reload
```

## API Documentation

After starting the application, open the Swagger documentation:

http://localhost:8000/docs

You can use it to test the available endpoints and view their responses.

## Testing

The matching service has been tested with real student and job data fetched from HireSol APIs.

Example results for the **Software Developer Winter Internship**:

- Total students checked: 338
- Eligible students: 134
- Not eligible students: 204
- Top 10 matches: 100%

Performance testing was also carried out earlier using more than 10,000 sample student records.

## Project Objective

The main goal of this project is to make student-job matching easier for HireSol by automatically finding and ranking students based on their skills and job requirements.