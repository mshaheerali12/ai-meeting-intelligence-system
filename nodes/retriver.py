from nodes.llm import model_embed
from langchain_redis import RedisVectorStore
from nodes.state import meemory
async def meeting_retriver(state:meemory,k:int=3):
    redis_url="redis://default:cntrZVax6Mh3kWbAfvhD5SGLkrOBBhpi@redis-12687.c241.us-east-1-4.ec2.cloud.redislabs.com:12687"
    id=state['meeting_id']
    embed=model_embed()
    index_name=f"meeting{id}"
    vector_store=RedisVectorStore(
        redis_url=redis_url,
        index_name=index_name,
        embeddings=embed,
        distance_metric="COSINE"
    )
    retriver=vector_store.as_retriever( search_kwargs={"k": k})
    docs=await retriver.ainvoke(state["question"])
    return {"docs":docs}
