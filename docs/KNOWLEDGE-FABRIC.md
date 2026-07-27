# Korame Knowledge Fabric

**Enterprise-Grade Knowledge Management for AI-Native Software Factory**

The Knowledge Fabric is the central intelligence system that manages all knowledge, context, and state in Korame.

---

## 🎯 Overview

```
Knowledge Fabric
    │
    ├─ Memory Systems
    │   ├─ Conversation Memory (user-agent interactions)
    │   ├─ Agent Memory (agent-specific state)
    │   ├─ Session Memory (session-level context)
    │   └─ Working Memory (temporary computation)
    │
    ├─ Knowledge Graph
    │   ├─ NetworkX (in-memory, default)
    │   └─ Neo4j (production)
    │
    ├─ Vector Store
    │   └─ In-memory (V1)
    │   └─ Qdrant/Pinecone/Weaviate (future)
    │
    ├─ Embeddings
    │   ├─ Sentence Transformers (local)
    │   ├─ OpenAI (API)
    │   └─ Custom providers
    │
    ├─ Search Systems
    │   ├─ Full-Text Search (keyword matching)
    │   ├─ Semantic Search (embedding similarity)
    │   └─ Hybrid Search (combined)
    │
    └─ Artifact Storage
        ├─ Versioning
        ├─ Relationships
        ├─ Tags & Metadata
        └─ Status Tracking
```

---

## 📦 Components

### 1. Memory Systems

#### Conversation Memory
Stores all user-agent interactions in a conversation.

```python
from app.knowledge import ConversationMemory

memory = ConversationMemory()
memory.add_message(
    conversation_id="conv-1",
    role="user",
    content="Generate a login feature",
    agent_name="rte"
)

# Get conversation context
context = memory.get_context_for_model("conv-1", max_messages=10)
```

#### Agent Memory
Stores agent-specific state with optional TTL.

```python
from app.knowledge import AgentMemory

memory = AgentMemory()
memory.store(
    agent_name="rte",
    key="recent_requirements",
    value=["login", "signup", "profile"],
    ttl_seconds=3600  # 1 hour
)

# Retrieve
value = memory.retrieve("rte", "recent_requirements")
```

#### Session Memory
Manages session-level variables with TTL.

```python
from app.knowledge import SessionMemory

session_mem = SessionMemory()
session_mem.create_session("session-1", "user-123")
session_mem.set_variable("session-1", "current_feature", "auth")
```

#### Working Memory
Temporary storage for computation with scopes.

```python
from app.knowledge import WorkingMemory, MemoryScope

working = WorkingMemory()
working.store(
    key="intermediate_result",
    value=data,
    scope=MemoryScope.TASK  # Valid for one task only
)

# Retrieve
result = working.retrieve("intermediate_result")
```

### 2. Knowledge Graph

#### NetworkX (Default for V1)
In-memory graph for quick prototyping.

```python
from app.knowledge import NetworkXGraph

graph = NetworkXGraph()

# Add nodes
graph.add_node("user-1", "User", {"name": "Alice"})
graph.add_node("story-1", "UserStory", {"title": "Login"})

# Add edges
graph.add_edge("user-1", "story-1", "CREATED")

# Query
related = graph.get_related_nodes("user-1", max_depth=2)
path = graph.find_path("user-1", "story-1")
```

#### Neo4j (Production)
Distributed graph database.

```python
from neo4j import GraphDatabase
from app.knowledge import Neo4jGraph

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
graph = Neo4jGraph(driver)

# Same API as NetworkX
graph.add_node("user-1", "User", {"name": "Alice"})
graph.add_edge("user-1", "story-1", "CREATED")
```

### 3. Vector Store & Embeddings

#### Vector Store
Stores embeddings for similarity search.

```python
from app.knowledge import InMemoryVectorStore, SentenceTransformersEmbedding

# Create embeddings provider
embedder = SentenceTransformersEmbedding("all-MiniLM-L6-v2")

# Create vector store
vector_store = InMemoryVectorStore(vector_dimension=384)

# Add vectors
text = "Users should be able to log in with email"
embedding = embedder.embed_text(text)
vector_store.add("story-1", embedding, text=text)

# Search
query_embedding = embedder.embed_text("authentication")
results = vector_store.search(query_embedding, k=10, threshold=0.5)
```

#### Embedding Providers
- **Sentence Transformers** - Local, fast, free (recommended for V1)
- **OpenAI** - High quality, requires API key
- **Custom** - Implement `EmbeddingProvider` interface

### 4. Search Systems

#### Full-Text Search
Keyword matching.

```python
from app.knowledge import FullTextSearch

search = FullTextSearch()
search.index_document("doc-1", "Title", "Description", "Content")
results = search.search("login authentication", limit=10)
```

#### Semantic Search
Embedding-based similarity.

```python
from app.knowledge import SemanticSearch

semantic = SemanticSearch(vector_store, embedder)
semantic.index_document("doc-1", "Title", "Description", "Content")
results = semantic.search("user authentication", limit=10, threshold=0.5)
```

#### Hybrid Search
Combines both methods.

```python
from app.knowledge import HybridSearch

hybrid = HybridSearch(full_text_search, semantic_search)
results = hybrid.search(
    "user authentication",
    limit=10,
    full_text_weight=0.3,
    semantic_weight=0.7
)
```

### 5. Artifact Storage

Stores all software engineering artifacts with versioning.

```python
from app.knowledge import ArtifactStore, ArtifactType, ArtifactStatus

artifacts = ArtifactStore()

# Create
artifact = artifacts.create_artifact(
    artifact_id="story-1",
    artifact_type=ArtifactType.USER_STORY,
    title="User Login",
    description="Allow users to log in",
    created_by="alice"
)

# Update
artifacts.update_artifact(
    artifact_id="story-1",
    content="Updated content",
    author="alice",
    change_summary="Fixed typos"
)

# Manage status
artifacts.set_status("story-1", ArtifactStatus.APPROVED)

# Query
user_stories = artifacts.list_by_type(ArtifactType.USER_STORY)
approved = artifacts.list_by_status(ArtifactStatus.APPROVED)
history = artifacts.get_version_history("story-1")
```

---

## 🚀 Knowledge Fabric Service

Central service that orchestrates everything.

```python
from app.knowledge import KnowledgeFabric

fabric = KnowledgeFabric()

# Memory APIs
fabric.store_conversation("conv-1", "user", "Add login feature", agent_name="rte")
fabric.store_agent_memory("rte", "recent_tasks", [...])
fabric.create_session("session-1", "user-1")

# Graph APIs
fabric.add_entity("user-1", "User", {"name": "Alice"})
fabric.add_relationship("user-1", "story-1", "CREATED")
fabric.get_related_entities("user-1", max_depth=2)

# Search APIs
fabric.index_for_search("story-1", "Title", "Description", "Content")
results = fabric.search("login feature", search_type="hybrid", limit=10)

# Artifact APIs
fabric.create_artifact("story-1", "user_story", "Title", "Desc", "alice")
fabric.get_artifact("story-1")
fabric.update_artifact("story-1", "new content", "alice")

# Stats
stats = fabric.get_stats()
health = fabric.health_check()
```

---

## 📁 Directory Structure

```
app/knowledge/
├── __init__.py                  # Main package exports
├── knowledge_service.py         # Central KnowledgeFabric service
│
├── memory/                      # Memory systems
│   ├── __init__.py
│   ├── conversation.py          # User-agent interactions
│   ├── agent_memory.py          # Agent-specific state
│   ├── session.py               # Session variables
│   └── working.py               # Temporary computation
│
├── graph/                       # Knowledge graph
│   ├── __init__.py
│   ├── networkx_graph.py        # In-memory (default)
│   └── neo4j_graph.py           # Production Neo4j
│
├── vector/                      # Vector storage
│   ├── __init__.py
│   └── vector_store.py          # Embeddings storage
│
├── embeddings/                  # Embedding providers
│   ├── __init__.py
│   └── embeddings.py            # Multiple providers
│
├── search/                      # Search systems
│   ├── __init__.py
│   └── search.py                # Full-text, semantic, hybrid
│
├── artifacts/                   # Artifact storage
│   ├── __init__.py
│   └── artifacts.py             # Versioning & relationships
│
└── models/                      # Reserved for data models
    └── __init__.py
```

---

## 🔄 Usage Patterns

### Pattern 1: Store and Retrieve Conversation

```python
fabric = KnowledgeFabric()

# User sends message
fabric.store_conversation(
    conversation_id="conv-1",
    role="user",
    content="Add login feature",
    agent_name="rte"
)

# Agent processes and responds
fabric.store_conversation(
    conversation_id="conv-1",
    role="assistant",
    content="User Story: As a user, I want to log in...",
    agent_name="rte"
)
```

### Pattern 2: Build Knowledge Graph

```python
# Add entities
fabric.add_entity("user-1", "User", {"name": "Alice"})
fabric.add_entity("story-1", "UserStory", {"title": "Login"})
fabric.add_entity("epic-1", "Epic", {"title": "Authentication"})

# Add relationships
fabric.add_relationship("user-1", "story-1", "CREATED")
fabric.add_relationship("story-1", "epic-1", "PART_OF")

# Query relationships
related = fabric.get_related_entities("epic-1", max_depth=2)
```

### Pattern 3: Search Knowledge Base

```python
# Index documents
fabric.index_for_search("story-1", "Login", "User authentication", "...")
fabric.index_for_search("story-2", "Signup", "User registration", "...")

# Search
results = fabric.search("authentication", search_type="hybrid", limit=10)
for result in results:
    print(f"{result['title']}: {result['score']:.2f}")
```

### Pattern 4: Track Artifacts

```python
# Create
fabric.create_artifact("story-1", "user_story", "Login", "...", "alice")

# Update
fabric.update_artifact("story-1", "Updated content", "bob", "Fixed typos")

# Track relationships
fabric.create_artifact("design-1", "design", "Login Flow", "...", "alice")
artifact = fabric.get_artifact("story-1")
artifact["related_artifacts"].append("design-1")
```

---

## 🛠️ Configuration

### In-Memory (V1)
```python
fabric = KnowledgeFabric()
# Uses all in-memory storage
# Fast, limited to single machine
```

### With Custom Embeddings
```python
from app.knowledge import SentenceTransformersEmbedding, KnowledgeFabric

embedder = SentenceTransformersEmbedding("all-mpnet-base-v2")
fabric = KnowledgeFabric(embedding_provider=embedder)
```

### Neo4j Graph (Production)
```python
from neo4j import GraphDatabase
from app.knowledge import Neo4jGraph

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
graph = Neo4jGraph(driver)
# Use with fabric (future version)
```

---

## 📊 Scalability Roadmap

### V1 (Current)
- ✅ In-memory storage
- ✅ NetworkX graph
- ✅ Sentence Transformers embeddings
- ✅ Full-text + semantic search

### V2
- [ ] Redis caching
- [ ] PostgreSQL persistence
- [ ] Qdrant vector store
- [ ] Multi-node graph

### V3+
- [ ] Distributed graph (Neo4j)
- [ ] Enterprise embeddings (OpenAI, Cohere)
- [ ] Advanced RAG with fine-tuning
- [ ] Knowledge extraction & inference
- [ ] Multi-tenant support

---

## 🔌 Integration Examples

### With Agents
```python
class MyAgent(BaseAgent):
    def __init__(self, knowledge_fabric):
        self.fabric = knowledge_fabric
    
    async def execute(self, task):
        # Search knowledge base
        results = self.fabric.search(task.description, limit=5)
        
        # Store result
        self.fabric.create_artifact(
            artifact_id=f"result-{task.id}",
            artifact_type="code",
            title="Generated Code",
            description="...",
            created_by=self.name,
            content=result.content
        )
```

### With API
```python
@router.post("/search")
async def search_knowledge(query: str, limit: int = 10):
    results = fabric.search(query, search_type="hybrid", limit=limit)
    return {"results": results}

@router.get("/stats")
async def get_knowledge_stats():
    return fabric.get_stats()
```

---

## 📚 API Reference

### Memory APIs
- `store_conversation()` - Store message
- `retrieve_agent_memory()` - Get agent state
- `create_session()` - Start session
- `set_working_memory()` - Store temporary data

### Graph APIs
- `add_entity()` - Add node
- `add_relationship()` - Add edge
- `get_related_entities()` - Query relationships
- `find_path()` - Shortest path

### Search APIs
- `index_for_search()` - Index document
- `search()` - Query (hybrid/full-text/semantic)

### Artifact APIs
- `create_artifact()` - Create new artifact
- `get_artifact()` - Retrieve artifact
- `update_artifact()` - Update with versioning
- `list_by_type/status/tag()` - Query artifacts

### Utility APIs
- `get_stats()` - System statistics
- `health_check()` - System health

---

## 🎓 Learning Path

1. **Start** - Use `ConversationMemory` and `ArtifactStore`
2. **Explore** - Add entities to the graph
3. **Search** - Index and search documents
4. **Scale** - Add Neo4j or Qdrant for production

---

**Knowledge Fabric: The Intelligence Layer of Korame** 🧠

Built with extensibility, scalability, and enterprise production in mind.

