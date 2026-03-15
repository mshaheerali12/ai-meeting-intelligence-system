from langgraph.graph import StateGraph, END
from nodes.state import meemory
from langgraph.checkpoint.redis import RedisSaver
from nodes.retriver import meeting_retriver
from nodes.evaluater import doc_eval_node
from nodes.query import web_query_ref
from nodes.tavily import web_Search
from nodes.filter import filteration
from nodes.generatiion import generate



def decide_route(state: meemory):

    verdict = state["verdict"]

    if verdict == "correct":
        return "filter"

    elif verdict == "incorrect":
        return "web_query"

    else:
        return "web_query"


async def build_graph():

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
 
    graph = builder.compile()

    return graph