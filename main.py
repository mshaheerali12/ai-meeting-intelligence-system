from fastapi import FastAPI
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from nodes.graph import graph_building
from nodes.rag_graph import build_graph
from transcription.api import app as raw_transcription_app
from summary.summary import app as summary_app
from pdf.pdf_api import app as pdf_app
from auth_service.routes import app as auth_app
from vec_store.redis_api import app as retriever_app
from rag.rag_api import app as rag_app
from transcription.format_transc import app as format_app
from nodes.transcription_graph import transcript_graph
from nodes.summary_graph import summarizer_graph
from langgraph.checkpoint.redis import RedisSaver
@asynccontextmanager
async def lifespan(app:FastAPI):
    app_graph = None
    rag_graph=None
    sum_graph=None
    transc_graph=None
    app.state.app_graph = await graph_building()
    app.state.rag_graph=await build_graph()
    app.state.transc_graph=await transcript_graph()
    app.state.sum_graph=await summarizer_graph()
    yield
api_app = FastAPI(title="Meeting transcription & Summarization ", lifespan=lifespan)

api_app.include_router(auth_app,prefix="/auth")
api_app.include_router(raw_transcription_app,prefix="/raw_transcription")
api_app.include_router(format_app,prefix="/transcription")
api_app.include_router(summary_app,prefix="/summary")
api_app.include_router(pdf_app,prefix="/pdf")
api_app.include_router(retriever_app,prefix="/retriever")
api_app.include_router(rag_app,prefix="/rag")
