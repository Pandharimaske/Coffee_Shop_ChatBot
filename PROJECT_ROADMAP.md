# ☕ Merry's Way — Master Roadmap

Single source of truth for all planned upgrades, architectural decisions, and next-level features.  
**Stack**: React 18 + Vite + Tailwind · FastAPI · LangGraph (8-agent pipeline) · Supabase (PostgreSQL + Auth) · Pinecone · `arcee-ai/trinity-large-preview` via OpenRouter

---

## 🗂️ Overview

| Phase | Feature | Effort | Status |
|---|---|---|---|
| 1 | LangSmith Observability + Metrics | ~1 hour | ⬜ Todo |
| 2 | SSE Token Streaming | ~1 day | ⬜ Todo |
| 3 | Admin Panel | ~2 days | ⬜ Todo |
| 4 | Human-in-the-Loop (HITL) | ~2 days | ⬜ Todo |
| 5 | Voice Ordering | ~1 week | ⬜ Todo |
| 6 | AWS Production Deployment | ~1 week | ⬜ Todo |
| — | Architecture Upgrades | ongoing | ⬜ Todo |
| — | Next-Level Features | future | 💡 Backlog |

---

## Phase 1 — LangSmith Observability *(Immediate, ~1 hour)*

Zero code changes. Environment variables only.

- Flip `LANGSMITH_TRACING_V2=true` in `.env.example`; add `LANGCHAIN_API_KEY` and `LANGCHAIN_PROJECT`
- Every LangGraph node run is now auto-traced in the LangSmith dashboard
- Add a **RAGAS evaluation script** targeting the existing Pinecone retriever — establishes RAG precision@3 baseline before touching anything else
- **Instrument `prometheus_client` metrics** as the project's observability backbone:
  - P95 end-to-end latency
  - RAG precision@3
  - Guard agent accuracy
  - Router accuracy
  - Order state accuracy

> These baselines are critical — every subsequent phase should move at least one of these metrics.

---

## Phase 2 — SSE Token Streaming *(Biggest perceived performance win)*

**Problem**: Users wait 3–5 seconds for the full LangGraph pipeline to finish before seeing any response.  
**Goal**: First token visible in < 500ms.

- Upgrade FastAPI endpoint to `StreamingResponse` with `text/event-stream` content type
- Use LangGraph's `.astream_events()` to tap the final agent's token stream as it generates
- Update React frontend to consume the SSE stream and render tokens incrementally (typewriter effect)
- Add **Optimistic UI** for cart mutations — when user says "Add 2 cappuccinos", update cart display instantly without waiting for LLM confirmation; reconcile on completion

---

## Phase 3 — Admin Panel *(This weekend)*

Two distinct sub-features behind a protected `/admin` route:

**A. Product CRUD**
- Add / edit / delete menu items with form validation
- On every write: sync Supabase PostgreSQL + re-upsert or delete Pinecone vectors atomically
- Prevents vector store drift from manual DB edits

**B. Analytics Chatbot (Text-to-SQL)**
- Natural language → SQL against Supabase via RPC, restricted to `SELECT` queries only
- Add `_suggest_chart()` frontend hint helper so the UI can auto-render bar/line charts from query results
- Example queries: *"What were the top 5 orders this week?"*, *"How many cold drinks were ordered this month?"*

---

## Phase 4 — Human-in-the-Loop (HITL) *(Next weekend)*

**Problem**: `MemorySaver` dies on server restart; no staff visibility into ambiguous or flagged orders.

- Replace `MemorySaver` with **`PostgresSaver`** backed by Supabase — graph state survives process restarts
- Use LangGraph native **`interrupt()`** to pause the graph when Order or Router agent has low confidence
- Two resolution paths:
  - **Action Buttons in chat**: Inject interactive React buttons (e.g., *"🧊 Iced"* / *"🔥 Hot"*) directly into the chat window — no typing required, zero friction for the user
  - **Staff approval flow**: Send a Slack webhook notification to staff; approval endpoint calls `aupdate_state` to resume the paused graph

---

## Phase 5 — Voice Ordering *(Week 3)*

**Option A — Twilio** *(simpler, production-ready)*
- Twilio webhooks receive audio; `CallSid` is used as the persistent LangGraph session identifier
- Existing LangGraph graph reuses without modification
- Edge case to handle: Guard agent receiving very short transcriptions ("um", "hello", silence) that aren't real orders

**Option B — WebRTC Realtime** *(higher wow-factor, post-Twilio)*
- Browser mic → WebRTC → OpenAI Realtime API (or OpenRouter equivalent)
- True voice-to-voice with sub-second response, natural interruptions, and drive-thru feel
- Validate Twilio path first; upgrade to this after

---

## Phase 6 — AWS Production Deployment *(Last)*

All infrastructure in `ap-south-1` (Mumbai) for lowest latency from Pune.

| Component | Service |
|---|---|
| FastAPI backend | ECS Fargate |
| React frontend | S3 + CloudFront |
| Docker images | ECR |
| SSL termination | ALB |
| Secrets | AWS Secrets Manager (replaces `.env`) |
| CI/CD | GitHub Actions → ECR → ECS rolling deploy |

---

## Architecture Upgrades *(Run alongside phases, not after)*

### A. Tiered LLM Routing
Using `arcee-ai/trinity-large-preview` for Guard + Router is overkill.
- Route **Guard** and **Router** agents to a fast small model (`Qwen-2.5-1.5B` or `Llama-3-8B-Instruct`)
- Reserve heavy model for Details / Order / Recommendation / General agents
- Expected: ~60% reduction in average pipeline latency

### B. Kuzu Graph DB — Hybrid Vector + Graph Architecture
Pinecone metadata filtering is a poor fit for structured relational queries (allergens, pairings, categories).
- Add **Kuzu** (embedded Python-native graph DB, Cypher query language) alongside Pinecone
- **Kuzu handles**: product relationships, menu pairings, allergen traversal, category filtering
- **Pinecone handles**: fuzzy natural-language description search only
- `apriori_recommendations.json` maps directly to Kuzu graph edges with confidence scores — minimal migration work
- Migration path: build graph from Supabase products + Apriori data → integrate into Details + Recommendation agents → progressively strip metadata filters from Pinecone

### C. Semantic Caching (Redis + GPTCache)
Repetitive queries like *"What's the menu?"* or *"What are store hours?"* hit the LLM unnecessarily.
- Cache LLM responses keyed by embedding similarity (≥ 95% cosine = cache hit)
- Redis as backend; GPTCache as the abstraction layer
- Track cache hit rate alongside RAGAS metrics from Phase 1

### D. Graceful Degradation (Fallback Mode)
- If OpenRouter or Pinecone goes down, auto-switch to a regex-based or local small-LLM fallback
- Fallback mode: strict menu-only ordering until external services recover
- User-facing banner: *"Merry's is in limited mode right now — standard orders only"*

### E. Persistent Memory Graph (Mem0)
Current memory is static likes/dislikes per session.
- Upgrade to **Mem0**-style dynamic memory graph
- Stores temporal context: *"Last Tuesday ordered black coffee, found it too bitter"*
- Recommendation agent uses memory graph to personalize without re-asking preferences

---

## 💡 Next-Level Features *(Backlog — build after Phase 6)*

### Barista Vision (Multimodal)
User uploads a photo of any coffee → Vision model analyzes it → Pinecone maps it to the closest item on Merry's menu.  
*"Can you make something that looks like this latte I had in Milan?"*

### Proactive Weather-Aware Suggestions
App reads local weather + time of day on open → bot proactively suggests items before the user types.  
*"It's 8°C and raining in Pune ☔ — want your usual hazelnut latte to start the day?"*

### Kitchen Display System (KDS)
Secondary staff dashboard. Order Agent groups hot/cold items into separate kitchen queues, estimates prep time, and pushes ETA back to the customer in chat.

### Secret Menu Loyalty Gamification
Hidden menu items unlocked only after 5+ orders or by solving a daily riddle.  
*"I see you're a regular... want to hear about our off-menu Midnight Espresso?"*

---

## ✅ Execution Principles

1. **Measure before optimizing** — LangSmith + Prometheus baselines go in first (Phase 1), always
2. **Perceived speed > actual speed** — SSE streaming (Phase 2) is higher priority than backend caching
3. **Every phase moves a metric** — ship nothing that doesn't show up in the dashboard
4. **Graph DB is architecture, not a feature** — evaluate Kuzu alongside Phase 3/4, not as an afterthought post-Phase 6
5. **Deploy last** — AWS (Phase 6) only after core features are stable and tested locally
