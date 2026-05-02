from nodes.meeting_nodes import extract_action_items_node
from nodes.state import meemory
from langsmith import traceable
from langgraph.graph import StateGraph,START,END
@traceable(name="build action item extraction graph")
async def extract_action_items_graph():
    graph=StateGraph(meemory)
    graph.add_node("extract_action_items",extract_action_items_node)
    graph.add_edge(START,"extract_action_items")
    graph.add_edge("extract_action_items",END)
    return graph.compile()