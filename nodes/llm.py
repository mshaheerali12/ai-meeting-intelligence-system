from langchain_openai import ChatOpenAI,OpenAIEmbeddings
import os
from dotenv import load_dotenv
load_dotenv()
api_key=os.getenv("OPENAI_API_KEY")
def llm():
    model=ChatOpenAI(model="gpt-4o", api_key=api_key,temperature=0,streaming=True)
    return model
def model_embed():
    embeding= OpenAIEmbeddings(model="text-embedding-3-large")
    return embeding