import requests
import os
from tools.utils import time_ago

ADZUNA_APP_ID  = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")


def fetch_adzuna_jobs(query):

    jobs = []

    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

    params = {
        "app_id":           ADZUNA_APP_ID,
        "app_key":          ADZUNA_APP_KEY,
        "results_per_page": 20,
        "what":             query,
        "max_days_old":     30
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print("Adzuna API error:", response.text)
            return []

        data = response.json()

    except Exception as e:
        print("Adzuna failed:", e)
        return []

    for job in data.get("results", []):

        # salary
        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")

        if salary_min and salary_max:
            salary = f"₹{int(salary_min):,} - ₹{int(salary_max):,}"
        elif salary_min:
            salary = f"₹{int(salary_min):,}+"
        else:
            salary = ""

        jobs.append({
            "title":       job.get("title", ""),
            "company":     job.get("company", {}).get("display_name", ""),
            "location":    job.get("location", {}).get("display_name", ""),
            "url":         job.get("redirect_url", ""),
            "description": job.get("description", ""),
            "posted":      time_ago(job.get("created", "")),
            "salary":      salary,
        })

    return jobs
