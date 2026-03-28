from langgraph.graph import StateGraph, END

from agent.state import AgentState
from agent.nodes import fetch_jobs_node
from agent.nodes import load_resume_node
from agent.nodes import llm_rank_jobs_node


def build_graph():

    workflow = StateGraph(AgentState)

    # 3 nodes — fetch, resume, rank
    workflow.add_node("fetch_jobs",   fetch_jobs_node)
    workflow.add_node("load_resume",  load_resume_node)
    workflow.add_node("rank_jobs",    llm_rank_jobs_node)

    workflow.set_entry_point("fetch_jobs")

    workflow.add_edge("fetch_jobs",  "load_resume")
    workflow.add_edge("load_resume", "rank_jobs")
    workflow.add_edge("rank_jobs",   END)

    return workflow.compile()
