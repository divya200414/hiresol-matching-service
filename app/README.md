# HireSol Matching Microservice

A FastAPI-based microservice that matches students with job requirements and ranks students based on their skill match percentage.

## Features

- Student and job skill matching
- Match percentage calculation
- Global student ranking
- Pagination support
- Top matching students API
- Input validation
- Database health check
- Database indexing
- Performance testing with 10,000+ students

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Service status |
| GET | `/health` | Database health |
| POST | `/seed` | Insert sample data |
| GET | `/match/{job_id}` | Ranked students with pagination |
| GET | `/match/{job_id}/top` | Top matching students |

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start server:

```bash
uvicorn app.main:app --reload
```

Swagger documentation:

http://127.0.0.1:8000/docs

## Matching Formula

Match Percentage = (Matched Skills / Required Skills) × 100