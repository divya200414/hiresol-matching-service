# HireSol Matching Microservice

## Overview

The HireSol Matching Microservice helps identify suitable students for different job opportunities based on their skills and profiles.

It connects to HireSol APIs, fetches student and job details, compares their skills, calculates match percentages, and ranks students based on their suitability for each job.

The main goal is to make the student-job matching process faster and easier, especially when handling a large number of student profiles and job opportunities.

## Features

- Fetches student profiles and job details from HireSol APIs.
- Extracts skills from student profiles and job requirements.
- Supports exact and related skill matching.
- Calculates match percentages for each student.
- Ranks students based on their matching scores.
- Shortlists students with a match percentage of 60% or above.
- Supports pagination and top matching results.
- Handles API pagination and temporary request failures.
- Runs the matching process automatically twice a day.
- Provides API health checks and error handling.

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
- Requests

## Project Structure

```text
hiresol-matching-service/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── README.md
│   │
│   └── services/
│       ├── hiresol_api.py
│       ├── matching_service.py
│       └── scheduler.py
│
├── .env
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── benchmark.py
```

## HireSol API Configuration

The matching service connects to HireSol APIs to retrieve student and job information.

### API Details

- **Base URL:** `https://hiresol.cloud/api/matching/v1`
- **Authentication:** Bearer Token
- **Environment Variable:** `HIRESOL_API_KEY`

### API Setup

1. Make sure you have access to the HireSol API and a valid API key.
2. Create a `.env` file in the project's root directory.
3. Add your API key using the following format:

```env
HIRESOL_API_KEY=your_actual_api_key
```

4. Save the file.
5. Keep your `.env` file private. Never upload your actual API key to GitHub.

The project includes a `.env.example` file as a sample configuration.

### API Integration

The service uses HireSol APIs to:

- Fetch student profiles.
- Retrieve job details.
- Filter jobs based on their live status.
- Retrieve all available records using cursor-based pagination.

The API integration also includes:

- Bearer Token authentication.
- Request timeout handling.
- Retry handling for rate limits (HTTP 429).
- Retry handling for server errors (HTTP 5xx).

The service fetches data from HireSol APIs instead of maintaining separate copies of student and job information.

## How the Matching Works

The matching process follows these steps:

1. Fetch student profiles from HireSol APIs.
2. Fetch job details and identify live jobs.
3. Extract skills from student profiles.
4. Identify the skills required for each job.
5. Compare student skills with job requirements.
6. Calculate the match percentage.
7. Rank students based on their matching scores.
8. Shortlist students who meet the minimum eligibility threshold.

### Matching Formula

**Match Percentage = (Matched Skills / Total Required Skills) × 100**

For example:

If a job requires 5 skills and a student matches 4 of them:

**(4 / 5) × 100 = 80%**

The student receives an 80% match score and is considered eligible.

### Skill Matching

The matching system supports:

- Exact skill matching.
- Related skill matching.
- Skill normalization.
- Different skill formats.
- Avoiding duplicate skill matches.

Students with a match percentage of 60% or above are considered eligible.

## API Endpoints

The service provides the following endpoints:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check service status |
| GET | `/health` | Check database connection |
| POST | `/seed` | Add sample data for testing |
| GET | `/match/{job_id}` | Get ranked students with pagination |
| GET | `/match/{job_id}/top` | Get top matching students |

### Example API Requests

Get ranked students for a job:

```http
GET /match/4
```

Get the top 10 matching students:

```http
GET /match/4/top?top_n=10
```

Get the second page of results:

```http
GET /match/4?page=2&page_size=10
```

## Automatic Matching Scheduler

The service uses APScheduler to run the matching process automatically twice a day.

**Schedule (IST):**

- Morning: 9:00 AM
- Evening: 9:00 PM

During each scheduled run:

1. Fetches the latest student profiles.
2. Fetches all live jobs.
3. Matches students against each job.
4. Identifies students with at least 60% matching scores.
5. Prints eligible student counts in the application logs.

The scheduler uses the Asia/Kolkata timezone.

The current implementation logs matching results. It does not automatically upload shortlisted results back to HireSol.

## Running the Project with Docker

### Prerequisites

- Python
- Docker Desktop
- Docker Compose
- HireSol API access and a valid API key

### Step 1: Configure Environment Variables

Create a `.env` file in the project root:

```env
HIRESOL_API_KEY=your_actual_api_key
```

### Step 2: Build and Start Services

```bash
docker compose up -d --build
```

### Step 3: Check Running Containers

```bash
docker compose ps
```

### Step 4: View Application Logs

```bash
docker compose logs api
```

### Step 5: Open API Documentation

Once the application is running, open:

`http://localhost:8000/docs`

You can use Swagger UI to test the available API endpoints.

## Running the Project Locally

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Configure the `HIRESOL_API_KEY` environment variable in the root `.env` file.

Start the FastAPI application:

```bash
uvicorn app.main:app --reload
```

Open the API documentation:

`http://localhost:8000/docs`

## Testing and Results

The matching service has been tested using student and job data fetched from HireSol APIs.

### Example Test Results

**Job:** Software Developer Winter Internship

| Metric | Result |
|---|---:|
| Total students checked | 338 |
| Eligible students | 134 |
| Not eligible students | 204 |
| Top 10 matches | 100% |

The service was also tested earlier with more than 10,000 sample student records for performance evaluation.

### Scheduler Testing

The matching process was manually executed to verify that:

- Student data could be fetched successfully.
- Live jobs could be retrieved.
- Matching was performed for each job.
- Eligible student counts were calculated.
- The process completed successfully.

The automatic scheduler configuration was also verified for its 9 AM and 9 PM IST execution times.

## Security

- API credentials are stored in environment variables.
- The `.env` file is excluded through `.gitignore`.
- Actual API keys should never be committed to GitHub.
- The `.env.example` file contains only a sample configuration.

## Project Objective

The objective of this project is to help HireSol identify suitable students for job opportunities based on their skills and profiles.

By automating skill comparison, match percentage calculation, ranking, and shortlisting, the service makes the matching process easier to manage as the number of students and job opportunities grows.