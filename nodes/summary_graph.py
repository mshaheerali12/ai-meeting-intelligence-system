from nodes.meeting_nodes import summarizer_node
from nodes.state import meemory
from langgraph.graph import StateGraph,START,END
async def summarizer_graph():
    graph=StateGraph(meemory)
    graph.add_node("summary",summarizer_node)
    graph.add_edge(START,"summary")
    graph.add_edge("summary",END)
    return graph.compile()   
