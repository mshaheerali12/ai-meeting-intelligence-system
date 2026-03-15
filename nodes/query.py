from langchain_core.prompts import ChatPromptTemplate
from nodes.state import meemory
from nodes.llm import llm
from pydantic import BaseModel
model=llm()
class query_ref(BaseModel):
    query:str
async def web_query_ref(state:meemory):
    prompt=ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
             Rewrite the user question into a websearch query composed o keywords.\n
             Rules:\n
             -keep it short (6-14 words)
             -if the question implies recency(e.g recent/latest/lastweek/lastmonth) add a constraint like(last 30 days)\n
             Donot answer the question\n
             -Return JSON with a single(e.g :"query")

"""
            ),
            (
                "human",
                """query:{query}"""
            )
        ]
    )
    chain=prompt | model.with_structured_output(query_ref)
    res=await chain.ainvoke({"query":state["question"]})
    return{
        "web_query":res.query
    }