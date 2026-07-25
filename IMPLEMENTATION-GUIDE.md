# KORAME Implementation Guide

## Getting Started with Korame Development

This guide helps new developers understand and contribute to Korame. Start here if you're joining the team.

---

## Part 1: Understanding Korame

### The 5-Minute Overview

Korame is an AI-native software factory composed of:

1. **RTE Agent** - Your business representative; creates requirements
2. **Architect Agent** - Designs solutions 
3. **Developer Agent** - Writes code
4. **Reviewer/Security/Testing Agents** - Quality gates
5. **UAT Agent** - Business validation
6. **DevOps Agent** - Deployment

All agents communicate via **Event Bus** (Redis). The **Workflow Orchestrator** coordinates everything.

**Your job:** Implement agents that:
- Take input (artifact + context)
- Do their work (using LLMs)
- Emit events (success/failure)
- Never call other agents directly

### The Core Loop

```
1. RTE creates requirement
   ↓
2. Architect designs it
   ↓
3. Developer implements it
   ↓
4. Reviewer checks code quality
   ↓
5. Security scans for vulnerabilities
   ↓
6. Tester generates/runs tests
   ↓
7. If any gate fails → Developer fixes → Back to step 4
   ↓
8. If all pass → UAT validates business requirements
   ↓
9. If UAT fails → Developer fixes → Back to step 4
   ↓
10. If UAT passes → DevOps deploys
```

**Key Rule:** No gate can be skipped. Failures go back to Developer.

---

## Part 2: Development Environment Setup

### Prerequisites

- Python 3.11+
- Docker + Docker Compose
- Git
- Text editor (VS Code, JetBrains, etc.)
- Redis CLI (optional, for debugging)

### Initial Setup

```bash
# 1. Clone the repository
git clone <korame-repo>
cd korame

# 2. Create Python virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements-dev.txt

# 4. Start Docker services
docker-compose up -d

# 5. Verify setup
python -m pytest tests/ -v

# 6. Check all services are running
docker-compose ps
```

### Services Verification

```bash
# Check if Redis is running
redis-cli ping  # Should return "PONG"

# Check if PostgreSQL is running
psql -h localhost -U postgres -d korame -c "SELECT version();"

# Check if API is running
curl http://localhost:8000/health  # Should return {"status": "ok"}
```

---

## Part 3: Project Structure Guide

```
korame/
├── src/korame/              # Main source code
│   ├── kernel/              # Core orchestrator, event bus, config
│   ├── agents/              # All agent implementations
│   ├── sdk/                 # Agent SDK (what agents use)
│   ├── knowledge/           # Knowledge Fabric
│   ├── models/              # Model Router and LLM providers
│   ├── api/                 # FastAPI endpoints
│   ├── observability/       # Logging, metrics, tracing
│   └── utils/               # Helper utilities
│
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── fixtures/            # Test data
│
├── config/                  # Configuration files
│   ├── local.yaml           # Development (use this)
│   ├── docker.yaml          # Docker environment
│   └── agents/              # Agent-specific configs
│
├── docs/                    # Documentation
│   ├── KORAME-SAS.md        # THIS IS THE SPEC (single source of truth)
│   ├── QUICK-REFERENCE.md   # Quick lookup
│   └── ADRs/                # Architecture decisions
│
└── docker-compose.yml       # Local development setup
```

### Key Files to Understand

1. **KORAME-SAS.md** - The official specification. **Everything** should trace back to this.
2. **config/local.yaml** - Your development configuration
3. **src/korame/sdk/agent.py** - Base class for all agents; study this
4. **src/korame/kernel/orchestrator.py** - The heart of Korame
5. **tests/integration/test_artifact_lifecycle.py** - Example of complete flow

---

## Part 4: Before You Start Coding

### Read These First

1. **KORAME-SAS.md** - Section 1 (Vision), Section 4 (High-Level Architecture), Section 8 (Agent Framework)
2. **QUICK-REFERENCE.md** - Especially the "Principles" and "State Transitions" sections
3. **docs-ADRs.md** - ADR-001 (Event-Driven) and ADR-005 (Quality Gates Cannot Be Skipped)

### Understand the Mental Model

**MOST IMPORTANT:** Think in terms of **events**, not function calls.

❌ WRONG:
```python
# DON'T DO THIS
code_reviewer = CodeReviewerAgent()
result = code_reviewer.review_code(artifact)  # Direct call
```

✅ RIGHT:
```python
# DO THIS
event_bus.publish(Event(
    event_type="task.code_review.ready",
    artifact_id=artifact.id,
    payload={"code": artifact.content}
))

# Code Reviewer Agent listens for this event separately
class CodeReviewerAgent:
    def __init__(self):
        event_bus.subscribe("task.code_review.ready", self.handle_review_task)
    
    def handle_review_task(self, event):
        # Review the code
        result = self.review(event.payload["code"])
        # Publish result event
        event_bus.publish(Event(type="gate.code_review.passed", ...))
```

---

## Part 5: Implementing Your First Agent

### Agent Skeleton

```python
# src/korame/agents/my_first_agent.py

from korame.sdk import Agent, EventBus, KnowledgeFabric
from korame.events import Event

class MyFirstAgent(Agent):
    """
    Description of what this agent does.
    
    Responsibilities:
    - Input: artifact of type X
    - Output: artifact of type Y
    """
    
    def __init__(self, config):
        self.name = "my-first-agent"
        self.event_bus = EventBus(config.redis_url)
        self.knowledge_fabric = KnowledgeFabric(config.db_urls)
        
    def initialize(self):
        """Called on startup; subscribe to events"""
        self.event_bus.subscribe(
            listener_id=self.name,
            topics=["task.my_task_type.ready"]
        )
        print(f"{self.name} initialized and listening")
    
    def can_handle(self, event: Event) -> bool:
        """Check if this agent should handle this event"""
        return event.event_type == "task.my_task_type.ready"
    
    def execute(self, artifact, context, config):
        """Main agent logic"""
        
        print(f"Starting work on {artifact.id}")
        
        # Step 1: Get additional context from Knowledge Fabric if needed
        related_artifacts = self.knowledge_fabric.search(
            query=artifact.title,
            context_type="similar",
            max_results=3
        )
        
        # Step 2: Do the work (use model, process, analyze, etc.)
        result = self.do_work(artifact, context, related_artifacts)
        
        # Step 3: Validate result
        if not self.validate_result(result):
            raise ValueError("Result validation failed")
        
        # Step 4: Return result
        return result
    
    def do_work(self, artifact, context, examples):
        """Your actual agent logic here"""
        # Example: Generate something, analyze something, validate something
        return "result"
    
    def validate_result(self, result):
        """Ensure result meets requirements"""
        return True
```

### Test Your Agent

```python
# tests/unit/test_my_first_agent.py

import pytest
from korame.agents.my_first_agent import MyFirstAgent
from korame.events import Event

@pytest.fixture
def agent():
    config = load_test_config()
    agent = MyFirstAgent(config)
    agent.initialize()
    return agent

def test_agent_can_handle_event(agent):
    """Agent recognizes relevant events"""
    event = Event(event_type="task.my_task_type.ready")
    assert agent.can_handle(event)

def test_agent_executes(agent):
    """Agent successfully executes task"""
    artifact = create_test_artifact()
    context = create_test_context()
    result = agent.execute(artifact, context, {})
    assert result is not None

def test_agent_validates_input(agent):
    """Agent rejects invalid input"""
    with pytest.raises(ValueError):
        invalid_artifact = create_invalid_artifact()
        agent.execute(invalid_artifact, {}, {})
```

---

## Part 6: Common Patterns

### Pattern 1: Using the Model Router

```python
def my_agent_execute(self, artifact, context, config):
    # Don't specify which model; let Model Router choose
    result = self.model_router.invoke(
        task_type="code_generation",
        prompt=build_prompt(artifact, context),
        max_tokens=2000
    )
    return result
```

### Pattern 2: Querying Knowledge Fabric

```python
# Search for similar artifacts
similar = self.knowledge_fabric.search(
    query="JWT authentication",
    context_type="code",
    max_results=5
)

# Get artifact history
history = self.knowledge_fabric.get_artifact_history("story-123")

# Traverse relationships
dependencies = self.knowledge_fabric.graph_traverse(
    start_node="story-123",
    relationship_types=["DEPENDS_ON"],
    max_depth=2
)
```

### Pattern 3: Publishing Events

```python
# Publish success
self.event_bus.publish(Event(
    event_type="task.my_task.completed",
    artifact_id=artifact.id,
    source_agent=self.name,
    payload={"result": result, "duration_ms": elapsed_ms}
))

# Publish failure with findings
self.event_bus.publish(Event(
    event_type="gate.my_gate.failed",
    artifact_id=artifact.id,
    source_agent=self.name,
    payload={
        "findings": [
            {"severity": "ERROR", "message": "...", "location": "..."}
        ]
    }
))
```

### Pattern 4: Structured Logging

```python
self.logger.info(
    "Artifact processed",
    extra={
        "artifact_id": artifact.id,
        "gate": "code_review",
        "status": "passed",
        "duration_ms": 1234,
        "correlation_id": get_correlation_id()
    }
)
```

---

## Part 7: Testing Your Code

### Unit Tests

Focus on agent logic in isolation:

```bash
# Run unit tests
pytest tests/unit/ -v

# Run specific test
pytest tests/unit/test_my_agent.py::test_can_handle_event -v

# Run with coverage
pytest tests/unit/ --cov=korame.agents --cov-report=html
```

### Integration Tests

Test the complete flow:

```bash
# Run integration tests (requires Docker services running)
pytest tests/integration/ -v

# Example: full artifact lifecycle
pytest tests/integration/test_artifact_lifecycle.py -v
```

### Manual Testing

```bash
# 1. Create a test artifact via API
curl -X POST http://localhost:8000/api/v1/artifacts \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "UserStory",
    "title": "Test story",
    "description": "Test",
    "acceptance_criteria": ["Test criteria"]
  }'

# Response includes artifact ID, e.g., "story-123"

# 2. Watch the state transitions
curl http://localhost:8000/api/v1/artifacts/story-123/state \
  -H "Authorization: Bearer test-token"

# 3. Check audit log
curl http://localhost:8000/api/v1/artifacts/story-123/audit \
  -H "Authorization: Bearer test-token"

# 4. View in logs
docker-compose logs -f korame
```

---

## Part 8: Debugging Guide

### View Event Bus Activity

```bash
# Connect to Redis
redis-cli

# Monitor all pub/sub activity
SUBSCRIBE "*"

# Check event queue for specific artifact
LRANGE audit_log:story-123 0 -1

# View event count
DBSIZE
```

### Check Service Logs

```bash
# Orchestrator logs
docker-compose logs korame

# Follow logs (live)
docker-compose logs -f korame

# Logs for specific agent (once implemented)
docker-compose logs developer-agent
```

### Inspect Database State

```bash
# Connect to PostgreSQL
psql -h localhost -U postgres -d korame

# View artifacts
SELECT id, status, created_at FROM artifacts ORDER BY created_at DESC;

# View state transitions
SELECT * FROM state_transitions WHERE artifact_id = 'story-123';

# View gate results
SELECT * FROM gate_results WHERE artifact_id = 'story-123';
```

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Connection refused" | Docker not running | `docker-compose up -d` |
| Agent not processing events | Agent not subscribed | Check `event_bus.subscribe()` call |
| Stuck in state | Event routing issue | Check orchestrator logs; review event payload |
| Token limit exceeded | Context too large | Reduce examples; use summary instead of full text |
| Slow inference | Using wrong model | Check Model Router selection; may need Azure GPU |
| Artifact lost | Database crash | Check PostgreSQL container; restore from backup |

---

## Part 9: Code Quality & Standards

### Code Style

- **Language:** Python 3.11+
- **Style Guide:** PEP 8 + Black formatter
- **Type Hints:** Required for all functions
- **Docstrings:** Required for classes and public methods

```python
def analyze_code(code: str, rules: List[Rule]) -> List[Finding]:
    """
    Analyze code against style rules.
    
    Args:
        code: Source code to analyze
        rules: List of style rules to check
    
    Returns:
        List of findings (violations found)
    
    Raises:
        ValueError: If code is empty
    """
    if not code:
        raise ValueError("Code cannot be empty")
    
    findings = []
    for rule in rules:
        if violation := rule.check(code):
            findings.append(violation)
    
    return findings
```

### Testing Requirements

- **Minimum Coverage:** 80%
- **All public methods:** Must have tests
- **Integration tests:** For agent interactions

```bash
# Check coverage
pytest --cov=korame --cov-report=term-missing
```

### Pre-commit Hooks

Before committing code:

```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/

# Run tests
pytest tests/ -v
```

### Documentation

- Add docstrings to all functions
- Update ADRs for architectural changes
- Update SAS if changing core architecture
- Document new configuration options

---

## Part 10: Deployment to Production

### Before Merging to Main

1. ✓ All tests pass (pytest)
2. ✓ Code coverage ≥ 80%
3. ✓ No type errors (mypy)
4. ✓ No linting issues (flake8, black)
5. ✓ No new CVEs (pip-audit)
6. ✓ Documentation updated
7. ✓ ADRs updated (if applicable)

### Release Process

```bash
# 1. Update version
# Edit: src/korame/__init__.py
__version__ = "1.0.0"

# 2. Create release notes
# docs/RELEASE-NOTES-1.0.0.md

# 3. Tag release
git tag -a v1.0.0 -m "Release 1.0.0: Korame Kernel"
git push origin v1.0.0

# 4. Build Docker image
docker build -t korame:1.0.0 .

# 5. Push to registry
docker push myregistry.azurecr.io/korame:1.0.0

# 6. Deploy to AKS
kubectl apply -f k8s/korame-deployment.yaml
```

---

## Part 11: Getting Help

### Documentation
- **SAS (Specification):** KORAME-SAS.md
- **Quick Lookup:** QUICK-REFERENCE.md
- **Decisions:** docs-ADRs.md
- **API Docs:** Auto-generated at `http://localhost:8000/docs` (Swagger)

### Channels
- **Architecture Questions:** Create GitHub issue with [ARCHITECTURE] tag
- **Implementation Help:** Code review process
- **Bug Reports:** GitHub issues with [BUG] tag
- **Meetings:** Weekly architecture sync (Thursdays 2pm)

### Learning Resources
- Event-Driven Architecture patterns
- Temporal.io (workflow orchestration inspiration)
- 12 Factor App (cloud-native design)
- Python Async Design (event loops, pub/sub)

---

## Part 12: Making Your First Contribution

### Pick a Task

Start small; build confidence:
1. Fix a typo in documentation
2. Add a unit test
3. Implement a small utility function
4. Implement RTE Agent (simple task)
5. Implement Architect Agent (medium complexity)
6. Implement Developer Agent (complex; coordinate with team)

### The Process

```
1. Create feature branch
   git checkout -b feature/implement-rte-agent
   
2. Implement in small commits
   git commit -m "Add RTE agent skeleton"
   git commit -m "Add requirement parsing"
   git commit -m "Add story generation"
   
3. Write tests as you go
   pytest tests/unit/test_rte_agent.py -v
   
4. Push and create PR
   git push origin feature/implement-rte-agent
   
5. Code review process
   - Address feedback
   - Ensure tests pass
   - Update docs
   
6. Merge and deploy
   Maintainer merges to main; CI/CD handles deployment
```

### PR Checklist

- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Coverage ≥ 80% (`pytest --cov`)
- [ ] No linting issues (`flake8`, `black`, `mypy`)
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No debug print statements or commented code
- [ ] No new CVEs introduced

---

## Quick Command Reference

```bash
# Development
docker-compose up -d        # Start services
docker-compose logs -f      # View logs
pytest tests/ -v           # Run tests
black src/ tests/          # Format code
flake8 src/ tests/         # Lint check
mypy src/                  # Type check

# Testing
pytest tests/unit/ -v                    # Unit tests only
pytest tests/integration/ -v             # Integration tests
pytest tests/ --cov=korame --cov-report=html  # Coverage report

# Debugging
redis-cli                  # Redis client
psql -h localhost -U postgres -d korame  # PostgreSQL client
docker-compose ps         # View container status
docker-compose restart    # Restart services

# Deployment
docker build -t korame:latest .
docker push registry.azurecr.io/korame:latest
kubectl apply -f k8s/
```

---

## Next Steps

1. **Read KORAME-SAS.md** (Sections 1-5)
2. **Clone the repository** and run setup
3. **Study the Agent SDK** (`src/korame/sdk/agent.py`)
4. **Implement a simple agent** (RTE Agent is a good start)
5. **Write tests** for your agent
6. **Submit PR** for review
7. **Learn from feedback** and iterate

---

**Good luck! Welcome to the Korame team. 🚀**

*Last Updated: July 25, 2026*

