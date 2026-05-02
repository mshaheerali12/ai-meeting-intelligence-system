from nodes.state import meemory
from nodes.decomposer import decomposer
from nodes.llm import llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from pydantic import BaseModel
from typing import List
from langsmith import traceable
import logging

logger = logging.getLogger(__name__)
model = llm()


class FilterResult(BaseModel):
    kept_indices: List[int]


@traceable(name="filter documents")
async def filteration(state: meemory):
    q = state["question"]

    if state.get("verdict") == "correct":
        docs_to_use = state["good_docs"]
    elif state.get("verdict") == "incorrect":
        docs_to_use = state["web_docs"]
    else:
        # ambiguous — merge both, filter will keep only relevant ones
        docs_to_use = state["good_docs"] + state.get("web_docs", [])

    context = "\n\n".join(d.page_content for d in docs_to_use).strip()
    strips = [Document(page_content=s) for s in decomposer(context)]

    if not strips:
        logger.warning(f"[filter] No strips after decomposition for question: {q[:80]}")
        return {"strips": [], "kept_strips": [], "refined_context": ""}

    numbered = "\n".join(
        f"{i}. {s.page_content}" for i, s in enumerate(strips)
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a strict relevance filter for a meeting Q&A system.
You will be given a question and a numbered list of sentences.
Return ONLY the indices of sentences that directly help answer the question.
Output JSON only: {{"kept_indices": [0, 2, 5]}}
If no sentences are relevant, return {{"kept_indices": []}}"""
        ),
        (
            "human",
            "Question: {question}\n\nSentences:\n{sentences}"
        )
    ])

    chain = prompt | model.with_structured_output(FilterResult)
    result = await chain.ainvoke({"question": q, "sentences": numbered})

    # Fix Issue 7 — deduplicate indices so GPT-4o duplicates don't cause
    # the same sentence appearing twice in refined_context
    seen = set()
    unique_indices = []
    for i in result.kept_indices:
        if i not in seen and i < len(strips):
            seen.add(i)
            unique_indices.append(i)

    kept = [strips[i] for i in unique_indices]
    refined_context = "\n".join(d.page_content for d in kept)

    logger.info(f"[filter] kept {len(kept)}/{len(strips)} sentences for question: {q[:80]}")

    return {
        "strips": strips,
        "kept_strips": kept,
        "refined_context": refined_context
    }
