from nodes.llm import llm
from nodes.state import meemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langsmith import traceable
import logging

model = llm()

# Fix Issue 6 — removed logging.basicConfig() which was:
# 1. Using filemode="w" wiping logs on every restart
# 2. Conflicting with main.py's logging.config.dictConfig
# Now uses standard getLogger — inherits config from main.py
logger = logging.getLogger(__name__)


@traceable(name="transcription node")
async def transcription_node(state: meemory):
    try:
        logger.info("Starting transcription node")

        if "raw_transcription" not in state or not state.get("raw_transcription"):
            logger.error("No raw transcription found in state")
            return {"transcription": "Error: No raw transcription found."}

        prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an intelligent meeting transcript editor and transformer.

Your job is to modify the transcript based on the user’s instruction while preserving accuracy and speaker structure.

==============================
CORE RULES (ALWAYS APPLY)
==============================

1. Do NOT remove or alter important meaning unless explicitly requested.
2. Do NOT mix or merge different speakers.
3. Keep each speaker clearly separated.
4. Preserve the original order of conversation.
5. Do NOT hallucinate new facts or add unrelated content.

==============================
SPEAKER FORMAT (STRICT)
==============================

- Keep speaker labels exactly as provided.
- Format each entry as:

Speaker Name: text

- Always start a new line when the speaker changes.

==============================
TRANSFORMATION RULES
==============================

- Apply the user’s instruction as requested.
- The instruction can include:
  - Tone change (funny, formal, casual, dramatic, etc.)
  - Style change (short summary, detailed version, bullet-like clarity but still plain text)
  - Rewriting for clarity or simplicity
  - Translation or paraphrasing

- You MAY:
  - Rephrase sentences
  - Adjust tone and wording
  - Improve readability

- You MUST:
  - Keep the original meaning intact (unless user explicitly asks to change it)
  - Keep all key information
  - Keep speaker mapping correct

==============================
FORMATTING RULES
==============================

- Use clean, natural sentences
- No markdown, no bullet points
- Plain text only
- Make it easy to read


==============================
TASK
==============================

Transform the transcript according to the instruction while preserving speaker structure and meaning."""
    ),
    (
        "human",
        """Raw transcription:
{response}

User instruction:
{instruction}

"""
    )
])

        chain = prompt | model | StrOutputParser()
        synthesis = await chain.ainvoke({
            "response": state["raw_transcription"],
            "instruction": state.get("instruction", "")
        })

        if not synthesis or not synthesis.strip():
            raise ValueError("Empty transcription result returned by LLM")

        logger.info("Transcription node completed successfully")
        return {"transcription": synthesis}

    except Exception as e:
        logger.error(f"Error in transcription node: {e}", exc_info=True)
        raise


@traceable(name="summarizer node")
async def summarizer_node(state: meemory):
    try:
        if "transcription" not in state or not state.get("transcription"):
            raise ValueError("Missing or empty transcription in state")

        prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an enterprise-grade AI Meeting Notes Assistant.

Your task is to extract and generate a structured, factual, and professional meeting summary
from a raw meeting transcription.

You must strictly follow all rules and output format.

==============================
RULES (MANDATORY)
==============================

1. Only use information explicitly present in the transcription.
2. Do not infer, assume, or fabricate any details.
3. Do not combine unrelated statements into one.
4. Preserve factual accuracy over fluency.
5. If any section has no clear data, output exactly: Not specified
6. Use concise and formal business language.
7. Do not include explanations, reasoning, or commentary.
8. Do not use markdown symbols, emojis, or decorative characters.
9. Maintain consistent formatting across all sections.
10. Extract information carefully from ALL parts of the transcription.

==============================
EXTRACTION GUIDELINES
==============================

- Action items must be explicit tasks or commitments.
- Decisions must reflect confirmed conclusions, not suggestions.
- Risks must reflect concerns, blockers, or uncertainties.
- Do not treat casual discussion as decisions or actions.

==============================
OUTPUT STRUCTURE (STRICT)
==============================

Meeting Overview:
Write exactly 3 to 5 sentences summarizing the discussion.

Key Topics:
- Topic 1
- Topic 2
(If none, write: Not specified)

Decisions Made:
- Decision 1
(If none, write: Not specified)

Action Items:
- Task: <description> | Owner: <name or "Not specified"> | Deadline: <date or "Not specified">
(If none, write: Not specified)

Risks or Concerns:
- Risk 1
(If none, write: Not specified)

Next Steps:
- Next step 1
(If none, write: Not specified)

==============================
FINAL CHECK (MANDATORY)
==============================

Before output:
- Ensure no hallucinated information is present.
- Ensure all sections follow the exact format.
- Ensure "Not specified" is used where appropriate.
"""
    ),
    (
        "human",
        "Generate the meeting summary strictly from the transcription below:\n\n{transcription}"
    )
])

        chain = prompt | model | StrOutputParser()
        summary = await chain.ainvoke({"transcription": state["transcription"]})

        if not summary or not summary.strip():
            raise ValueError("Empty summary result returned by LLM")

        logger.info("Summarizer node completed successfully")
        return {"summary": summary}

    except Exception as e:
        logger.error(f"Error in summarizer node: {e}", exc_info=True)
        raise
@traceable(name="extract action items node")
async def extract_action_items_node(state: meemory):
    try:
        if "transcription" not in state or not state.get("transcription"):
            raise ValueError("Missing or empty transcription in state")

        prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an enterprise-grade AI assistant specialized in extracting action items from meeting transcripts.

Your task is to identify and extract ONLY explicit tasks, assignments, or responsibilities mentioned in the conversation.

==============================
RULES (MANDATORY)
==============================

1. Extract ONLY clearly stated tasks or responsibilities.
2. Do NOT infer or assume tasks.
3. Do NOT create tasks from suggestions unless explicitly assigned.
4. Each task must include:
   - Task description
   - Owner (who is responsible)
   - Deadline (if mentioned)
5. If owner is not clearly mentioned, write: Not specified
6. If deadline is not mentioned, write: Not specified
7. Preserve speaker context when identifying the owner.
8. Do NOT merge multiple tasks into one.
9. Keep tasks concise and factual.
10. Output must be structured and consistent.

==============================
OUTPUT FORMAT (STRICT)
==============================

Action Items:
- Task: <description> | Owner: <speaker name> | Deadline: <date or "Not specified">

If no action items are found, output exactly:
Action Items:
Not specified

==============================
FINAL CHECK
==============================

- Ensure no hallucinated tasks are included
- Ensure each task is explicitly supported by the transcript
- Ensure correct speaker attribution
"""
    ),
    (
        "human",
        """Transcript:
{transcript}

Task:
Extract all action items strictly from the transcript.
"""
    )
])
        chain= prompt | model | StrOutputParser()
        extract_result = await chain.ainvoke({"transcript": state["transcription"]})
        if not extract_result or not extract_result.strip():
            raise ValueError("Empty action items result returned by LLM")
    except Exception as e:
        logger.error(f"Error in extract_action_items_node: {e}", exc_info=True)
        raise
