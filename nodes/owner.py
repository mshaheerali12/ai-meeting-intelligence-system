from nodes.llm import llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser,JsonOutputParser
from nodes.state2 import emailstr
from auth_service.db import extract_meeting
import json


async def owner_node(state: emailstr) -> dict:
    prompt=ChatPromptTemplate.from_messages([
        ("system",
         """You are an AI assistant that extracts action items from meeting transcripts.

Your task is to identify ONLY explicitly stated tasks and assign them to the correct person.

==============================
STRICT RULES (MANDATORY)
==============================

1. Do NOT invent or assume any tasks.
2. Only extract tasks that are clearly stated or strongly implied.
3. Do NOT guess task ownership.
4. If no owner is واضح (clear), assign it to "Unassigned".
5. Use EXACT participant names as given. Do NOT modify or split names.
6. Do NOT merge different people.
7. Do NOT rephrase names (e.g., "S afa" → must be "Safa" if provided like that).
8. Keep tasks short and clear (1 line each).
9. Do NOT include explanations.

==============================
INPUT CONTEXT
==============================

You will receive:
- Meeting transcription
- List of participants (names)

You MUST only assign tasks to names from the participant list.

==============================
OUTPUT FORMAT (STRICT JSON)
==============================

Return ONLY valid JSON.

Format:

{{
  "Name 1": ["task 1", "task 2"],
  "Name 2": ["task 1"],
  "Unassigned": ["task 1"]
}}

NO text before or after JSON.
NO explanations.
NO markdown.
ONLY JSON.

==============================
FINAL CHECK
==============================

- JSON must be valid
- Keys must match participant names exactly
- No extra text outside JSON
"""),
        ("human",
         """
Participants:
{participants}

Transcription:
{transcription}

Task:
Extract action items and assign them to the correct person.
""")
    ])
    chain= prompt | llm() | JsonOutputParser()
    result=await chain.ainvoke({"participants": state["participants"], "transcription": state["transcription"]})
    if not result :
        raise ValueError("Empty owner assignment result returned by LLM")
    
    
    return {"assign_task": result}
    
  
    
