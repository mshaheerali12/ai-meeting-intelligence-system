from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from nodes.rag_graph import build_graph
from summary.summary import app as summary_app
from pdf.pdf_api import app as pdf_app
from auth_service.routes import app as auth_app
from rag.rag_api import app as rag_app
from transcription.format_transc import app as format_app
from nodes.transcription_graph import transcript_graph
from nodes.summary_graph import summarizer_graph
from nodes.extrac import extract_action_items_graph
from nodes.changerg import  build_ch_graph
from extraction.ex_apiq import app as ext_app
from langgraph.checkpoint.redis import AsyncRedisSaver
from transcription.meeting_generation import app as meet
from pipeline.pipe import app as pipe_app
from nodes.emailgraph import email_graph_building
from email_fol.email_apis import app as email_app
from pipeline.pipeline2 import app as v_app
from pipeline.pipeline3 import app as r_app
import os
import logging
import logging.config
from dotenv import load_dotenv

load_dotenv()


REDIS_CHECKPOINTER_URL = os.getenv("REDIS_CHECKPOINTER_URL")


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    

        cm           = AsyncRedisSaver.from_conn_string(REDIS_CHECKPOINTER_URL)
        checkpointer = await cm.__aenter__()
        app.state.ch_graph     = await build_ch_graph()
        app.state.em_graph     = await email_graph_building()
        app.state.rag_graph    = await build_graph(checkpointer)
        app.state.transc_graph = await transcript_graph()
        app.state.ext_graph    = await extract_action_items_graph()
        app.state.sum_graph    = await summarizer_graph()
        

        yield

   

# ── App ───────────────────────────────────────────────────────────────────────
api_app = FastAPI(
    title="Meeting Transcription & Summarization",
    version="1.0.0",
    lifespan=lifespan
)


# ── Global exception handler ──────────────────────────────────────────────────
@api_app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
   
    return JSONResponse(status_code=500, content={"error": "An unexpected error occurred."})

# ── Routers ───────────────────────────────────────────────────────────────────
api_app.include_router(auth_app,              prefix="/auth",             tags=["auth"])
api_app.include_router(meet,                  prefix="/meeting_gen",      tags=["meeting"])
api_app.include_router(pipe_app,              prefix="/pipeline",         tags=["pipeline"])
api_app.include_router(v_app,                 prefix="/pipeline",         tags=["pipeline"])
api_app.include_router(r_app,                 prefix="/pipeline",         tags=["pipeline"])
api_app.include_router(format_app,            prefix="/transcription",    tags=["transcription"])
api_app.include_router(ext_app,               prefix="/extraction",       tags=["extraction"])
api_app.include_router(summary_app,           prefix="/summary",          tags=["summary"])
api_app.include_router(pdf_app,               prefix="/pdf",              tags=["pdf"])
api_app.include_router(email_app,             prefix="/meeting_gen",      tags=["email"])
api_app.include_router(rag_app,               prefix="/rag",              tags=["rag"])
