# Korame V1 Architecture

## Overview

Korame V1 is built on a **kernel-first** architecture. Every component depends only on stable interfaces defined in the kernel.

```
┌─────────────────────────────────────┐
│         FastAPI REST API            │
│  /chat  /health  /conversations     │
└────────────────┬────────────────────┘
                 │
        ┌────────▼────────┐
        │ Workflow Engine │
        └────────┬────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼────────┐       ┌────────▼──┐
│  Registry  │       │Model Router│
├────────────┤       └────────┬───┘
│  Agents    │                │
│  Providers │       ┌────────▼────────┐
└────────────┘       │     Provider    │
                     │   (LiteLLM)     │
                     └────────┬────────┘
                              │
                     ┌────────▼────────┐
                     │  Ollama/OpenAI/ │
                     │  Claude/etc     │
                     └─────────────────┘
```

## Core Components

### 1. Kernel (app/kernel/)

The foundation. Everything depends on these stable interfaces.

#### models.py
- **Context**: Execution context (user, session, metadata)
- **Task**: Unit of work
- **Response**: Agent output
- **Event**: System events
- **EventType**: Event types
- **ResponseStatus**: Status enum

```python
# All agents receive Task and return Response
async def execute(task: Task) -> Response:
    pass
```

#### agent.py
- **Agent**: Abstract base class
- Every agent inherits from this
- Must implement `execute(task: Task) -> Response`

```python
class MyAgent(Agent):
    async def execute(self, task: Task) -> Response:
        # Do work
        return Response(...)
```

#### provider.py
- **Provider**: Abstract model provider
- Handles communication with models
- All providers inherit from this

```python
class MyProvider(Provider):
    async def call(self, prompt: str, **kwargs) -> str:
        # Call model
        return response
```

#### registry.py
- **Registry**: Central registration for agents and providers
- Enables dependency management without coupling

```python
registry.register_agent(agent)
registry.register_provider(provider)
agent = registry.get_agent("rte")
```

### 2. Agents (app/agents/)

Each agent inherits from the kernel interface.

#### agents/base/agent.py
- **BaseAgent**: Common functionality for all agents

#### agents/rte/agent.py
- **RTEAgent**: Requirements & Test Engineer
- Takes business requirements
- Generates user stories with acceptance criteria
- Uses model router to select provider
- Loads prompts from file

```
Input: "Users should be able to upload CSV files"
↓
RTE Agent
↓
Model Router (selects provider)
↓
LiteLLM → Ollama → Qwen2 7B
↓
Output: "As a user, I want to upload CSV files..."
```

### 3. Providers (app/providers/)

Model provider implementations using LiteLLM abstraction.

#### providers/ollama.py
- **OllamaProvider**: Local Ollama models
- Uses LiteLLM for unified interface

#### providers/litellm.py
- **LiteLLMProvider**: Multi-provider support
- Works with any LiteLLM-supported model
- Tomorrow: OpenAI, Claude, etc.

**Why LiteLLM?**
- Single interface for 100+ models
- Swap providers without code changes
- Built-in error handling, retries, caching

### 4. Router (app/router/)

Intelligent task routing.

#### router/model_router.py
- **ModelRouter**: Decides which provider to use
- V1: Always returns default (Ollama)
- Future: Route based on task type, complexity, resources

```python
# Today
def route(task: Task) -> Provider:
    return self.default_provider  # Ollama

# Tomorrow
def route(task: Task) -> Provider:
    if task.type == "architecture":
        return self.claude_provider
    if task.type == "coding":
        return self.qwen_provider
    if task.type == "review":
        return self.gpt4_provider
```

### 5. Workflow Engine (app/workflow/)

Orchestrates task execution.

#### workflow/engine.py
- **WorkflowEngine**: Main orchestrator
- Takes agent name, routes through registry
- Manages task execution lifecycle
- Supports agent chaining (future)

```python
# Execute single agent
response = await engine.execute(
    agent_name="rte",
    input_data={"requirement": "..."}
)

# Execute agent chain (future)
responses = await engine.execute_chain(
    agent_sequence=["rte", "architect", "developer"],
    initial_input={"requirement": "..."}
)
```

### 6. Memory (app/memory/)

Conversation storage.

#### memory/conversation.py
- **ConversationMemory**: In-memory storage
- Stores message history per conversation
- Returns formatted context for models

```python
memory.add_message(
    conversation_id="conv-1",
    role="user",
    content="Add login feature"
)
```

### 7. API (app/api/)

REST endpoints.

#### api/chat.py

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/chat` | POST | Execute workflow |
| `/api/v1/conversations/{id}` | GET | Get history |

```python
@router.post("/api/v1/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    # Route through workflow engine
    response = await engine.execute(
        agent_name=request.agent_name,
        input_data={"requirement": request.requirement}
    )
    # Store in memory
    memory.add_message(...)
    return ChatResponse(...)
```

### 8. Configuration (app/config/)

#### config/settings.py
- **Settings**: Pydantic-based config
- Loads from `.env` file
- Type-safe environment variables

```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2:7b
LOG_LEVEL=INFO
```

### 9. Prompts (app/prompts/)

Agent-specific prompts.

#### prompts/rte.md
- RTE agent system prompt
- Loaded by RTEAgent at init
- Can be updated without code changes

```markdown
You are an expert Requirements & Test Engineer...

Generate a user story with:
- Title
- User story statement
- Description
- Acceptance Criteria
- Technical Notes
```

## Data Flow

### Single Agent Execution

```
1. User sends request to POST /api/v1/chat
   ├── Request: {"agent_name": "rte", "requirement": "..."}
   
2. API handler creates Chat request
   ├── Creates task_id
   ├── Creates conversation
   
3. Workflow engine routes to agent
   ├── Looks up "rte" in registry
   ├── Calls agent.execute(task)
   
4. RTE agent executes
   ├── Loads prompt from file
   ├── Builds full prompt with requirement
   ├── Calls model_router.route(task)
   
5. Model router selects provider
   ├── V1: Returns default (Ollama)
   
6. Provider calls model
   ├── Ollama → Qwen2 7B
   ├── Returns generated user story
   
7. Agent returns Response
   ├── Status: success
   ├── Data: {"user_story": "..."}
   
8. API handler stores in memory
   ├── Adds to conversation history
   
9. User receives response
   ├── Contains: task_id, conversation_id, user_story
```

### Agent Chaining (Future)

```
1. Initial input: {"requirement": "..."}

2. RTE Agent
   ├── Input: requirement
   ├── Output: user_story
   
3. Architect Agent  
   ├── Input: user_story
   ├── Output: system_design
   
4. Developer Agent
   ├── Input: system_design
   ├── Output: code
   
5. Final response: code
```

## Adding New Components

### Adding a New Agent

```python
# 1. Create file: app/agents/architect/agent.py

from app.agents.base import BaseAgent
from app.kernel.models import Task, Response

class ArchitectAgent(BaseAgent):
    def __init__(self, model_router, config=None):
        super().__init__("architect", config)
        self.model_router = model_router
        self.prompt = self._load_prompt()
    
    async def execute(self, task: Task) -> Response:
        # Implementation
        pass

# 2. Register in main.py
architect = ArchitectAgent(model_router)
registry.register_agent(architect)

# 3. Use in API
POST /api/v1/chat {"agent_name": "architect", ...}
```

### Adding a New Provider

```python
# 1. Create file: app/providers/anthropic.py

from app.kernel.provider import Provider

class AnthropicProvider(Provider):
    async def call(self, prompt: str, **kwargs) -> str:
        # LiteLLM call to Claude
        pass

# 2. Register in main.py
claude = AnthropicProvider("claude-3-opus")
registry.register_provider(claude)

# 3. Update router (optional)
def route(task: Task) -> Provider:
    if task.type == "review":
        return self.claude_provider
```

### Adding a New API Endpoint

```python
# 1. Add to app/api/chat.py

@router.post("/api/v1/new-endpoint")
async def new_endpoint(request: RequestModel) -> ResponseModel:
    # Use engine and memory
    response = await engine.execute(...)
    memory.add_message(...)
    return ResponseModel(...)
```

## Principles

### 1. Kernel-First Design
- Stable interfaces first
- Everything builds on kernel
- Kernel changes are rare and breaking

### 2. No Direct Agent Calls
- ❌ `agent.execute()` directly
- ✅ `workflow_engine.execute(agent_name)`
- Enables flexibility, testability, logging

### 3. Provider Abstraction
- ❌ Code directly against Ollama
- ✅ Use Provider interface + LiteLLM
- Swappable providers without code changes

### 4. Configuration Over Code
- ❌ Model name hardcoded
- ✅ From `.env` file
- Enables different configs per environment

### 5. In-Memory by Default
- V1 uses in-memory storage (fast)
- V2 adds Redis (distributed)
- V3 adds PostgreSQL (persistent)

## Testing

### Unit Tests
- Test kernel models
- Test registry
- Test provider abstraction
- No external dependencies

```bash
pytest tests/test_kernel.py
pytest tests/test_registry.py
```

### Integration Tests (Future)
- Test full workflows
- Test agent chaining
- Requires Ollama running

```bash
pytest tests/test_workflow.py
```

### End-to-End Tests (Future)
- Test full API flow
- Test with real Ollama
- Slower but most complete

## Scalability

### Why This Architecture Scales

1. **Loose Coupling**
   - Agents don't know about each other
   - Registry is the only mediator
   - New agents don't break existing ones

2. **Provider Independence**
   - Agents use Router
   - Router uses Provider interface
   - Can add 10 new providers tomorrow

3. **Single Responsibility**
   - Each component has one job
   - Easy to test in isolation
   - Easy to optimize independently

4. **Extensible**
   - New agents: just inherit Agent
   - New providers: just inherit Provider
   - New features: don't change kernel

### Future Scaling

**V2 Scaling:**
- Redis event bus (publish-subscribe)
- Multiple worker processes
- Distributed agent execution

**V3 Scaling:**
- PostgreSQL for persistence
- Qdrant for vector storage (RAG)
- Kubernetes orchestration
- Multi-region deployment

But the kernel stays the same.

---

*Korame: Kernel-First, Agent-Native, Model-Agnostic*

