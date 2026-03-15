from pydantic import BaseModel
from typing import List
from nodes.state import meemory
from nodes.llm import llm
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import asyncio
from langchain_core.documents import Document
class doc_eval(BaseModel):
    score:float
    index:int
    reason:str

class BatchRerank(BaseModel):
    results: List[doc_eval]
model=llm()
async def doc_eval_node(state:meemory):
    if not state.get("docs"):
        return {
            "good_docs": [],
            "verdict": "incorrect"
        }
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a strict retrieval evaluator for RAG.
You will be given multiple retrieved chunks and a question.
Score EACH chunk from 0.0 to 1.0.
1.0 = fully sufficient
0.0 = irrelevant
Be conservative with high scores.
Also return a short reason.

Return JSON literally:
{{
"results": [
{{"index": 0, "score": 0.8, "reason": "..."}},
{{"index": 1, "score": 0.2, "reason": "..."}}
]
}}
"""
            ),
            (
                "human",
                """Question: {question}\n\nChunks: {chunk}"""
            )
        ]
    )
    q=state["question"]
    chuncks="\n\n".join([f"{i}.{doc.page_content}"for i , doc in enumerate(state["docs"])])
    chain=prompt | model.with_structured_output(BatchRerank)
    output= await chain.ainvoke({ "question":q,
            "chunk":chuncks})

    l_Th=0.4
    h_Th=0.8
    if not output.results:
        return {
            "good_docs": [],
            "verdict": "incorrect"
        }

    scores=[r.score for r in output.results]
    good_docs = [
        state["docs"][r.index]
        for r in output.results
        if r.score > 0.5 and r.index < len(state["docs"])
    ]

    max_score = max(scores)

    if max_score >= 0.8:
        verdict = "correct"

    elif max_score <= 0.4:
        verdict = "incorrect"

    else:
        verdict = "ambiguous"

    return {
        "good_docs": good_docs,
        "verdict": verdict
    }
    

    