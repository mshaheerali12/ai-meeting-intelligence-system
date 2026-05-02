import hashlib
import json
import logging
import os

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langsmith import traceable

from langchain_redis import RedisVectorStore
from auth_service.db import get_hash_trans, hash_trans
from nodes.llm import model_embed

load_dotenv()


# Module-level singletons

embed = model_embed()
redis_url="redis://default:zZ3rxZU1cv6NyrLBVvSITHpQnmz1V0rj@redis-11730.crce219.us-east-1-4.ec2.cloud.redislabs.com:11730"

async def get_retriever(transcription,id):

    meeting_id = id
    data = transcription

    

    index_name = f"meeting{meeting_id}"

    vector_store = RedisVectorStore(
        redis_url=redis_url,
        index_name=index_name,
        embeddings=embed,
        distance_metric="COSINE"
    )

    # Try retrieving to see if index exists
    transcription=await hash_trans(meeting_id,data)
    existance=await get_hash_trans(meeting_id)
    if existance == transcription:
        return {"message":"already embed"}
    

    

    doc = Document(
            page_content=data,
            metadata={
                "source": "meeting_audio",
                "meeting_id": meeting_id
            }
        )

    splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=120
        )

    chunks = splitter.split_documents([doc])

    await vector_store.aadd_documents(chunks)

    return {"vector_store": vector_store}
    

