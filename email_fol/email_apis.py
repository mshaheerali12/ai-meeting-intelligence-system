from fastapi import APIRouter,Depends,Request,Form
from auth_service.db import get_meeting,get_v_Trans_meeting
from auth_service.database import collection2
from auth_service.security import verify_token
app=APIRouter()
@app.post("/automails")
async def auto_mails(request:Request,meeting_id:str=Form(...),user=Depends(verify_token)):
    try:
        e_graph= request.app.state.em_graph
        transcription=await get_meeting(meeting_id) or await get_v_Trans_meeting(meeting_id)
        doc=await collection2.find_one({"id":meeting_id})
        
        if not doc:
            return {"participant didnt found"}
        participant=[p["name"]for p in doc.get("participants",[])]
        intial_State={
             "meeting_id":meeting_id,
             "participants":participant,
             "transcription":transcription
        }
        result=await e_graph.ainvoke(intial_State)
        return {
            "message":"email send successfully"
        }
    except Exception as e:
        return {
            "message":f"internal server error {e}" 
        }