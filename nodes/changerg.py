from langgraph.graph import StateGraph, START, END
from nodes.state2 import emailstr
from nodes.owner import owner_node
from auth_service.db import get_meeting

async def build_ch_graph():
    graph = StateGraph(emailstr)
    graph.add_node("changer",owner_node)
    graph.add_edge(START, "changer")
    graph.add_edge("changer", END)
    app=graph.compile()
    return app
