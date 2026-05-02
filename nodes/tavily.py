from langchain_tavily import TavilySearch
from langchain_core.documents import Document
from nodes.state import meemory
import os
from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()

tavily = TavilySearch(
    tavily_api_key=os.getenv("TAVILY_API_KEY"),
    max_results=5
)

@traceable(name="perform web search using Tavily")
async def web_Search(state: meemory):
    q = state.get("web_query", state["question"])
    response = await tavily.ainvoke({"query": q})
    results = response.get("results", [])

    web_docs = []
    for r in results:
        title = r.get("title", "")
        url = r.get("url", "")
        content = r.get("content", "")
        text = f"title: {title}\nurl: {url}\ncontent: {content}"
        web_docs.append(Document(page_content=text))

    return {"web_docs": web_docs}
