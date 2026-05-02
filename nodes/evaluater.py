from pydantic import BaseModel
from typing import List
from nodes.state import meemory
from nodes.llm import llm
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable

class doc_eval(BaseModel):
    score: float
    index: int
    reason: str

class BatchRerank(BaseModel):
    results: List[doc_eval]

model = llm()
@traceable(name="evaluate documents")
async def doc_eval_node(state: meemory):
    if not state.get("docs"):
        return {"good_docs": [], "verdict": "incorrect"}

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are a retrieval evaluator for a meeting Q&A system.
You will be given chunks from a meeting transcript and a question asked about that meeting.
Score EACH chunk from 0.0 to 1.0.

Scoring guide:
- 1.0 = chunk directly answers the question
- 0.7 = chunk contains clearly relevant content about the topic
- 0.5 = chunk is related to the topic but only partially useful
- 0.2 = chunk is about a different topic
- 0.0 = completely irrelevant

IMPORTANT: These are informal meeting transcripts — spoken language, casual phrasing.
Be generous when the topic clearly matches even if the wording is imprecise.

Return JSON only:
{{
  "results": [
    {{"index": 0, "score": 0.8, "reason": "..."}},
    {{"index": 1, "score": 0.3, "reason": "..."}}
  ]
}}
"""
        ),
        (
            "human",
            "Question: {question}\n\nTranscript chunks:\n{chunk}"
        )
    ])

    q = state["question"]
    chunks_text = "\n\n".join([
        f"{i}. {doc.page_content}"
        for i, doc in enumerate(state["docs"])
    ])

    chain = prompt | model.with_structured_output(BatchRerank)
    output = await chain.ainvoke({"question": q, "chunk": chunks_text})

    if not output or not output.results:
        return {"good_docs": [], "verdict": "incorrect"}

    scores = [r.score for r in output.results]
    max_score = max(scores)

    # Collect docs that score above 0.4 (lowered from 0.5)
    good_docs = [
        state["docs"][r.index]
        for r in output.results
        if r.score > 0.4 and r.index < len(state["docs"])
    ]

    # Thresholds — lowered for casual meeting transcripts
    # correct:   max >= 0.6  (was 0.8 — too strict for informal speech)
    # ambiguous: max between 0.35 and 0.6
    # incorrect: max < 0.35
    if max_score >= 0.6:
        verdict = "correct"
    elif max_score >= 0.35:
        verdict = "ambiguous"
    else:
        verdict = "incorrect"

    return {
        "good_docs": good_docs,
        "verdict": verdict
    }
