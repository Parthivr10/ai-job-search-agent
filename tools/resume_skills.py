from agent.llm import llm
import json


def extract_resume_skills(resume_text):

    prompt = f"""
Extract the technical skills from this resume.

Return ONLY valid JSON array of strings.

Example:
["python", "machine learning", "langchain", "rag"]

Resume:
{resume_text}

Return ONLY the JSON array. No explanation. No markdown.
"""

    response = llm.invoke(prompt)

    try:
        raw = response.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        skills = json.loads(raw.strip())

    except Exception as e:
        print(f"Failed to parse resume skills: {e}")
        skills = []

    return [s.lower() for s in skills]
