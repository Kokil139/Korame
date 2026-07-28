# Korame V1 - Directory Tree & File Guide

```
korame/
│
├── 📄 BUILD-SUMMARY.md                    ⭐ START HERE - Complete overview
├── 📄 PROJECT-CHECKLIST.md                ✅ Verification checklist  
├── 📄 README.md                           📖 Main readme (existing)
├── 📄 DIRECTORY-GUIDE.md                  🗺️  Directory tree & navigation (this file)
├── 📄 QUICK-REFERENCE.md                  🔑 Principles, state machine, event flow cheat sheet
├── 📄 KORAME-SAS.md                       📐 Full Software Architecture Specification
├── 📄 IMPLEMENTATION-GUIDE.md             🧭 Onboarding guide for new developers
├── 📄 KNOWLEDGE-FABRIC-BUILD.md           🧠 Knowledge Fabric build notes
├── 📄 docs-ADRs.md                        📝 Architecture Decision Records
├── 📄 pyproject.toml                      ⚙️  Backend dependencies & config
├── 📄 .env                                🔐 Backend environment variables
├── 📄 .gitignore                          🚫 Git ignore rules
│
│
├── 📁 app/                                🎯 MAIN APPLICATION (backend)
│   │
│   ├── __init__.py                        📦 Package init
│   ├── main.py                            ⭐ ENTRY POINT - FastAPI app
│   │
│   ├── 📁 kernel/                         🏗️  CORE FOUNDATION
│   │   ├── __init__.py
│   │   ├── models.py                      📊 Context, Task, Response, Event
│   │   ├── agent.py                       👤 Agent base class (abstract)
│   │   ├── provider.py                    🤖 Provider base class (abstract)
│   │   └── registry.py                    📋 Agent/provider registry
│   │
│   ├── 📁 agents/                         👥 AGENT IMPLEMENTATIONS
│   │   ├── __init__.py
│   │   ├── 📁 base/                       🔧 Base utilities
│   │   │   ├── __init__.py
│   │   │   └── agent.py                   BaseAgent (common logic)
│   │   └── 📁 rte/                        📝 RTE Agent (example)
│   │       ├── __init__.py
│   │       └── agent.py                   RTEAgent (working)
│   │
│   ├── 📁 providers/                      🧠 MODEL PROVIDERS
│   │   ├── __init__.py
│   │   ├── ollama.py                      🟠 OllamaProvider (local LLM)
│   │   └── litellm.py                     🔵 LiteLLMProvider (100+ models)
│   │
│   ├── 📁 router/                         🔀 ROUTING LOGIC
│   │   ├── __init__.py
│   │   └── model_router.py                🚦 ModelRouter (provider selection)
│   │
│   ├── 📁 workflow/                       ⚙️  ORCHESTRATION
│   │   ├── __init__.py
│   │   └── engine.py                      🎬 WorkflowEngine (main orchestrator)
│   │
│   ├── 📁 knowledge/                      🧠 KNOWLEDGE & MEMORY LAYER
│   │   ├── __init__.py
│   │   ├── knowledge_service.py           🔍 Knowledge service (main interface)
│   │   ├── 📁 memory/                     💾 CONVERSATION STORAGE
│   │   │   ├── __init__.py
│   │   │   ├── conversation.py            🗣️  ConversationMemory (in-memory)
│   │   │   ├── agent_memory.py            👤 Agent memory management
│   │   │   ├── session.py                 🔐 Session tracking
│   │   │   └── working.py                 📝 Working memory
│   │   ├── 📁 artifacts/                  📦 STORED ARTIFACTS
│   │   │   ├── __init__.py
│   │   │   └── artifacts.py               📎 Artifact storage & retrieval
│   │   ├── 📁 embeddings/                 🔗 EMBEDDINGS
│   │   │   ├── __init__.py
│   │   │   └── embeddings.py              🧮 Embedding generation & caching
│   │   ├── 📁 vector/                     🎯 VECTOR STORAGE
│   │   │   ├── __init__.py
│   │   │   └── vector_store.py            📊 Vector store (similarity search)
│   │   ├── 📁 search/                     🔎 SEARCH ENGINE
│   │   │   ├── __init__.py
│   │   │   └── search.py                  🔍 Unified search interface
│   │   ├── 📁 graph/                      🌐 KNOWLEDGE GRAPHS
│   │   │   ├── __init__.py
│   │   │   ├── neo4j_graph.py             🔗 Neo4j graph backend
│   │   │   └── networkx_graph.py          🔗 NetworkX graph backend
│   │   └── 📁 models/                     📊 KNOWLEDGE DATA MODELS
│   │       └── __init__.py                (reserved for expansion)
│   │
│   ├── 📁 api/                            🌐 REST API
│   │   ├── __init__.py
│   │   └── chat.py                        📡 Endpoints: /chat, /health, /conversations
│   │
│   ├── 📁 config/                         ⚙️  CONFIGURATION
│   │   ├── __init__.py
│   │   └── settings.py                    🔧 Pydantic settings (from .env)
│   │
│   ├── 📁 prompts/                        📝 AGENT PROMPTS
│   │   ├── __init__.py
│   │   └── rte.md                         RTE system prompt
│   │
│   ├── 📁 models/                         📊 DATA MODELS
│   │   └── __init__.py                    (reserved for expansion)
│   │
│   └── 📁 utils/                          🛠️  UTILITIES
│       ├── __init__.py
│       └── logging.py                     📊 Rich logging setup
│
│
├── 📁 frontend/                           💻 REACT FRONTEND (Vite + TypeScript)
│   ├── index.html                         Entry HTML
│   ├── package.json                       react, react-router-dom, axios, zustand, react-markdown
│   ├── vite.config.ts / tsconfig*.json    Build & type-check config
│   ├── eslint.config.js                   Lint config
│   ├── .env / .env.example                🔐 VITE_API_BASE_URL (points at backend)
│   │
│   └── 📁 src/
│       ├── main.tsx                       ⭐ ENTRY POINT - mounts <App />
│       ├── App.tsx                        Renders <AppRoutes />
│       ├── index.css                      Global styles & animations
│       ├── vite-env.d.ts                  Vite client type reference
│       │
│       ├── 📁 routes/
│       │   └── AppRoutes.tsx              "/" welcome + "/rte" chat page routing
│       │
│       ├── 📁 pages/
│       │   ├── RTEPage.tsx                📝 Business requirement chat page (built)
│       │   ├── DashboardPage.tsx          (placeholder - reserved for V2)
│       │   ├── ProjectPage.tsx            (placeholder - reserved for V2)
│       │   └── SettingsPage.tsx           (placeholder - reserved for V2)
│       │
│       ├── 📁 hooks/
│       │   └── useChat.ts                 Hook wrapping chatStore for components
│       │
│       ├── 📁 store/
│       │   ├── chatStore.ts               🗣️  Zustand store: messages, conversationId, API calls
│       │   └── projectStore.ts            (placeholder - reserved for V2)
│       │
│       ├── 📁 api/
│       │   ├── client.ts                  Axios instance (baseURL, 120s timeout)
│       │   └── chatApi.ts                 submitBusinessRequirement(), fetchConversationHistory()
│       │
│       ├── 📁 types/
│       │   ├── chat.ts                    ChatMessage, ChatApiResponse, ConversationHistory*
│       │   └── project.ts                 (placeholder - reserved for V2)
│       │
│       ├── 📁 theme/
│       │   └── theme.ts                   Shared design tokens (colors, radius, font)
│       │
│       ├── 📁 utils/
│       │   └── constants.ts               Agent name, API routes, storage keys
│       │
│       └── 📁 components/
│           ├── 📁 chat/                   💬 ChatWindow, ChatMessage, ChatInput, TypingIndicator
│           ├── 📁 common/                 EmptyState, ErrorAlert, LoadingSpinner
│           ├── 📁 layout/                 (placeholder - AppHeader, AppLayout, Sidebar - V2)
│           └── 📁 project/                (placeholder - NewProjectDialog, ProjectCard, ProjectList - V2)
│
│
├── 📁 tests/                              🧪 TEST SUITE
│   ├── __init__.py
│   ├── conftest.py                        🔧 Pytest fixtures & config
│   ├── test_kernel.py                     ✅ Kernel tests (5 tests)
│   ├── test_registry.py                   ✅ Registry tests (4 tests)
│   └── test_workflow.py                   ✅ Workflow tests (3 tests)
│
│
├── 📁 docs/                               📚 DOCUMENTATION
│   ├── QUICKSTART.md                      ⭐ 5-minute quick start
│   ├── ARCHITECTURE.md                    🏗️  Deep architectural guide
│   └── CONTRIBUTING.md                    🤝 Contribution guidelines
│
│
└── 📁 scripts/                            🔧 HELPER SCRIPTS
    ├── setup.py                           ⚙️  Setup & verification
    ├── quality-check.sh                   🔍 Code quality (Mac/Linux)
    └── quality-check.bat                  🔍 Code quality (Windows)
```

---

## 📍 Finding Your Way Around

### 🎯 If You Want To...

**Understand the architecture**
- Read: `BUILD-SUMMARY.md`
- Then: `docs/ARCHITECTURE.md`

**Get the backend running**
- Read: `docs/QUICKSTART.md`
- Run: `uvicorn app.main:app --reload`

**Get the frontend running**
- `cd frontend && npm install && npm run dev`
- Visit http://localhost:5173/rte (requires the backend running on port 8000
  and Ollama serving the configured model)
- If `npm install` hangs with no progress, check for a corporate network proxy
  (e.g., Zscaler) blocking `registry.npmjs.org` before assuming it's a code problem

**Understand the RTE chat/clarification flow**
- Backend: `app/prompts/rte.md` (STATUS markers) → `app/agents/rte/agent.py`
  (parses status, builds history-aware prompt) → `app/api/chat.py` (passes
  conversation history, returns `needs_clarification`/`questions`)
- Frontend: `frontend/src/store/chatStore.ts` (calls the API, keeps
  `conversationId`) → `frontend/src/pages/RTEPage.tsx` (renders the chat)

**Add a new agent**
1. Check: `docs/CONTRIBUTING.md`
2. Copy: `app/agents/rte/agent.py`
3. Create: `app/agents/myagent/agent.py`
4. Register: In `app/main.py`

**Add a new provider**
1. Check: `docs/ARCHITECTURE.md` (Providers section)
2. Copy: `app/providers/ollama.py`
3. Create: `app/providers/myprovider.py`
4. Register: In `app/main.py`

**Understand the data flow**
- Read: `docs/ARCHITECTURE.md` (Data Flow section)
- Look at: `app/main.py` (how it all connects)

**Run tests**
```bash
pytest tests/test_kernel.py -v     # No Ollama needed
pytest tests/test_workflow.py -v   # Needs Ollama
```

**Check code quality**
```bash
python scripts/setup.py            # Windows
bash scripts/quality-check.sh      # Mac/Linux
```

**See the API docs**
- Visit: http://localhost:8000/docs (when server running)

---

## 🔑 Key Files to Know

### Core Files (Must Read)
| File | Purpose | Key Content |
|------|---------|-------------|
| `app/kernel/models.py` | Core types | Context, Task, Response, Event |
| `app/kernel/agent.py` | Agent interface | Agent (abstract base) |
| `app/kernel/provider.py` | Provider interface | Provider (abstract base) |
| `app/main.py` | App setup | FastAPI initialization |

### Example Files (Learn From)
| File | Purpose | Pattern |
|------|---------|---------|
| `app/agents/rte/agent.py` | Working agent | How to implement agents |
| `app/providers/ollama.py` | Working provider | How to implement providers |
| `tests/test_kernel.py` | Testing kernel | How to test components |

### Frontend Files (Learn From)
| File | Purpose | Pattern |
|------|---------|---------|
| `frontend/src/store/chatStore.ts` | Chat state + API calls | Zustand store pattern used across the app |
| `frontend/src/hooks/useChat.ts` | Hook over the store | How pages consume state without touching the store directly |
| `frontend/src/api/chatApi.ts` | Backend API calls | How to call a new backend endpoint from the frontend |
| `frontend/src/components/chat/ChatMessage.tsx` | Chat bubble rendering | How to style clarification vs. final-story vs. error messages |

### Configuration Files
| File | Purpose | Controls |
|------|---------|----------|
| `.env` | Backend environment variables | API port, Ollama URL, model name, log level |
| `pyproject.toml` | Backend project config | Dependencies, versions, tool settings |
| `frontend/.env` | Frontend environment variables | `VITE_API_BASE_URL` (backend URL) |
| `frontend/package.json` | Frontend project config | Dependencies, scripts (`dev`, `build`, `lint`) |

### Documentation Files
| File | Time | Level | Purpose |
|------|------|-------|---------|
| `BUILD-SUMMARY.md` | 10 min | Beginner | Overview & statistics |
| `DIRECTORY-GUIDE.md` | 10 min | Beginner | Directory tree & navigation (this file) |
| `docs/QUICKSTART.md` | 5 min | Beginner | Get it running |
| `docs/ARCHITECTURE.md` | 30 min | Intermediate | Deep dive |
| `docs/KNOWLEDGE-FABRIC.md` | 20 min | Intermediate | Knowledge Fabric deep dive |
| `docs/CONTRIBUTING.md` | 20 min | Intermediate | Development process |
| `KORAME-SAS.md` | 45 min | Advanced | Full architecture specification |
| `PROJECT-CHECKLIST.md` | 5 min | All | Verification checklist |

---

## 🚀 Quick Navigation

### First Time Here?
1. Read this file (you are here!)
2. Read `BUILD-SUMMARY.md` (overview)
3. Read `docs/QUICKSTART.md` (get running)
4. Try the API (make a curl request)

### Want to Contribute?
1. Read `docs/CONTRIBUTING.md`
2. Pick a task (agent, provider, endpoint)
3. Look at an example (RTE agent, Ollama provider)
4. Follow the pattern
5. Run tests and quality checks
6. Submit PR

### Want to Understand the Code?
1. Start with `app/kernel/models.py` (data types)
2. Then `app/kernel/agent.py` (agent interface)
3. Then `app/main.py` (how it connects)
4. Then specific component (agents, providers, etc.)

### Having Problems?
1. Check `docs/QUICKSTART.md` (Troubleshooting section)
2. Check inline code comments
3. Run tests: `pytest tests/ -v`
4. Check logs: Set `LOG_LEVEL=DEBUG` in `.env`

---

## 📊 File Statistics

```
App Code:
  kernel/          4 files    300 lines   (foundation)
  agents/          5 files    400 lines   (implementation)
  providers/       2 files    150 lines   (integration)
  router/          1 file      50 lines   (routing)
  workflow/        1 file     150 lines   (orchestration)
  knowledge/       12 files   ~800 lines  (memory, embeddings, vectors, graphs, search)
    ├─ memory/       4 files    200 lines  (conversation, agent, session, working)
    ├─ artifacts/    1 file     100 lines  (storage)
    ├─ embeddings/   1 file     100 lines  (generation)
    ├─ vector/       1 file     150 lines  (similarity search)
    ├─ search/       1 file     100 lines  (unified search)
    ├─ graph/        2 files    150 lines  (neo4j, networkx)
    └─ models/       1 file      50 lines  (data models)
  api/             1 file     180 lines   (endpoints)
  config/          1 file      40 lines   (settings)
  utils/           1 file      50 lines   (logging)
  main.py          1 file     100 lines   (setup)
  ────────────────────────────────────────
  TOTAL:          26 files   ~2300 lines

Tests:
  test_kernel.py   1 file      50 lines   (5 tests)
  test_registry.py 1 file      50 lines   (4 tests)
  test_workflow.py 1 file      50 lines   (3 tests)
  conftest.py      1 file      50 lines   (fixtures)
  ────────────────────────────────────────
  TOTAL:           4 files    ~200 lines  (12 tests)

Frontend (frontend/src/):
  api/                 2 files    60 lines   (client.ts, chatApi.ts)
  store/               1 file     95 lines   (chatStore.ts - zustand)
  hooks/               1 file     20 lines   (useChat.ts)
  components/chat/     4 files   170 lines   (ChatWindow, ChatMessage, ChatInput, TypingIndicator)
  components/common/   3 files    60 lines   (EmptyState, ErrorAlert, LoadingSpinner)
  pages/               1 file     45 lines   (RTEPage.tsx built; Dashboard/Project/Settings empty)
  routes/              1 file     35 lines   (AppRoutes.tsx)
  types/               1 file     35 lines   (chat.ts)
  theme/               1 file     25 lines   (theme.ts)
  utils/               1 file     10 lines   (constants.ts)
  App.tsx / main.tsx / index.css              (bootstrap + global styles)
  ────────────────────────────────────────
  TOTAL:  ~17 built files (plus reserved empty placeholders for Dashboard/
          Project/Settings pages, projectStore, layout/project components)

Docs:
  BUILD-SUMMARY.md     (this comprehensive guide)
  DIRECTORY-GUIDE.md   (directory tree & navigation - this file)
  PROJECT-CHECKLIST.md (verification checklist)
  QUICK-REFERENCE.md   (principles/state-machine cheat sheet)
  KORAME-SAS.md            (full architecture specification)
  IMPLEMENTATION-GUIDE.md  (developer onboarding)
  KNOWLEDGE-FABRIC-BUILD.md (knowledge fabric build notes)
  docs-ADRs.md             (architecture decision records)
  docs/QUICKSTART.md        (5-minute quick start)
  docs/ARCHITECTURE.md      (30-minute deep dive)
  docs/CONTRIBUTING.md      (development guidelines)
  docs/KNOWLEDGE-FABRIC.md  (knowledge fabric deep dive)

Scripts:
  setup.py             (setup & verification)
  quality-check.sh     (code quality - Unix)
  quality-check.bat    (code quality - Windows)

Config:
  pyproject.toml       (dependencies & project config)
  .env                 (environment variables)
  .gitignore           (git ignore rules)
```

---

## 🎯 Component Relationships

```
Frontend (frontend/src, Vite dev server :5173)
    │  HTTP (axios) → VITE_API_BASE_URL
    ▼
FastAPI (app/main.py, :8000)
    │
    ├─→ API Routes (app/api/chat.py)
    │   └─→ Workflow Engine (app/workflow/engine.py)
    │       └─→ Registry (app/kernel/registry.py)
    │           ├─→ Agents (app/agents/*/agent.py)
    │           │   ├─→ Model Router (app/router/model_router.py)
    │           │   │   └─→ Providers (app/providers/*.py)
    │           │   │       └─→ LiteLLM (100+ models)
    │           │   │
    │           │   └─→ Prompts (app/prompts/*.md)
    │           │
    │           └─→ Providers (app/providers/*.py)
    │
    ├─→ Knowledge Service (app/knowledge/knowledge_service.py)
    │   ├─→ Memory (app/knowledge/memory/conversation.py)
    │   ├─→ Embeddings (app/knowledge/embeddings/embeddings.py)
    │   ├─→ Vector Store (app/knowledge/vector/vector_store.py)
    │   ├─→ Search (app/knowledge/search/search.py)
    │   ├─→ Knowledge Graphs (app/knowledge/graph/*.py)
    │   └─→ Artifacts (app/knowledge/artifacts/artifacts.py)
    │
    └─→ Config (app/config/settings.py)
        └─→ .env file
```

---

## 💡 Pro Tips

1. **Use type hints** - All functions have them; they help with IDE autocomplete
2. **Read docstrings** - Every class and method has documentation
3. **Check tests** - Tests show how to use components
4. **Use fixtures** - `conftest.py` has reusable test components
5. **Follow patterns** - Look at RTE agent/Ollama provider as examples
6. **Keep it small** - V1 is intentionally minimal; add features in V2
7. **Test as you go** - Write tests with your code
8. **Use the API docs** - Visit /docs when server is running

---

## 🔐 Important Reminders

### Before Running
- [ ] Python 3.12+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed: `pip install -e ".[dev]"`
- [ ] Ollama running: `ollama serve`
- [ ] Model pulled: `ollama pull qwen2:7b`

### When Committing
- [ ] Code formatted: `black app/ tests/`
- [ ] No lint issues: `flake8 app/ tests/`
- [ ] Types check: `mypy app/`
- [ ] Tests pass: `pytest tests/ -v`
- [ ] Coverage: `pytest --cov=app` (80%+)

### When Adding Code
- [ ] Add docstrings
- [ ] Add type hints
- [ ] Add tests
- [ ] Follow naming conventions
- [ ] Follow existing patterns

---

## 🎓 Learning Paths

### Path 1: Quick Tinkering (30 min)
1. Read QUICKSTART.md
2. Start server
3. Make API calls
4. Try changing prompts

### Path 2: Understanding (2 hours)
1. Read BUILD-SUMMARY.md
2. Read ARCHITECTURE.md
3. Explore code structure
4. Run tests
5. Make one small change

### Path 3: Contributing (1 day)
1. Read all docs
2. Run all tests
3. Understand patterns
4. Add new agent or provider
5. Submit PR

### Path 4: Mastery (ongoing)
1. Understand kernel thoroughly
2. Add multiple agents
3. Implement new providers
4. Optimize architecture
5. Lead development

---

## 📞 Reference Quick Links

| Need | Where | File |
|------|-------|------|
| Overview | BUILD-SUMMARY.md | 🔗 /BUILD-SUMMARY.md |
| 5-min start | QUICKSTART.md | 🔗 /docs/QUICKSTART.md |
| Architecture | ARCHITECTURE.md | 🔗 /docs/ARCHITECTURE.md |
| Contributing | CONTRIBUTING.md | 🔗 /docs/CONTRIBUTING.md |
| Checklist | PROJECT-CHECKLIST.md | 🔗 /PROJECT-CHECKLIST.md |
| App entry | main.py | 🔗 /app/main.py |
| Kernel core | kernel/models.py | 🔗 /app/kernel/models.py |
| Knowledge service | knowledge/knowledge_service.py | 🔗 /app/knowledge/knowledge_service.py |
| Example agent | agents/rte/agent.py | 🔗 /app/agents/rte/agent.py |
| Example provider | providers/ollama.py | 🔗 /app/providers/ollama.py |
| Tests | tests/ | 🔗 /tests/ |
| Config | .env | 🔗 /.env |

---

## 🎉 You're Ready!

The entire Korame V1 project is complete and ready to use:

✅ All files created  
✅ All components implemented  
✅ All tests written  
✅ All docs written  
✅ All config files ready  

**Next step**: Follow `docs/QUICKSTART.md` to get it running!

---

*Korame V1 - Built July 27, 2026 - Ready for Development* 🚀

