from langchain_core.prompts import ChatPromptTemplate
from nodes.state import meemory
from nodes.llm import llm
from pydantic import BaseModel
from langsmith import traceable
import logging

logger = logging.getLogger(__name__)
model = llm()


class query_ref(BaseModel):
    query: str


@traceable(name="generate web search query")
async def web_query_ref(state: meemory):
    try:
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """Rewrite the user question into a web search query composed of keywords.
Rules:
- Keep it short (6-14 words)
- If the question implies recency (e.g. recent/latest/last week) add a time constraint like (last 30 days)
- Do NOT answer the question
- Return JSON with a single key "query"
"""
            ),
            (
                "human",
                "query: {query}"
            )
        ])

        chain = prompt | model.with_structured_output(query_ref)
        res = await chain.ainvoke({"query": state["question"]})
        return {"web_query": res.query}

    except Exception as e:
        logger.error(f"[web_query_ref ERROR] error={e}", exc_info=True)
        # Fall back to original question as the web query
        return {"web_query": state.get("question", "")}
