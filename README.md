# AutoStream-AI-Agent
AI-powered conversational sales agent that classifies user intent, answers product questions via RAG, and captures qualified leads through a stateful multi-turn chat workflow. Built with LangGraph, FastAPI, and Next.js.

A production-grade conversational AI sales agent built for the ServiceHive / Inflx 
Machine Learning Intern Assignment. The agent simulates a real-world social-to-lead 
workflow for AutoStrea, a fictional SaaS platform offering automated video editing 
tools for content creators.

## What it does

The agent handles the full sales conversation lifecycle autonomously:

- Greets users naturally and answers any product or pricing question using a 
  local knowledge base (RAG), so responses are always grounded in facts, no hallucinations
- Detects when a user shows high purchase intent in real time and smoothly 
  transitions into lead qualification
- Collects the user's name, email, and creator platform one step at a time 
  through natural conversation, never all at once
- Fires a lead capture function the moment all three fields are collected, 
  simulating a CRM or webhook integration

## Tech Stack

**Backend**
- Python + FastAPI — REST API with session management
- LangGraph — stateful conversation graph with MemorySaver for multi-turn memory
- LangChain Anthropic — Claude Haiku as the reasoning LLM
- BM25 (rank-bm25) — lightweight RAG retrieval over a local JSON knowledge base
- Pydantic v2 — request/response validation

**Frontend**
- Next.js 15 + TypeScript — production-grade React framework
- Tailwind CSS — utility-first styling with off-white light theme
- Framer Motion — animated message bubbles, typing indicators, intent badge transitions
- Custom useChat hook — manages all conversation state client-side

## Key Features

- Intent classification — every user message is classified as greeting, inquiry, 
  or high_intent, with the UI adapting in real time
- RAG pipeline — BM25 retriever pulls relevant pricing, feature, and policy chunks 
  from the knowledge base and injects them into the LLM prompt
- Stateful lead collection — a LangGraph state machine tracks conversation stage 
  (chat - collecting_name - collecting_email -collecting_platform - complete) 
  across multiple HTTP requests using MemorySaver
- Tool safety — mock_lead_capture() only fires when all three fields are confirmed 
  in state, never prematurely
- Live intent badge — the UI shows Greeting / Exploring / High Intent in real time 
  as the conversation progresses
- Lead panel — a slide-in side panel tracks captured fields with a live progress bar
- Standalone demo — a single HTML file that runs the full agent in the browser 
  with no backend required

## Architecture

User - Next.js Frontend - FastAPI - LangGraph Agent - Claude Haiku - BM25 Retriever - autostream_kb.json -       mock_lead_capture()
