from nodes.state import meemory
from nodes.llm import llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
model=llm()
async def generate(state:meemory):
    prompt=ChatPromptTemplate.from_messages(
        
        [
            (
                "system",
                """You are helpful assistant\n
                answer only using the provided reined bullets\n
                """
            ),
            (
                "human",
                """Question:{question}\n\n
                refined_context:
                {refined_context}"""
            )
        ]
    )
    chain=prompt | model | StrOutputParser()
    final=await chain.ainvoke({
        "question": state["question"],
        "refined_context": state.get("refined_context", "")
    })
        # Wrap the string in a dict as LangGraph expects
    return {"answer": final}