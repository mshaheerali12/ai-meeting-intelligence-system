from langchain_core.messages import AIMessageChunk
def serialize_chunk(chunk):
    if isinstance(chunk, AIMessageChunk):
        return chunk.content
    return ""


async def generate_rag_stream(graph, state):

    async for event in graph.astream_events(state, version="v1"):

        if event["event"] == "on_chat_model_stream":

            chunk = event["data"]["chunk"]
            text = serialize_chunk(chunk)

            # SSE format
            yield f"data: {text}\n\n"

        elif event["event"] == "on_chat_model_end":
            yield "data: [DONE]\n\n"
