import sys
import os
from dotenv import load_dotenv

load_dotenv()

from agent.graph import build_graph


# PRETTY PRINT HELPER
def print_job(rank, job):

    score        = job.get("score", 0)
    title        = job.get("title", "N/A")
    company      = job.get("company", "N/A")
    location     = job.get("location", "N/A")
    posted       = job.get("posted", "N/A")
    salary       = job.get("salary", "")
    url          = job.get("url", "")
    description  = job.get("description", "")[:300]
    reason       = job.get("match_reason", "")
    matched      = job.get("matched_skills", [])


    filled = int(score / 10)
    bar    = "█" * filled + "░" * (10 - filled)

    print(f"\n{'─'*60}")
    print(f"  #{rank}  [{bar}] {score}%  MATCH")
    print(f"{'─'*60}")
    print(f" {title}")
    print(f" {company}")
    print(f" {location}")
    print(f" {posted}")

    if salary:
        print(f"{salary}")
    if reason:
        print(f"{reason}")
    if matched:
        print(f"Matched skills : {', '.join(matched)}")
    if description:
        print(f"\n{description.strip()}...")
    if url:
        print(f"\n{url}")


# MAIN
def main():

    print("\n" + "═"*60)
    print("         🤖  AI JOB SEARCH AGENT  (CLI)")
    print("═"*60)

    #get query
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("\nEnter your job search query: ").strip()

    if not query:
        print("No query entered. Exiting.")
        sys.exit(1)

    #get resume path
    resume_path = input("Enter path to your resume PDF: ").strip()

    if not resume_path or not os.path.exists(resume_path):
        print(f"Resume file not found: {resume_path}")
        sys.exit(1)

    print(f"\n🔍  Query   : {query}")
    print(f"📄  Resume  : {resume_path}")
    print("\nStarting agent...\n")

    #run agent
    app = build_graph()

    result = app.invoke({
        "query":       query,
        "resume_path": resume_path,
        "jobs":        [],
        "ranked_jobs": [],
        "resume_skills": []
    })

    ranked_jobs = result.get("ranked_jobs", [])

    if not ranked_jobs:
        print("\nNo jobs found. Try a different query.")
        sys.exit(0)

    #print results
    print(f"\n\n{'═'*60}")
    print(f"  🎯  TOP {len(ranked_jobs)} MATCHES FOR:  \"{query}\"")
    print(f"{'═'*60}")

    for i, job in enumerate(ranked_jobs, start=1):
        print_job(i, job)

    print(f"\n{'═'*60}\n")


if __name__ == "__main__":
    main()
