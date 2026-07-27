# Contributing to Korame V1

Welcome! This guide will help you contribute to Korame.

## Getting Started

### 1. Clone and Setup

```bash
git clone <korame-repo>
cd korame
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

### 2. Start Ollama

```bash
ollama serve
# In another terminal:
ollama pull qwen2:7b
```

### 3. Run Tests

```bash
pytest tests/ -v
```

### 4. Start the Server

```bash
uvicorn app.main:app --reload
```

## What to Contribute

### Good for Beginners

1. **Add documentation**
   - Fix typos
   - Expand examples
   - Add comments

2. **Add tests**
   - Test edge cases
   - Test error handling
   - Improve coverage

3. **Add prompts**
   - Create prompts for new agents
   - Improve existing prompts
   - Test prompt variations

4. **Fix bugs**
   - Report issues you find
   - Submit fixes with tests

### Good for Intermediate

1. **Implement new agents**
   - Architect Agent
   - Developer Agent
   - Reviewer Agent

2. **Add providers**
   - OpenAI provider
   - Claude provider
   - vLLM provider

3. **Improve routing**
   - Task complexity detection
   - Model selection based on task type
   - Performance optimizations

### Good for Advanced

1. **Infrastructure**
   - Add Redis support
   - Add PostgreSQL support
   - Docker setup

2. **Features**
   - Agent chaining
   - Memory optimization
   - Caching layer

3. **Architecture**
   - Design plugins system
   - Event bus implementation
   - Distributed execution

## Development Process

### 1. Create Feature Branch

```bash
git checkout -b feature/describe-feature
```

Name format: `feature/`, `fix/`, `docs/`, `test/`

### 2. Make Changes

- Write tests first
- Implement feature
- Keep commits small and focused

### 3. Code Quality

```bash
# Format
black app/ tests/

# Lint
flake8 app/ tests/

# Type check
mypy app/

# Test
pytest tests/ -v --cov=app

# All together
bash scripts/quality-check.sh
```

### 4. Commit Message

```
Short description (50 chars)

Longer explanation if needed.
Explain *why*, not just *what*.

Fixes #123
```

### 5. Push and Create PR

```bash
git push origin feature/describe-feature
```

Go to GitHub and create a Pull Request.

### 6. Code Review

- Address feedback
- Push fixes
- Request re-review

### 7. Merge

Maintainer merges to `main`.

## Project Structure

Before contributing, understand:

```
korame/
├── app/kernel/          ← Stable interfaces
├── app/agents/          ← Agent implementations
├── app/providers/       ← Model providers
├── app/workflow/        ← Orchestration
├── app/api/             ← REST endpoints
├── tests/               ← Test suite
└── docs/                ← Documentation
```

**Key Rule:** Agents depend on kernel, not on each other.

## Coding Standards

### Style

- **Language:** Python 3.12+
- **Formatter:** Black
- **Linter:** Flake8
- **Type Checking:** MyPy

### Naming Conventions

- **Classes:** `PascalCase` (e.g., `RTEAgent`, `OllamaProvider`)
- **Functions:** `snake_case` (e.g., `execute_task`, `get_agent`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- **Private:** `_leading_underscore` (e.g., `_internal_method`)

### Docstrings

```python
def my_function(arg1: str, arg2: int) -> dict[str, Any]:
    """
    Brief description.
    
    Longer description if needed.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When something is invalid
    """
    pass
```

### Type Hints

Required for all functions:

```python
def process(data: dict[str, Any], timeout: int = 30) -> Response:
    pass
```

### Imports

```python
# Standard library
import os
from typing import Optional

# Third-party
import httpx
from pydantic import BaseModel

# Local
from app.kernel import Task, Response
from app.agents.base import BaseAgent
```

## Testing

### Unit Tests

Test single components in isolation:

```python
def test_agent_initialization(registry):
    """Test agent can be registered."""
    agent = MyAgent("test")
    registry.register_agent(agent)
    assert registry.has_agent("test")
```

### Integration Tests

Test components working together:

```python
@pytest.mark.asyncio
async def test_workflow_execution(workflow_engine, registry):
    """Test complete workflow."""
    agent = TestAgent("test")
    registry.register_agent(agent)
    response = await workflow_engine.execute("test", {})
    assert response.status == "success"
```

### Fixtures

Use `conftest.py` for shared fixtures:

```python
@pytest.fixture
def registry():
    return Registry()
```

### Coverage

Aim for >80% coverage:

```bash
pytest tests/ --cov=app --cov-report=html
```

## Common Tasks

### Add a New Agent

1. Create `app/agents/myagent/agent.py`
2. Inherit from `BaseAgent`
3. Implement `execute(task: Task) -> Response`
4. Add prompt to `app/prompts/myagent.md`
5. Add tests to `tests/test_myagent.py`
6. Register in `app/main.py`

### Add a New Provider

1. Create `app/providers/myprovider.py`
2. Inherit from `Provider`
3. Implement `call(prompt: str, **kwargs) -> str`
4. Add to `app/providers/__init__.py`
5. Register in `app/main.py`
6. Update router (optional)

### Add a New Endpoint

1. Add to `app/api/chat.py`
2. Use `router.get()` or `router.post()`
3. Add request/response models
4. Use `workflow_engine` and `conversation_memory`
5. Add tests to `tests/test_api.py`

### Update Documentation

1. Modify relevant `.md` file in `docs/`
2. Update architecture diagrams if needed
3. Include examples
4. Test examples if code

## Questions?

- **GitHub Issues** - Bug reports, feature requests
- **GitHub Discussions** - Questions, ideas
- **Email** - contact@korame.dev

## Code of Conduct

- Be respectful
- Be inclusive
- Assume good intent
- Address conflicts privately

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Korame!** 🚀


