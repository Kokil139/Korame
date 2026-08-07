# Korame V1 - Complete Build Summary

**Date**: July 30, 2026 (updated)
**Status**: ✅ **PHASE 1 COMPLETE** — RTE → Developer → Testing pipeline, real GitHub PR creation, live workflow visualization UI

> This document describes what is **actually implemented** in this repository
> ("Phase 1" of Korame). For the longer-term, larger-scale vision (event bus,
> additional agents, Postgres/Neo4j, Azure GPU routing), see `KORAME-SAS.md`
> and `README.md` — those describe future phases, not what runs today.

---

## 🎯 What Was Built

Korame Phase 1 is a **kernel-first**, **multi-agent AI software factory** built in Python, with a React/TypeScript frontend for business users:

- ✅ Core kernel architecture (Agent, Provider, Task, Response, Registry)
- ✅ **RTE Agent** (Requirements & Test Engineer) — multi-turn clarification,
  adaptive question count (0-5, driven by genuine gaps, never a fixed habit),
  knowledge-base-driven suggestions from similar past requirements, handles
  revision requests on an already-finalized story, and decides whether a
  requirement needs a **single story or multiple independent stories**
- ✅ **Developer Agent** — decides whether a story needs a task breakdown at
  all (prefers one task, but splits a multi-page site into one task per
  page); detects Python vs. HTML output; implements/revises code; opens a
  real GitHub pull request once every task passes
- ✅ **Testing Agent** — generates real pytest tests (import-based for Python,
  text/structure assertions for HTML — never a browser); actually executes
  them in an isolated sandbox; detects when a *test itself* is broken (e.g.
  imported an unavailable package) and retries test generation instead of
  blaming the Developer for something that never really got tested
- ✅ **Shared per-story workspace** — every task in a story writes into the
  same temp-directory sandbox (not a throwaway one per task), so a multi-file
  deliverable like a multi-page site accumulates into one cohesive project
  and the final PR reflects everything actually built
- ✅ **Real GitHub integration** — REST API (not git CLI): branch creation,
  file commits, pull request opening; gracefully reports "not configured"
  if `GITHUB_TOKEN`/`GITHUB_REPO` aren't set
- ✅ **Automatic multi-story sequencing** — when RTE splits a complex
  requirement into several stories, the Developer works through them one at
  a time (implement → test → retry → PR, per story), only starting the next
  once the current one completes
- ✅ **Live workflow visualization** — non-blocking `/develop` (returns
  immediately, background task does the work) with a polling-based UI
  showing which agent is active, per-task status, a scrolling activity feed,
  and the resulting PR link — for both single-story and multi-story runs
- ✅ Knowledge Fabric (conversation/agent/session/working memory, embeddings,
  vector store, graph store, full-text search, artifacts, todo/story-run
  tracking) under `app/knowledge/`
- ✅ Model Router (Ollama provider; `think` mode tuned per-agent — enabled for
  RTE's judgment calls, disabled for Developer/Testing's format-constrained
  code/list generation to protect token budget)
- ✅ FastAPI REST API (chat + development-workflow endpoints)
- ✅ In-memory conversation storage with history-aware prompting, conversation
  list, and a "Requirements" library of finalized stories
- ✅ **React + TypeScript frontend** (Vite) — RTE chat with conversation
  sidebar, requirements library, multi-story "send all to development", and
  live agent-workflow visualization pages, under `frontend/`
- ✅ Comprehensive documentation

---

## 📁 Project Structure

```
korame/
├── app/                              # Main application (backend)
│   ├── __init__.py
│   ├── main.py                       # FastAPI entry point (Windows Proactor event loop policy set here)
│   │
│   ├── kernel/                       # CORE FOUNDATION
│   │   ├── __init__.py
│   │   ├── models.py                 # Context, Task, Response, Event
│   │   ├── agent.py                  # Agent base class
│   │   ├── provider.py               # Provider base class
│   │   └── registry.py               # Agent/provider registry
│   │
│   ├── agents/                       # Agent implementations
│   │   ├── __init__.py
│   │   ├── base/
│   │   │   ├── __init__.py
│   │   │   └── agent.py              # BaseAgent class
│   │   ├── rte/                      # Requirements & Test Engineer
│   │   │   ├── __init__.py
│   │   │   └── agent.py              # RTEAgent (clarification, splitting, suggestions)
│   │   ├── developer/                # Developer Agent
│   │   │   ├── __init__.py
│   │   │   └── agent.py              # DeveloperAgent (task breakdown, implement, PR)
│   │   └── testing/                  # Testing Agent
│   │       ├── __init__.py
│   │       ├── agent.py              # TestingAgent (test generation + execution)
│   │       └── sandbox.py            # Sandbox (isolated pytest execution, OS temp dir)
│   │
│   ├── integrations/                 # External service integrations
│   │   ├── __init__.py
│   │   └── github_service.py         # GitHubService (real REST API PR creation)
│   │
│   ├── providers/                    # Model providers
│   │   ├── __init__.py
│   │   ├── ollama.py                 # Ollama provider (direct HTTP, options nesting, retry, think toggle)
│   │   └── litellm.py                # Deprecated stub (raises ImportError if imported)
│   │
│   ├── router/                       # Task routing
│   │   ├── __init__.py
│   │   └── model_router.py           # Intelligent provider selection
│   │
│   ├── workflow/                     # Orchestration
│   │   ├── __init__.py
│   │   ├── engine.py                 # WorkflowEngine (single-story + multi-story cycles)
│   │   └── graph_engine.py           # LangGraph StateGraph (implement→test→fix loop)
│   │
│   ├── knowledge/                    # KNOWLEDGE FABRIC
│   │   ├── __init__.py
│   │   ├── knowledge_service.py      # Unified knowledge interface
│   │   ├── memory/                   # Conversation/agent/session/working memory
│   │   │   ├── __init__.py
│   │   │   ├── conversation.py       # ConversationMemory (history-aware)
│   │   │   ├── agent_memory.py
│   │   │   ├── session.py
│   │   │   └── working.py
│   │   ├── todos/                    # Developer/Testing workflow tracking
│   │   │   ├── __init__.py
│   │   │   └── todo_store.py         # TodoItem/TodoList/TodoStore + StoryRun/StoryRunStore
│   │   ├── artifacts/
│   │   │   ├── __init__.py
│   │   │   └── artifacts.py
│   │   ├── embeddings/
│   │   │   ├── __init__.py
│   │   │   └── embeddings.py
│   │   ├── vector/
│   │   │   ├── __init__.py
│   │   │   └── vector_store.py
│   │   ├── search/
│   │   │   ├── __init__.py
│   │   │   └── search.py
│   │   ├── graph/
│   │   │   ├── __init__.py
│   │   │   ├── neo4j_graph.py
│   │   │   └── networkx_graph.py
│   │   └── models/
│   │       └── __init__.py
│   │
│   ├── api/                          # REST endpoints
│   │   ├── __init__.py
│   │   ├── chat.py                   # /chat, /health, /conversations
│   │   └── development.py            # /develop, /todos/{id}, /develop-stories, /story-runs/{id}
│   │
│   ├── config/                       # Configuration
│   │   ├── __init__.py
│   │   └── settings.py               # Pydantic-based settings (incl. GitHub config)
│   │
│   ├── prompts/                      # Agent prompts
│   │   ├── __init__.py
│   │   ├── rte.md                    # RTE prompt (clarification, splitting, revision)
│   │   ├── developer.md              # Developer prompt (task breakdown, Python/HTML)
│   │   └── testing.md                # Testing prompt (import-based vs. text-assertion tests)
│   │
│   ├── models/                       # Reserved for data models
│   │   └── __init__.py
│   │
│   └── utils/                        # Utilities
│       ├── __init__.py
│       └── logging.py                # Rich logging setup
│
├── frontend/                         # React + TypeScript SPA (Vite)
│   ├── index.html
│   ├── package.json                  # react, react-router-dom, axios, zustand, react-markdown
│   ├── vite.config.ts / tsconfig*.json
│   ├── eslint.config.js
│   ├── .env / .env.example           # VITE_API_BASE_URL
│   │
│   └── src/
│       ├── main.tsx                  # Entry point
│       ├── App.tsx                   # Renders <AppRoutes />
│       ├── index.css                 # Global styles, K-logo animations, agent-workflow animations
│       ├── vite-env.d.ts
│       ├── routes/AppRoutes.tsx      # "/", "/rte", "/requirements", "/workflow", "/story-run"
│       ├── pages/
│       │   ├── HomePage.tsx          # Landing page
│       │   ├── RTEPage.tsx           # Business requirement chat + conversation sidebar
│       │   ├── RequirementsPage.tsx  # Library of finalized stories
│       │   ├── WorkflowPage.tsx      # Live single-story Dev/Test workflow view
│       │   └── StoryRunPage.tsx      # Live multi-story sequential workflow view
│       ├── hooks/useChat.ts          # Hook wrapping chatStore
│       ├── store/
│       │   ├── chatStore.ts          # Zustand: messages, conversations, API calls
│       │   ├── workflowStore.ts      # Zustand: single-story workflow polling
│       │   └── storyRunStore.ts      # Zustand: multi-story workflow polling
│       ├── api/
│       │   ├── client.ts             # Axios instance (baseURL, timeout)
│       │   ├── chatApi.ts            # submitBusinessRequirement(), listConversations(), etc.
│       │   └── developmentApi.ts     # startDevelopment(), getWorkflowStatus(), startStoryRun(), getStoryRunStatus()
│       ├── types/
│       │   ├── chat.ts               # ChatMessage (incl. stories[]), ChatApiResponse
│       │   └── workflow.ts           # WorkflowStatus, StoryRunStatus, WorkflowTodoItem, etc.
│       ├── theme/theme.ts            # Shared design tokens
│       ├── utils/constants.ts        # Agent name, API routes, storage keys
│       └── components/
│           ├── chat/                 # ChatWindow, ChatMessage (multi-story buttons), ChatInput, ConversationSidebar, TypingIndicator
│           ├── workflow/             # AgentWorkflow, TodoChecklist, ActivityLog
│           ├── common/               # EmptyState, ErrorAlert, LoadingSpinner
│           └── layout/                # AppHeader, Logo (animated "K")
│
├── tests/                            # Test suite (pytest, backend only)
│   ├── __init__.py
│   ├── conftest.py                   # Pytest fixtures & config
│   ├── test_kernel.py                # Kernel tests
│   ├── test_registry.py              # Registry tests
│   └── test_workflow.py              # Workflow tests
│
├── docs/                             # Documentation
│   ├── ARCHITECTURE.md               # Deep architectural guide
│   ├── CONTRIBUTING.md               # Contribution guidelines
│   ├── KNOWLEDGE-FABRIC.md           # Knowledge Fabric deep dive
│   └── QUICKSTART.md                 # 5-minute quickstart
│
├── scripts/                          # Helper scripts
│   ├── setup.py                      # Setup & verification
│   ├── quality-check.sh              # Code quality (Mac/Linux)
│   └── quality-check.bat             # Code quality (Windows)
│
├── pyproject.toml                    # Backend project config & dependencies
├── .env                              # Backend environment variables
├── .gitignore                        # Git ignore rules
└── README.md                         # Main readme
```

---

## 🔧 Core Components Explained

### 1. **Kernel** (app/kernel/)
The foundation everything depends on.

**Files**: models.py, agent.py, provider.py, registry.py

**Key Abstractions**:
- `Context` - Execution context (user, session, metadata)
- `Task` - Work unit for agents
- `Response` - Agent output
- `Event` - System events
- `Agent` - Base class for all agents
- `Provider` - Base class for all model providers
- `Registry` - Central registration of agents/providers

**Why it matters**: 
- Stable interfaces that never break
- Everything builds on this foundation
- New agents/providers don't require kernel changes

### 2. **Agents** (app/agents/)

**BaseAgent** (base/agent.py)
- Common functionality for all agents
- Error handling, validation

**RTEAgent** (rte/agent.py)
- Requirements & Test Engineer
- Takes business requirements plus prior conversation turns (if any)
- Asks clarifying questions when a requirement is ambiguous or incomplete
  (`STATUS: CLARIFICATION_NEEDED`), otherwise generates the final user story
  with acceptance criteria (`STATUS: READY`)
- Decides whether the requirement needs ONE story or genuinely independent
  MULTIPLE stories (separated by `---` in its reply); only splits when the
  requirement describes separately-shippable features, never just because a
  feature has many details
- Detects a request to revise an already-finalized story vs. a fresh requirement
- Looks up similar past requirements via full-text search and can surface
  actionable suggestions
- Uses `think=True` (deliberation helps ambiguity/judgment calls)

**DeveloperAgent** (developer/agent.py)
- Decides whether a story needs a task breakdown at all (prefers ONE task;
  only splits for genuinely separable work, e.g. one task per page of a
  multi-page site)
- Detects whether generated code is Python or a standalone HTML page
  (`detect_file_type`, with an `ast.parse` safety net for unrecognized content)
- Derives a stable, per-task filename (`derive_filename`) so multiple tasks
  can coexist as separate files in the same shared story workspace
- Implements/revises code based on Testing Agent feedback
- Opens a real GitHub pull request from the shared workspace's actual files
  once every task passes (`create_pull_request`)
- Uses `think=False` for code/task-list generation (format-constrained; avoids
  reasoning tokens truncating the output) except `populate_todo_list`'s
  breakdown call, which uses `think=True` (a judgment call)

**TestingAgent** (testing/agent.py)
- Generates real pytest tests: `import`-based for Python, `open()`-and-assert
  text/structure checks for HTML (never a browser or third-party package)
- Executes tests in a shared per-story `Sandbox` (app/agents/testing/sandbox.py)
- Targets just the current task's own test file per run (not the whole
  accumulated directory) for fast, clearly-attributed feedback
- Detects when a generated test itself is broken (e.g. imported an
  unavailable package) and retries test generation once with the specific
  error, instead of blaming the Developer for something that never actually ran

**How to add a new agent**:
```python
class ArchitectAgent(BaseAgent):
    async def execute(self, task: Task) -> Response:
        # Implementation
        pass

# Register in main.py
registry.register_agent(ArchitectAgent())
```

### 3. **Providers** (app/providers/)

**OllamaProvider** (ollama.py)
- Calls the local Ollama HTTP API directly (no LiteLLM)
- Handles `think: false` for Developer/Testing agents to protect token budget
- Configurable timeout, retries, `num_predict`, `temperature`

**litellm.py**
- Deprecated stub — raises `ImportError` if imported
- Kept as a placeholder; `OllamaProvider` is the sole active provider

### 4. **Model Router** (app/router/)

**V1**: Returns default provider (Ollama)

**Future**: Route by task type, complexity, resources
```python
# Tomorrow
if task_type == "architecture":
    return self.claude_provider
if task_type == "coding":
    return self.qwen_provider
```

### 5. **Workflow Engine** (app/workflow/)

**WorkflowEngine** (engine.py)
- Main orchestrator
- `execute()` — single agent execution via the registry
- `execute_development_cycle()` — the full Developer↔Testing loop for ONE
  story; delegates the per-item implement/test/retry cycle to a **LangGraph
  StateGraph** (`graph_engine.py`), then handles PR creation and RTE reporting
- `execute_multi_story_cycle()` — sequences `execute_development_cycle()`
  across MULTIPLE stories (from RTE’s split decision), one at a time
- Live status fields (`status`, `current_agent`, `current_activity`,
  `pull_request`, `report`, `error`) on `TodoList`/`StoryRun`, polled by the
  frontend

**LangGraph graph engine** (graph_engine.py)
- `build_dev_test_graph()` builds a compiled `StateGraph` for the
  implement → test → fix loop
- Nodes: `implement`, `test`, `advance`, `exhausted`
- Conditional routing: pass → advance to next item; fail+retryable → implement
  (retry); fail+exhausted → stop with blocked message
- `DevTestState` TypedDict: `item_index`, `attempt`, `test_feedback`, `stop`

```python
# Single agent
response = await engine.execute(
    agent_name="rte",
    input_data={"requirement": "..."}
)

# Full single-story Dev/Test cycle (used by POST /api/v1/develop)
result = await engine.execute_development_cycle(todo_list, story)

# Multi-story sequential cycle (used by POST /api/v1/develop-stories)
await engine.execute_multi_story_cycle(story_run)
```

### 5b. **GitHub Integration** (app/integrations/)

**GitHubService** (github_service.py)
- Real REST API calls (not git CLI): get base branch SHA → create branch ref
  → commit each file via the Contents API → open a pull request
- Gated behind `GITHUB_TOKEN`/`GITHUB_REPO`/`GITHUB_BASE_BRANCH` settings;
  reports `{"created": False, "reason": ...}` gracefully when unconfigured
  rather than failing the whole workflow

### 5c. **Sandbox** (app/agents/testing/sandbox.py)

- Isolated, per-story workspace under the OS temp directory (never inside the
  repo — avoids `uvicorn --reload`'s file watcher picking up generated code
  as a source change and restarting the app mid-workflow)
- Runs pytest via `subprocess.run()` inside a worker thread (`asyncio.to_thread`)
  rather than `asyncio.create_subprocess_exec()`, which requires the Proactor
  event loop on Windows and can raise a bare `NotImplementedError` otherwise
- Cleaned up once per story (not per task), after the PR is built from its contents

### 6. **Knowledge Fabric / Memory** (app/knowledge/memory/)

**ConversationMemory** (conversation.py)
- In-memory conversation storage (fast for V1)
- Stores messages with metadata
- `get_context_for_model()` formats prior turns for the model — the RTE agent
  uses this so it can ask clarifying questions with full context
- Future: Redis, PostgreSQL for persistence

### 7. **API** (app/api/)

**REST Endpoints** (`app/api/chat.py`):
- `POST /api/v1/chat` — Execute workflow. Response includes `needs_clarification`,
  `questions`, `suggestions`, and `stories` (populated when RTE splits a
  requirement into multiple independent stories)
- `GET /api/v1/health` - Health check
- `GET /api/v1/conversations/{id}` - Get history
- `GET /api/v1/conversations` - List all conversations

**REST Endpoints** (`app/api/development.py`):
- `POST /api/v1/develop` — Start a single-story Dev/Test workflow; returns
  immediately (`BackgroundTasks`) with a `todo_list_id` to poll
- `GET /api/v1/todos/{todo_list_id}` — Poll live status: current agent,
  activity, per-task status/code/test output, PR result
- `POST /api/v1/develop-stories` — Start an automatic multi-story workflow;
  returns immediately with a `story_run_id` to poll
- `GET /api/v1/story-runs/{story_run_id}` — Poll overall run status plus
  each story's own todo-list-level status

### 8. **Frontend** (frontend/)

React + TypeScript SPA built with Vite. Talks to the backend only through the
REST API above.

- **`store/chatStore.ts`** (Zustand) - owns `messages`, `conversations`,
  `conversationId`, `isLoading`, `error`; `sendRequirement()` posts to
  `/api/v1/chat`; `extractStoryTitle()` (exported) leniently parses a story's
  title even if the model doesn't format it exactly as instructed.
- **`store/workflowStore.ts`** / **`store/storyRunStore.ts`** (Zustand) —
  poll `/todos/{id}` / `/story-runs/{id}` every 1.5s, build an activity log,
  surface business-level errors the same way as network errors.
- **`hooks/useChat.ts`** - thin hook wrapping the chat store for components.
- **`pages/RTEPage.tsx`** - business-user chat page with a conversation
  sidebar; "Send to Development" (single story) or "Send All N Stories to
  Development" (multi-story split) buttons on finalized replies.
- **`pages/RequirementsPage.tsx`** - library of finalized stories, linking
  back into their original conversation.
- **`pages/WorkflowPage.tsx`** / **`pages/StoryRunPage.tsx`** - live views of
  a single-story / multi-story Dev/Test run: which agent is active, per-task
  checklist, activity feed, resulting PR link.
- **`components/chat/`** - `ChatWindow`, `ChatMessage` (renders markdown,
  multi-story blocks with their own send button, suggestions), `ChatInput`,
  `ConversationSidebar`, `TypingIndicator`.
- **`components/workflow/`** - `AgentWorkflow` (pipeline visualization with
  pulsing active-agent indicator), `TodoChecklist` (per-task status +
  expandable code/test-output detail), `ActivityLog` (scrolling feed).
- **`components/common/`** - `EmptyState`, `ErrorAlert`, `LoadingSpinner`.
- **`components/layout/`** - `AppHeader`, `Logo` (animated "K" mark).
- **`api/chatApi.ts`** / **`api/developmentApi.ts`** / **`api/client.ts`** -
  Axios wrappers for chat and development-workflow endpoints.

`components/project/`, `pages/DashboardPage.tsx`, `pages/ProjectPage.tsx`,
`pages/SettingsPage.tsx`, and `store/projectStore.ts` are still empty
placeholder files reserved for future project-management features.

---

## 📦 Dependencies

**Backend (Core)**:
- fastapi >= 0.104.0
- uvicorn >= 0.24.0
- pydantic >= 2.5.0
- pydantic-settings >= 2.1.0
- httpx >= 0.25.0
- python-dotenv >= 1.0.0
- rich >= 13.7.0
- langgraph >= 0.2 *(LangGraph StateGraph for the dev/test loop)*
- llama-index-core >= 0.11 *(LlamaIndex vector store)*
- llama-index-llms-ollama >= 0.3
- llama-index-embeddings-ollama >= 0.3 *(OllamaEmbedding for semantic search)*

**Backend (Dev)**:
- pytest >= 7.4.0
- pytest-asyncio >= 0.21.0
- pytest-cov >= 4.1.0
- black >= 23.11.0
- ruff >= 0.1.8
- mypy >= 1.7.0
- isort >= 5.13.0

**Frontend** (`frontend/package.json`):
- react ^18.3, react-dom ^18.3, react-router-dom ^6.28
- axios ^1.7 (HTTP client), zustand ^5.0 (chat state store)
- react-markdown ^9.0 (renders RTE responses)
- vite ^6.0, typescript ~5.6, eslint ^9.17 (dev tooling)

---

## 🚀 Quick Start

### 1. Install

```bash
git clone <korame-repo>
cd korame
python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate     # Windows
pip install -e ".[dev]"
```

### 2. Start Ollama

```bash
ollama serve
# In another terminal:
ollama pull qwen2.5-coder:7b     # generative model for all agents
ollama pull nomic-embed-text     # embedding model for semantic search
```

### 3. Run the backend

```bash
uvicorn app.main:app --reload
```

**Server**: http://localhost:8000  
**API Docs**: http://localhost:8000/docs

### 4. Test the backend

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Generate a user story (or get clarifying questions back)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "rte",
    "requirement": "Users should upload CSV files"
  }'
```

### 5. Install & run the frontend

```bash
cd frontend
npm install       # requires access to registry.npmjs.org
npm run dev
```

**Frontend**: http://localhost:5173/rte (configured via `frontend/.env` to call
the backend at `http://localhost:8000`)

> If `npm install` hangs with no progress on a corporate machine, check whether
> a network security proxy (e.g., Zscaler) is blocking `registry.npmjs.org`
> before assuming it's a code issue.

### 6. (Optional) Enable GitHub PR creation

Copy `.env.example` to `.env` and fill in:

```
GITHUB_TOKEN=<a personal access token with repo scope>
GITHUB_REPO=<owner/repo>
GITHUB_BASE_BRANCH=main
```

Without these set, the Developer Agent still runs the full implement/test/retry
loop but reports `{"created": false, "reason": "GitHub integration not configured..."}`
instead of opening a real pull request.

### 7. Try the Developer/Testing workflow end-to-end

1. Send a requirement to `/rte`, answer any clarifying questions until RTE
   replies with `STATUS: READY` (a finalized user story).
2. Click **"Send to Development"** on that message (or **"Send All N Stories
   to Development"** if RTE split the requirement into multiple stories).
3. You're navigated to `/workflow?id=...` (or `/story-run?id=...`), which
   polls the backend every 1.5s and shows which agent is active, the
   per-task checklist (expand a task to see its generated code and test
   output), a scrolling activity log, and the resulting PR link once done.

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_kernel.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

**Tests included**:
- Kernel models (Context, Task, Response, Event)
- Registry (agent/provider registration)
- Workflow engine (task execution)

---

## 📋 Configuration

Edit `.env`:

```env
# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# Ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:7b
OLLAMA_EMBED_MODEL=nomic-embed-text

# Logging
LOG_LEVEL=INFO
```

---

## 📚 Documentation

**docs/QUICKSTART.md** (5 min)
- Get running in 5 minutes
- Basic API calls
- Troubleshooting

**docs/ARCHITECTURE.md** (30 min)
- Deep architectural guide
- Component explanations
- Data flow diagrams
- Adding new components
- Scalability strategy

**docs/CONTRIBUTING.md**
- Development process
- Coding standards
- Testing guidelines
- How to add agents/providers

---

## 🎯 Data Flow

```
POST /chat {"agent_name": "rte", "requirement": "..."}
    ↓
API Handler
    ├─ Generate task_id
    ├─ Create conversation
    ├─ Call workflow_engine.execute()
    │
    ├─ Workflow Engine
    │  ├─ Look up "rte" in registry
    │  ├─ Call rte_agent.execute(task)
    │  │
    │  ├─ RTE Agent
    │  │  ├─ Load prompt from file
    │  │  ├─ Build full prompt
    │  │  ├─ Call model_router.route(task)
    │  │  │
    │  │  ├─ Model Router
    │  │  │  └─ Return default provider (Ollama)
    │  │  │
    │  │  ├─ Ollama Provider
    │  │  │  └─ Call Ollama HTTP API → qwen2.5-coder:7b
    │  │  │
    │  │  └─ Return Response (user_story)
    │  │
    │  └─ Return to API
    │
    ├─ Store in conversation memory
    │
    └─ Return ChatResponse
        ├─ task_id
        ├─ conversation_id
        ├─ user_story
        └─ status
```

---

## 🔌 Provider Architecture

The project calls the Ollama HTTP API directly via `OllamaProvider`. The
`litellm.py` file is a deprecated stub kept for historical reference.

**Current default**: `OllamaProvider` → `qwen2.5-coder:7b`

To swap in a different model, just change `.env`:
```bash
OLLAMA_MODEL=llama3.1:8b
```

To add a cloud provider later, implement the `Provider` base class and
register it in `main.py`.

---

## ✅ What Works Now

- ✅ RTE Agent generates user stories
- ✅ RTE Agent asks clarifying questions across multiple turns before
  finalizing a story (uses conversation history; frontend shows questions vs.
  final story differently)
- ✅ Model Router selects providers
- ✅ Ollama integration via direct HTTP API
- ✅ REST API with FastAPI
- ✅ In-memory conversation storage, history-aware prompting
- ✅ Registry for agents/providers
- ✅ Workflow orchestration
- ✅ Error handling
- ✅ Logging with Rich
- ✅ Type hints (Python 3.12+)
- ✅ Comprehensive test suite (backend)
- ✅ React + TypeScript frontend for submitting requirements and viewing the
  RTE conversation (`frontend/`)

---

## 🚧 Roadmap

### V2 (Next Phase)
- [ ] Architect Agent
- [x] Developer Agent *(built — Phase 1)*
- [ ] Redis event bus
- [ ] PostgreSQL persistence (conversations + artifacts)
- [ ] Docker Compose setup
- [x] Agent chaining (`execute_chain()` exists in WorkflowEngine)
- [ ] Frontend: Dashboard/Project/Settings pages (currently empty placeholders)
- [ ] Frontend: persist conversations server-side and list past conversations

### V3 (Future)
- [x] Code generation *(built — Developer Agent)*
- [ ] Code review agent
- [ ] Security scanning agent
- [x] Testing agent *(built — Phase 1)*
- [ ] UAT agent
- [ ] DevOps agent
- [x] LangGraph workflow orchestration *(added)*
- [x] Vector RAG with local embeddings (OllamaEmbedding + LlamaIndexVectorStore) *(added)*
- [ ] Vector RAG with external store (Qdrant/Pinecone)
- [ ] Multi-model routing
- [ ] Plugin system
- [ ] Kubernetes deployment
- [ ] MCP (Model Context Protocol)

---

## 🏗️ Architecture Principles

### 1. Kernel-First
- Stable interfaces in kernel
- Everything else builds on kernel
- Kernel rarely changes

### 2. Agent Independence
- Agents don't call each other
- Route through registry
- Enables flexibility

### 3. Provider Abstraction
- Code against `Provider` interface
- Not specific providers
- Swap `OllamaProvider` for any other implementation

### 4. Configuration Over Code
- Settings in `.env`
- Not hardcoded
- Different configs per environment

### 5. Event-Driven (Future)
- Currently: direct calls
- V2: event bus (Redis)
- Enables async, distributed execution

---

## 📖 File Reference

| File | Purpose | Key Classes |
|------|---------|-------------|
| app/kernel/models.py | Core data types | Context, Task, Response, Event |
| app/kernel/agent.py | Agent base class | Agent (abstract) |
| app/kernel/provider.py | Provider base class | Provider (abstract) |
| app/kernel/registry.py | Registration | Registry |
| app/agents/base/agent.py | Common agent logic | BaseAgent |
| app/agents/rte/agent.py | Requirements agent | RTEAgent |
| app/providers/ollama.py | Local LLM | OllamaProvider |
| app/providers/litellm.py | Deprecated stub | (raises ImportError) |
| app/router/model_router.py | Provider selection | ModelRouter |
| app/workflow/engine.py | Orchestration | WorkflowEngine |
| app/workflow/graph_engine.py | LangGraph dev/test loop | build_dev_test_graph, DevTestState |
| app/knowledge/memory/conversation.py | Conversation storage | ConversationMemory |
| app/api/chat.py | REST API | chat(), health(), get_conversation() |
| app/config/settings.py | Configuration | Settings |
| app/main.py | FastAPI app | create_app() |
| frontend/src/store/chatStore.ts | Chat state & API calls | useChatStore |
| frontend/src/hooks/useChat.ts | Chat hook | useChat() |
| frontend/src/pages/RTEPage.tsx | Business requirement page | RTEPage |
| frontend/src/api/chatApi.ts | Backend API calls | submitBusinessRequirement() |

---

## 🎓 Learning Path

1. **Start**: docs/QUICKSTART.md (5 min)
   - Get it running
   - Make a test API call

2. **Understand**: docs/ARCHITECTURE.md (30 min)
   - Read the architecture guide
   - Understand data flow
   - See how components connect

3. **Explore**: Read the code
   - app/kernel/ - Core interfaces
   - app/agents/rte/ - RTE agent
   - app/main.py - FastAPI setup

4. **Extend**: Add a new component
   - New agent (Architect)
   - New provider (OpenAI)
   - New endpoint

5. **Contribute**: Submit PR
   - Follow docs/CONTRIBUTING.md
   - Run tests
   - Check code quality

---

## 🛠️ Development Workflow

```bash
# 1. Start servers
ollama serve                    # Terminal 1
uvicorn app.main:app --reload  # Terminal 2

# 2. Make changes
# Edit app/agents/rte/agent.py (or whatever)

# 3. Check quality
black app/ tests/              # Format
flake8 app/ tests/             # Lint
mypy app/                      # Type check
pytest tests/ -v               # Test

# 4. Test API
curl http://localhost:8000/api/v1/chat ...

# 5. Commit
git add .
git commit -m "Add feature X"
git push
```

---

## ❓ Common Questions

**Q: Where do I add a new agent?**
A: Create `app/agents/myagent/agent.py`, inherit from BaseAgent, register in main.py

**Q: How do I use a different model?**
A: Change `.env`: `OLLAMA_MODEL=llama2` or use OpenAI: `OLLAMA_URL=https://api.openai.com`

**Q: Can I use my own model?**
A: Yes! Change `OLLAMA_MODEL` in `.env` to any model available on your Ollama instance

**Q: How do I store conversations permanently?**
A: V2 will add Redis/PostgreSQL. For now, ConversationMemory is in-memory

**Q: How do I chain agents?**
A: Use `engine.execute_chain()` (implementation in place, test it!)

**Q: Can I deploy to production?**
A: V1 is alpha. V2 will have Docker, K8s support. For now, it's dev/test only.

---

## 📞 Support

- **Questions**: Read docs/ARCHITECTURE.md first
- **Issues**: GitHub Issues with [BUG] tag
- **Ideas**: GitHub Discussions
- **Contributing**: See docs/CONTRIBUTING.md

---

## 🎉 You're All Set!

Your Korame V1 instance is complete with:

✅ Kernel foundation (stable, extensible)  
✅ RTE agent (working example)  
✅ Model routing (swappable providers)  
✅ REST API (production-ready FastAPI)  
✅ Tests (comprehensive coverage)  
✅ Docs (architecture, contributing, quickstart)  

**Next Steps**:
1. Follow docs/QUICKSTART.md to get it running
2. Make your first API call
3. Read docs/ARCHITECTURE.md to understand the design
4. Add a new agent (Architect) as your first contribution
5. Deploy to production (after V2 stabilization)

---

**Korame V1 is ready to scale to hundreds of agents.** 🚀

*Built: July 27, 2026*  
*Language: Python 3.12+*  
*Framework: FastAPI*  
*Status: Alpha (Ready for Development)*

