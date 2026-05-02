from langgraph.graph import StateGraph,START,END
from nodes.prse import graph_invoker
from nodes.changerg import build_ch_graph
from nodes.final_stucture_email import sendingmails
from nodes.emails_parser_text import send_email
from nodes.state2 import emailstr
async def email_graph_building():
    graph=StateGraph(emailstr)
    
    graph.add_node("inv",graph_invoker)
    graph.add_node("final",sendingmails)
    graph.add_node("final2",send_email)
    graph.add_edge(START,"inv")
    graph.add_edge("inv","final")
    graph.add_edge("final","final2")
    graph.add_edge("final2",END)
    return graph.compile()