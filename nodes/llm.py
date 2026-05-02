from langchain_openai import ChatOpenAI,OpenAIEmbeddings
import os
from dotenv import load_dotenv
from langsmith import traceable
load_dotenv()
api_key=os.getenv("OPENAI_API_KEY")
@traceable(name="initialize LLM")
def llm():
    model=ChatOpenAI(model="gpt-4o", api_key=api_key,temperature=0,streaming=True)
    return model
@traceable(name="initialize embeddings")
def model_embed():
    embeding= OpenAIEmbeddings(model="text-embedding-3-large")
    return embeding