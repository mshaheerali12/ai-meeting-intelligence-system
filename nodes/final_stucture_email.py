from nodes.emails_parser_text import  send_email
from auth_service.database import collection2
from nodes.state2 import emailstr
from datetime import datetime
async def sendingmails(state: emailstr):
    key = state['meeting_id']
    docs = await collection2.find_one({"id": key})

    if not docs:
        return state

    task_map = state.get("assign_task", {})
    subject = docs.get("agenda", "Meeting Task")

    emails_payload = []

    for p in docs.get("participants", []):
        name = p["name"]
        email = p["email"]

        # get tasks for this specific person
        tasks = task_map.get(name, [])

        if not tasks:
            continue  # skip if no tasks

        # build body for THIS person only
        body = f"Hi {name},\n\nYour tasks:\n"
        for t in tasks:
            body += f"- {t}\n"

        body += "\n_________________________________\n"

        emails_payload.append({
            "to": email,
            "body": body
        })

    return {
        **state,
        "emails_payload": emails_payload,
        "subject": subject}



    


