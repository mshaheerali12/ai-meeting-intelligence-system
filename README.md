AI Meeting Intelligence System

An AI-powered backend system that records meeting audio, converts it to text, generates intelligent summaries, performs semantic search over past meetings, and produces downloadable meeting reports.

Built using FastAPI, LangGraph, OpenAI, Deepgram, Redis, and Vector Databases.

Project Overview

This system automates the entire meeting intelligence pipeline:

Record or upload meeting audio

Convert speech to text using AI

Generate structured summaries

Store embeddings for semantic search

Retrieve relevant past meetings using RAG

Generate a professional PDF report

The system is designed with modular AI nodes using LangGraph to simulate production-grade AI workflows.

Features
AI Transcription

Uses Deepgram Speech-to-Text API to convert meeting audio into text.

AI Summarization

Uses OpenAI LLMs to generate concise meeting summaries.

Retrieval-Augmented Generation (RAG)

Stores meeting embeddings in a vector database for semantic search across previous meetings.

Meeting Memory

Uses Redis to manage meeting sessions and temporary memory.

PDF Report Generation

Automatically generates a structured meeting summary PDF.

Streaming Responses

Supports streaming outputs for real-time AI responses.

Modular AI Pipeline

Uses LangGraph nodes for building a scalable AI workflow.

Tech Stack

Backend Framework

FastAPI

AI & LLM Tools

OpenAI API

LangGraph

LangChain

Speech Recognition

Deepgram API

Databases

Redis (session memory)

Vector Store (embeddings)

Document Generation

Python PDF generator

Dev Tools

Python

Git

REST APIs

Project Structure
ai-meeting-intelligence-system
│
├── auth_service/        # Authentication logic
├── rag/                 # Retrieval Augmented Generation
├── vec_store/           # Vector database logic
├── streaming/           # Streaming AI responses
├── pdf/                 # Meeting PDF report generation
│
├── nodes/               # LangGraph AI nodes
│   ├── transcription_node.py
│   ├── summarizer_node.py
│
├── main.py              # FastAPI application
├── graph.py             # LangGraph workflow
├── state.py             # Meeting memory state
│
├── requirements.txt
├── .gitignore
└── README.md
System Architecture
User
  │
  ▼
FastAPI Backend
  │
  ▼
LangGraph Workflow
  │
  ├── Transcription Node (Deepgram)
  │
  ├── Summarization Node (OpenAI)
  │
  ├── RAG Retrieval (Vector Store)
  │
  └── PDF Generator
  │
  ▼
Redis Memory + Vector Database
