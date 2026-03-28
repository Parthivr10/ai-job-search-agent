from typing import TypedDict, List


class AgentState(TypedDict):

    query: str
    jobs: List[dict]
    ranked_jobs: List[dict]
    resume_path: str
    resume_skills: List[str]
