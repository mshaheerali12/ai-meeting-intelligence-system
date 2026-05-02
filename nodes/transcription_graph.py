from nodes.meeting_nodes import transcription_node
from nodes.state import meemory
from langgraph.graph import StateGraph,START,END
from langsmith import traceable

@traceable(name="build transcription graph")
async def transcript_graph():
    graph=StateGraph(meemory)
    graph.add_node("transcription",transcription_node)
    graph.add_edge(START,"transcription")
    graph.add_edge("transcription",END)
    return graph.compile()