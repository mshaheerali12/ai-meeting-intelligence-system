from nodes.state import meemory
from nodes.decomposer import decomposer
from nodes.llm import llm
from langchain_core.prompts import ChatPromptTemplate
import asyncio
from pydantic import BaseModel
model=llm()
class keepordrop(BaseModel):
    keep:bool
async def filteration(state:meemory):
    prompt=ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
             Your are a strict relvance filter\n
             return keep=true only if the sentence directly helps answer the question.\n
             use only the sentence.output JSON only

""" ),
(
    "human",
    """Question:{question}\n\nsentence:\n{sentence}"""
)
        ]
    )
    chain=prompt | model.with_structured_output(keepordrop)
    q=state["question"]
    if state.get("verdict")=="correct":
        docs_to_use=state["good_docs"]
    elif state.get("verdict")=="incorrect":
        docs_to_use=state["web_docs"]
    else:
        docs_to_use=state["good_docs"]+ state["web_docs"]
    context="\n\n".join(d.page_content for d in docs_to_use).strip()
    from langchain_core.documents import Document
    strips = [Document(page_content=s) for s in decomposer(context)]

    tasks = [
        chain.ainvoke({"question": q, "sentence": s.page_content})
        for s in strips
    ]

    out_r = await asyncio.gather(*tasks, return_exceptions=True)

    kept = []

    for s, result in zip(strips, out_r):

        if isinstance(result, Exception):
            continue

        if result.keep:
            kept.append(s)

    refined_context = "\n".join(d.page_content for d in kept)

    return {
        "strips": strips,
        "kept_strips": kept,
        "refined_context": refined_context
    }

