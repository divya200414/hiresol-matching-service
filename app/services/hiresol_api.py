import os
import time
import requests

BASE_URL = "https://hiresol.cloud/api/matching/v1"

API_KEY = os.getenv("HIRESOL_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}


def call_api(method, endpoint, **kwargs):
    """Send a request to HireSol API."""

    if not API_KEY:
        raise ValueError("HireSol API key is missing.")

    url = f"{BASE_URL}/{endpoint}"

    for attempt in range(5):
        response = requests.request(
            method,
            url,
            headers=HEADERS,
            timeout=60,
            **kwargs
        )

        if response.status_code == 429 or response.status_code >= 500:
            wait_time = int(
                response.headers.get("Retry-After", 2 ** attempt)
            )
            time.sleep(wait_time)
            continue

        response.raise_for_status()
        return response.json()

    response.raise_for_status()


def fetch_all(endpoint, **params):
    """Fetch all pages from HireSol API."""

    cursor = None
    all_records = []

    while True:
        query = {
            **params,
            "limit": 500
        }

        if cursor:
            query["cursor"] = cursor

        data = call_api("GET", endpoint, params=query)

        all_records.extend(data["data"])

        pagination = data["pagination"]

        if not pagination["has_more"]:
            break

        cursor = pagination["next_cursor"]

    return all_records


def get_students():
    return fetch_all("students")


def get_jobs():
    jobs = fetch_all("jobs", status="all")

    return [
        job for job in jobs
        if job.get("status") == "live"
    ]
