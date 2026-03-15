from langgraph.graph import StateGraph, START, END
from nodes.deep import transcribe  

from nodes.state import meemory
async def graph_building():
    graph = StateGraph(meemory)

    # Nodes
    graph.add_node("deepgram_node", transcribe)
    graph.add_edge(START, "deepgram_node")
    graph.add_edge("deepgram_node",END)
      
    return  graph.compile()