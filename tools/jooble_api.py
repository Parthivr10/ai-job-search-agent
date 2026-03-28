import requests
import os
from tools.utils import time_ago

JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY")


def fetch_jooble_jobs(query):

    jobs = []

    url = f"https://jooble.org/api/{JOOBLE_API_KEY}"

    payload = {
        "keywords": query,
        "location": "India"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code != 200:
            print("Jooble API error:", response.text)
            return []

        data = response.json()

    except Exception as e:
        print("Jooble failed:", e)
        return []

    for job in data.get("jobs", []):

        jobs.append({
            "title":       job.get("title", ""),
            "company":     job.get("company", ""),
            "location":    job.get("location", ""),
            "url":         job.get("link", ""),
            "description": job.get("snippet", ""),
            "posted":      time_ago(job.get("updated", "")),
            "salary":      "",   # Jooble doesn't reliably return salary
        })

    return jobs
