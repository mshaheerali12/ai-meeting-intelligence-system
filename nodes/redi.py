from langchain_redis import RedisVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from nodes.llm import model_embed
from nodes.state import meemory

redis_url = "redis://default:cntrZVax6Mh3kWbAfvhD5SGLkrOBBhpi@redis-12687.c241.us-east-1-4.ec2.cloud.redislabs.com:12687"


async def get_retriever(transcription,id, k: int = 3):

    meeting_id = id
    transcription_data = transcription

    embed = model_embed()

    index_name = f"meeting{meeting_id}"

    vector_store = RedisVectorStore(
        redis_url=redis_url,
        index_name=index_name,
        embeddings=embed,
        distance_metric="COSINE"
    )

    # Try retrieving to see if index exists
    try:
        retriever = vector_store.as_retriever(search_kwargs={"k": k})
        docs = await retriever.ainvoke("test")

        if len(docs) == 0:
            raise Exception("Index empty")

    except Exception:

        doc = Document(
            page_content=transcription_data,
            metadata={
                "source": "meeting_audio",
                "meeting_id": meeting_id
            }
        )

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=120
        )

        chunks = splitter.split_documents([doc])

        await vector_store.aadd_documents(chunks)

    return {"vector_store": vector_store}