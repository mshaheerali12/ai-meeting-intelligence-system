from nodes.llm import llm
from nodes.state import meemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser,JsonOutputParser
import logging
model=llm()
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",filename="transciption.log",filemode="w")
logger = logging.getLogger(__name__)

async def transcription_node(state:meemory):
    
    """
    Docstring for transcription_node
    
    :param state: this is node where transcription of audio file is generated 
    """
    try:
        logger.info("Starting transcription node")
        if "raw_transcription" not in state:
            logger.error("No raw transcription found in state")
            return {"transcription": "Error: No raw transcription found."} 
        prompt=ChatPromptTemplate.from_messages([
        (
            "system",
            """
            You are a professional meeting transcription formatter.
            Your task is to clean and structure raw meeting transcriptions.
            Rules:
            - Remove filler words (um, ah, like)
            - Fix grammar and punctuation
            - Break into clear sentences
            - Preserve original meaning
            - Do NOT add or remove content
            -Clean the transcription and apply the user's style instruction.
            -Preserve meaning but adapt tone and wording.
            """
        ),
        (
            "human",
            """
Format the following raw transcription:

{response}

User instruction:
{instruction}

Apply the instruction while preserving meaning.
"""

        )
    ])
        chain=prompt | model | StrOutputParser()
        synthesis=await chain.ainvoke({"response":state["raw_transcription"],"instruction":state.get("instruction","")})
        if not synthesis:
            raise ValueError("empty transcription result")
        logger.info("Transcription node completed successfully")
    
    
        return {"transcription":synthesis}
    except Exception as e:
        logger.error(f"Error in transcription node: {e}",exc_info=True)
        raise       

    

    
async def summarizer_node(state:meemory):
    """
    Docstring for summarizer_node
    
    :param state: Description
    :type state: variables
    this is node for doing summarization of transcription that comes from previous node

    """
    try:
        if "transcription" not in state:
            raise ValueError ("missing transcription in state")
        prompt=ChatPromptTemplate.from_messages([
        (
            "system",
            """
            You are an enterprise-grade AI Meeting Notes Assistant.

        Your task is to generate a structured, professional, and concise meeting summary 
        from a raw meeting transcription.

        You MUST strictly follow all rules below.

        ==============================
        RULES (MANDATORY)
        ==============================

        1. Do NOT add any information that is not explicitly present in the transcription.
        2 . Do NOT assume missing details.
        3. Do NOT hallucinate names, dates, tasks, or decisions.
        4. If information is unclear or missing, explicitly write: "Not specified".
        5. Be concise but complete.
        6. Maintain formal and professional business language.
        7. Do NOT include explanations about your reasoning.
        8. Do NOT include markdown symbols, bullet emojis, or decorative characters.
        9. Output must be plain structured text only.
        10. Follow the exact structure provided below.

        ==============================
        OUTPUT STRUCTURE (STRICT FORMAT)
        ==============================

        Meeting Overview:
        Write a clear 3–5 sentence summary describing the overall discussion.

        Key Topics:
        - Topic 1
        - Topic 2

        Decisions Made:
        - Decision 1
        - Decision 2
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

        """
        ),
        (
            "human",
            """
           Now generate the summary based strictly on the following transcription:

        {transcription}

        """
        )


    ])
        chain=prompt | model | StrOutputParser()
        summary=await chain.ainvoke({"transcription":state["transcription"]})
    
        if not summary:
            raise ValueError("empty summary result")
        logger.info("Summarizer node completed successfully")
        return {
        "summary":summary
        }
    except Exception as e:
        logger.error(f"Error in summarizer node: {e}",exc_info=True)
        raise
