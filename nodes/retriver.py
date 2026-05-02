from nodes.llm import model_embed
from langchain_redis import RedisVectorStore
from nodes.state import meemory
embed=model_embed()
redis_url="redis://default:zZ3rxZU1cv6NyrLBVvSITHpQnmz1V0rj@redis-11730.crce219.us-east-1-4.ec2.cloud.redislabs.com:11730"

async def meeting_retriver(state:meemory,k:int=3):
 
    id=state['meeting_id']
    
    index_name=f"meeting{id}"
    vector_store=RedisVectorStore(
        redis_url=redis_url,
        index_name=index_name,
        embeddings=embed,
        distance_metric="COSINE"
    )
    retriver=vector_store.as_retriever( search_kwargs={"k": k})
    docs=await retriver.ainvoke(state["question"])
    

    if not docs:
            return {"docs": [], "verdict": "incorrect"}

    return {"docs": docs}

  