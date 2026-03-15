from langchain_tavily import TavilySearch
from langchain_core.documents import Document
from nodes.state import meemory
import os
from dotenv import load_dotenv

load_dotenv()

tavily = TavilySearch(tavily_api_key="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",max_results=5)

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