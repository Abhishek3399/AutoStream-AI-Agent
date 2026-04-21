# AutoStream AI Agent

> **Social-to-Lead Agentic Workflow** — A production-grade conversational AI sales agent that classifies intent, retrieves knowledge via RAG, and captures qualified leads through a stateful multi-turn conversation.

Built for **ServiceHive / Inflx** Machine Learning Intern Assignment.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  Next.js 15 + Tailwind CSS + Framer Motion                  │
│  • Animated chat interface  • Intent-reactive UI            │
│  • Lead capture side panel  • Typing indicators             │
└────────────────────────┬────────────────────────────────────┘
                         │  REST API  (POST /api/chat)
┌────────────────────────▼────────────────────────────────────┐
│                        BACKEND                               │
│  FastAPI + Uvicorn                                           │
│  • Clean REST endpoints   • CORS middleware                  │
│  • Session management     • Pydantic validation             │
└────────────┬────────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────────┐
│                     AGENT LAYER                              │
│  LangGraph StateGraph + MemorySaver                          │
│                                                              │
│  START → [retrieve] → [agent] ──conditional──▶ [capture]    │
│                                    │                         │
│                                    └─────────────▶ END       │
└────────────┬──────────────────────────────────────────────┬─┘
             │                                              │
┌────────────▼──────────────┐          ┌────────────────────▼──┐
│     KNOWLEDGE BASE        │          │    TOOL EXECUTION      │
│  BM25 Retriever           │          │  mock_lead_capture()   │
│  autostream_kb.json       │          │  (name, email, platform│
│  11 searchable chunks     │          │  → CRM / webhook)      │
└───────────────────────────┘          └───────────────────────┘
```

### Why LangGraph?

LangGraph was chosen over a plain chain or AutoGen for three reasons:

1. **Explicit state machine** — The lead-collection flow (`chat → collecting_name → collecting_email → collecting_platform → complete`) maps naturally to a directed graph with conditional edges, making the control flow readable and auditable.

2. **Built-in persistence** — `MemorySaver` stores the full `ConversationState` keyed by `session_id` (thread_id). Every HTTP request is stateless from FastAPI's perspective, yet the agent retains full conversation history across turns — no external Redis or database needed for this scale.

3. **Clean node separation** — Each concern (RAG retrieval, LLM generation, lead capture) is an isolated node. Adding new capabilities (e.g., a scheduling node, a CRM sync node) requires adding a node and an edge — not refactoring the entire chain.

### State Management

```python
class ConversationState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]  # append-only
    session_id: str
    intent: str          # greeting | inquiry | high_intent
    conversation_stage: str  # chat | collecting_name | collecting_email | collecting_platform | complete
    lead_info: LeadInfo  # { name, email, platform } built incrementally
    lead_captured: bool
    rag_context: str     # injected into prompt, cleared per turn
    rag_sources: List[str]
```

`operator.add` on `messages` means LangGraph automatically appends new messages to the list across graph invocations — producing a complete, ordered conversation history without manual stitching.

### WhatsApp Deployment via Webhooks

To deploy this agent on WhatsApp using the **WhatsApp Business Cloud API**:

1. **Register a webhook** at `POST /webhook/whatsapp` in FastAPI. WhatsApp sends a `hub.challenge` GET request for verification and POST requests for incoming messages.

2. **Parse the payload** — Extract `from` (phone number as session_id), `text.body` (the user message) from the JSON payload.

3. **Route through the agent** — Call `agent.chat(message=body, session_id=phone_number)`. The phone number acts as the thread_id for MemorySaver, preserving conversation state per user.

4. **Reply via the API** — POST to `https://graph.facebook.com/v17.0/{phone_number_id}/messages` with a bearer token and the agent's response text.

```python
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    payload = await request.json()
    entry = payload["entry"][0]["changes"][0]["value"]
    msg = entry["messages"][0]
    phone = msg["from"]         # session_id
    text = msg["text"]["body"]  # user message

    result = agent.chat(message=text, session_id=phone)
    ai_reply = extract_last_ai_message(result)

    await send_whatsapp_message(to=phone, text=ai_reply)
    return {"status": "ok"}
```

5. **Stateless scaling** — Replace `MemorySaver` with `AsyncRedisSaver` from `langgraph-checkpoint-redis` for multi-instance deployments. Each instance reads/writes the same Redis state by thread_id.

---

## Project Structure

```
autostream/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app + lifespan
│   │   ├── api/
│   │   │   └── chat.py             # /api/chat, /api/reset, /api/health
│   │   ├── agent/
│   │   │   ├── graph.py            # AutoStreamAgent (LangGraph)
│   │   │   ├── nodes.py            # retrieve_node, agent_node, capture_node
│   │   │   ├── state.py            # ConversationState TypedDict
│   │   │   └── tools.py            # mock_lead_capture()
│   │   ├── rag/
│   │   │   ├── loader.py           # KB → flat document list
│   │   │   └── retriever.py        # BM25Okapi retriever
│   │   └── models/
│   │       └── schemas.py          # Pydantic models
│   ├── knowledge_base/
│   │   └── autostream_kb.json      # Pricing, features, policies
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx            # Landing page + chat embed
│   │   │   ├── layout.tsx          # Font setup + metadata
│   │   │   └── globals.css         # Tailwind + custom styles
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx   # Main orchestrator
│   │   │   ├── ChatMessage.tsx     # Individual message bubble
│   │   │   ├── TypingIndicator.tsx # Animated dots
│   │   │   ├── IntentBadge.tsx     # Greeting / Exploring / High Intent
│   │   │   └── LeadPanel.tsx       # Lead collection progress panel
│   │   ├── hooks/
│   │   │   └── useChat.ts          # All chat state management
│   │   ├── lib/
│   │   │   ├── api.ts              # Backend API client
│   │   │   └── utils.ts            # cn() helper
│   │   └── types/
│   │       └── index.ts            # Shared TypeScript types
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── next.config.js
│
├── docs/
│   └── demo.html                   # Self-contained interactive demo
│
└── README.md
```

---

## Local Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- An Anthropic API key → https://console.anthropic.com

---

### Backend

```bash
cd backend

# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and set: ANTHROPIC_API_KEY=sk-ant-...

# 4. Start the server
uvicorn app.main:app --reload --port 8000
```

The API will be available at http://localhost:8000

- **Swagger UI**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/api/health

---

### Frontend

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Configure environment (optional — defaults to localhost:8000)
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# 3. Start dev server
npm run dev
```

Open http://localhost:3000

---

### Interactive Demo (no backend needed)

Open `docs/demo.html` directly in any browser.
The demo calls the Anthropic API directly from the browser (API key is injected by the Claude.ai environment).

---

## API Reference

### `POST /api/chat`

```json
// Request
{
  "message": "Tell me about the Pro plan",
  "session_id": "user-abc-123"
}

// Response
{
  "message": "The Pro plan is $79/month and includes unlimited videos...",
  "intent": "inquiry",
  "session_id": "user-abc-123",
  "conversation_stage": "chat",
  "lead_captured": false,
  "lead_data": null,
  "rag_sources": ["Pro Plan Pricing & Features"]
}
```

### `POST /api/reset`

```json
{ "session_id": "user-abc-123" }
```

### `GET /api/health`

```json
{ "status": "healthy", "version": "1.0.0", "model": "claude-haiku-4-5-20251001" }
```

---

## Conversation Flow

```
User: "Hi there"
Agent: Greets warmly                          [intent: greeting]

User: "How much does Pro cost?"
Agent: Retrieves pricing from KB, explains    [intent: inquiry, RAG: pricing_pro]

User: "That's great, I want to sign up for Pro for my YouTube channel"
Agent: Detects high intent, asks for name     [intent: high_intent, stage: collecting_name]

User: "My name is Priya"
Agent: Saves name, asks for email             [stage: collecting_email]

User: "priya@email.com"
Agent: Saves email, asks for platform         [stage: collecting_platform]

User: "YouTube"
Agent: Saves platform, calls mock_lead_capture(), sends confirmation  [stage: complete, lead_captured: true]
```

---

## Evaluation Checklist

| Criterion | Implementation |
|---|---|
| Intent detection | Claude classifies every turn into greeting / inquiry / high_intent via structured JSON prompt |
| RAG grounding | BM25 retriever pulls top-4 KB chunks per query, injected into system prompt |
| State management | LangGraph `MemorySaver` persists full `ConversationState` keyed by `session_id` across HTTP requests |
| Tool calling logic | `mock_lead_capture` only fires when `stage == "complete"` AND all three fields are present |
| Code clarity | Modular nodes, typed state, clean API layer, docstrings throughout |
| Real-world deployability | Docker-ready, env-var configuration, CORS, async FastAPI, WhatsApp webhook path documented |

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Claude Haiku (`claude-haiku-4-5-20251001`) via `langchain-anthropic` |
| Agent framework | LangGraph 0.2 (StateGraph + MemorySaver) |
| RAG | BM25Okapi (`rank-bm25`) over a local JSON knowledge base |
| Backend | FastAPI + Uvicorn |
| Frontend | Next.js 15 + Tailwind CSS + Framer Motion |
| Validation | Pydantic v2 |

---

*Built with ❤️ for the ServiceHive / Inflx ML Intern Assignment*
