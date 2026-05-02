from langgraph.graph import StateGraph, END
from langgraph.checkpoint.redis import AsyncRedisSaver
from nodes.state import meemory
from nodes.retriver import meeting_retriver
from nodes.evaluater import doc_eval_node
from nodes.query import web_query_ref
from nodes.tavily import web_Search
from nodes.filter import filteration
from nodes.generatiion import generate
from nodes.redi import get_retriever
import os
from langsmith import traceable
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_CHECKPOINTER_URL")

@traceable(name="decide route based on evaluation verdict")
def decide_route(state: meemory):
    verdict = state["verdict"]
    if verdict == "correct":
        return "filter"
    elif verdict == "incorrect":
        return "web_query"
    else:
        return "web_query"

@traceable(name="build RAG graph")
async def build_graph(checkpointer):
    builder = StateGraph(meemory)
    
    builder.add_node("retriever", meeting_retriver)
    builder.add_node("eval", doc_eval_node)
    builder.add_node("web_query", web_query_ref)
    builder.add_node("web_search", web_Search)
    builder.add_node("filter", filteration)
    builder.add_node("generate", generate)

    builder.set_entry_point("retriever")
    builder.add_edge("retriever", "eval")

    builder.add_conditional_edges(
        "eval",
        decide_route,
        {
            "filter": "filter",
            "web_query": "web_query"
        }
    )

    builder.add_edge("web_query", "web_search")
    builder.add_edge("web_search", "filter")
    builder.add_edge("filter", "generate")
    builder.add_edge("generate", END)

    graph = builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["generate"]
    )

    return graph
