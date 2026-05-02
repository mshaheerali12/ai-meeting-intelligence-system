from langchain_core.messages import AIMessageChunk
from langsmith import traceable

@traceable(name="serialize AIMessageChunk for streaming")
def serialize_chunk(chunk):
    if isinstance(chunk, AIMessageChunk):
        return chunk.content
    return ""


@traceable(name="generate RAG stream")

async def generate_rag_stream(graph, state, config: dict = None):
    """
    Stream events from a LangGraph graph.
    - If state is provided: starts a fresh run (normal flow)
    - If state is None and config is provided: resumes a paused/checkpointed run (HITL approval)
    """
    stream_input = state if state is not None else None

    async for event in graph.astream_events(stream_input, config=config, version="v1"):
        if event["event"] == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            text = serialize_chunk(chunk)
            yield  text

        elif event["event"] == "on_chat_model_end":
            yield "data: [DONE]\n\n"
