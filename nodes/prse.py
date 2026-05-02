from nodes.changerg import build_ch_graph
from nodes.state2 import emailstr
from auth_service.db import get_meeting
from auth_service.database import collection2

async def graph_invoker(state: emailstr):
    graph = await build_ch_graph()
    
    initial_state={
        "meeting_id":state["meeting_id"],
        "participants":state["participants"],
        "transcription":state["transcription"]

    }
    result = await graph.ainvoke(initial_state)
    tasks = result.get("assign_task", {})
    return { 
        **state,
        "assign_task":tasks}