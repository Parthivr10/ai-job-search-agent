from tools.adzuna_api import fetch_adzuna_jobs
from tools.jooble_api import fetch_jooble_jobs
from tools.resume_parser import extract_resume_text
from tools.resume_skills import extract_resume_skills
from agent.llm import llm

import json
import concurrent.futures


# NODE 1 — FETCH JOBS  (parallel API calls)
def fetch_jobs_node(state):

    query = state["query"]

    print("\n[1/3] Fetching jobs from Adzuna & Jooble in parallel...")

    # run both APIs at the same time
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_adzuna = executor.submit(fetch_adzuna_jobs, query)
        future_jooble = executor.submit(fetch_jooble_jobs, query)

        adzuna_jobs = future_adzuna.result()
        jooble_jobs = future_jooble.result()

    print(f"   Adzuna: {len(adzuna_jobs)} jobs")
    print(f"   Jooble: {len(jooble_jobs)} jobs")

    jobs = adzuna_jobs + jooble_jobs

    # deduplicate by URL
    seen = set()
    unique_jobs = []

    for job in jobs:
        url = job.get("url")
        if not url or url in seen:
            continue
        seen.add(url)

        # filter jobs older than 30 days
        posted = job.get("posted", "")
        if "days ago" in posted:
            try:
                days = int(posted.split()[0])
                if days > 30:
                    continue
            except:
                pass

        unique_jobs.append(job)

    state["jobs"] = unique_jobs[:20]

    print(f"   Total unique jobs after dedup: {len(state['jobs'])}")

    return state


# NODE 2 — LOAD RESUME
def load_resume_node(state):

    resume_path = state.get("resume_path")

    if not resume_path:
        raise ValueError("No resume file provided")

    print("\n[2/3] Extracting skills from resume...")

    text = extract_resume_text(resume_path)
    skills = extract_resume_skills(text)

    state["resume_skills"] = skills

    print(f"   Skills found: {skills}")

    return state



# NODE 3 — LLM RANK JOBS
def llm_rank_jobs_node(state):

    jobs = state.get("jobs", [])
    resume_skills = state.get("resume_skills", [])

    if not jobs:
        state["ranked_jobs"] = []
        return state

    print("\n[3/3] Asking LLM to rank jobs based on resume skills...")

    # build job list text for the prompt
    jobs_text = ""

    for i, job in enumerate(jobs):
        salary = job.get("salary", "")
        salary_line = f"Salary: {salary}" if salary else ""

        jobs_text += f"""
Job {i+1}:
Title: {job.get("title", "")}
Company: {job.get("company", "")}
Location: {job.get("location", "")}
{salary_line}
Description: {job.get("description", "")[:800]}
---"""

    prompt = f"""
You are an expert technical recruiter.

A candidate has these skills extracted from their resume:
{resume_skills}

Below are {len(jobs)} job listings.

For each job, analyze how well the candidate's skills match the job requirements.
Consider the job title, description, and required skills.

Return ONLY a valid JSON array with exactly {len(jobs)} objects in the same order as the jobs listed.

Each object must have:
- "match_score": integer from 0 to 100 (percentage match)
- "match_reason": one short sentence explaining why this score (max 15 words)
- "matched_skills": list of skills from the candidate that are relevant to this job

Example format:
[
  {{
    "match_score": 85,
    "match_reason": "Strong Python and RAG experience aligns well with this GenAI role.",
    "matched_skills": ["python", "rag", "langchain"]
  }}
]

Jobs to rank:
{jobs_text}

Return ONLY the JSON array. No explanation. No markdown.
"""

    response = llm.invoke(prompt)

    # parse LLM response
    try:
        raw = response.content.strip()

        # strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        rankings = json.loads(raw.strip())

    except Exception as e:
        print(f"   LLM parsing failed: {e} — using default scores")
        rankings = [
            {"match_score": 0, "match_reason": "Could not analyze.", "matched_skills": []}
            for _ in jobs
        ]

    # merge LLM rankings back into job dicts
    ranked = []

    for i, job in enumerate(jobs):
        r = rankings[i] if i < len(rankings) else {}

        ranked.append({
            "title":         job.get("title", ""),
            "company":       job.get("company", ""),
            "location":      job.get("location", ""),
            "posted":        job.get("posted", ""),
            "salary":        job.get("salary", ""),
            "url":           job.get("url", ""),
            "description":   job.get("description", ""),
            "score":         r.get("match_score", 0),
            "match_reason":  r.get("match_reason", ""),
            "matched_skills": r.get("matched_skills", []),
        })

    # sort by score descending
    ranked.sort(key=lambda x: x["score"], reverse=True)

    state["ranked_jobs"] = ranked[:10]

    print(f"   Top match: {ranked[0]['title']} at {ranked[0]['company']} — {ranked[0]['score']}%")

    return state
