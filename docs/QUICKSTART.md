# Korame V1 Quick Start

Get Korame V1 running in 5 minutes.

## Prerequisites

- Python 3.12+
- Ollama running locally
- Git

## Step 1: Clone and Setup (2 minutes)

```bash
# Clone
git clone <korame-repo>
cd korame

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

## Step 2: Start Ollama (1 minute)

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Pull a model (one-time)
ollama pull qwen2:7b
```

## Step 3: Start Korame (1 minute)

```bash
# Terminal 3: Start Korame
uvicorn app.main:app --reload
```

Visit: http://localhost:8000/docs

## Step 4: Test the API (1 minute)

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Generate a user story
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "rte",
    "requirement": "Users should be able to upload CSV files and preview them"
  }'
```

## What You Can Do Now

### Generate User Stories
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "rte",
    "requirement": "Your requirement here"
  }'
```

### Check Conversation History
```bash
# Get your conversation ID from the previous response
curl http://localhost:8000/api/v1/conversations/{conversation_id}
```

### API Documentation
Open http://localhost:8000/docs for interactive API docs

## Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_kernel.py -v

# With coverage
pytest tests/ --cov=app
```

## Code Quality

```bash
# Format code
black app/ tests/

# Check style
flake8 app/ tests/

# Type checking
mypy app/

# All checks (Windows)
python scripts/setup.py

# All checks (Mac/Linux)
bash scripts/quality-check.sh
```

## Project Structure

```
korame/
├── app/
│   ├── kernel/          # Core interfaces
│   ├── agents/          # Agent implementations (RTE)
│   ├── providers/       # Model providers (Ollama)
│   ├── router/          # Task routing
│   ├── workflow/        # Orchestration
│   ├── memory/          # Conversation storage
│   ├── api/             # REST endpoints
│   ├── config/          # Configuration
│   ├── prompts/         # Agent prompts
│   ├── utils/           # Utilities
│   └── main.py          # FastAPI app
├── tests/               # Test suite
├── docs/                # Documentation
└── scripts/             # Helper scripts
```

## Common Commands

| Command | Purpose |
|---------|---------|
| `uvicorn app.main:app --reload` | Start server (dev) |
| `pytest tests/ -v` | Run tests |
| `black app/ tests/` | Format code |
| `flake8 app/ tests/` | Check style |
| `mypy app/` | Type check |

## Next Steps

1. **Explore the API** - Try different requirements
2. **Read the docs** - Check `docs/ARCHITECTURE.md`
3. **Run tests** - Understand the test suite
4. **Add an agent** - Implement Architect Agent
5. **Add a provider** - Integrate OpenAI or Claude

## Troubleshooting

### "Connection refused" on Ollama
- Make sure Ollama is running: `ollama serve`
- Check it's on localhost:11434
- Try: `curl http://localhost:11434/api/tags`

### "No module named 'app'"
- Make sure you're in the project root
- Make sure venv is activated
- Reinstall: `pip install -e .`

### Tests fail
- Make sure Ollama is running
- Check: `pytest tests/test_kernel.py -v` (no Ollama needed)
- Check: `pytest tests/test_workflow.py -v` (needs Ollama)

### Model not found
- Pull it: `ollama pull qwen2:7b`
- Change `.env`: `OLLAMA_MODEL=<model-name>`

## Documentation

- **Architecture** - `docs/ARCHITECTURE.md`
- **Contributing** - `docs/CONTRIBUTING.md`
- **API** - http://localhost:8000/docs (when running)

## Support

- **Issues** - GitHub Issues
- **Discussions** - GitHub Discussions
- **Email** - contact@korame.dev

---

**You're all set! Happy coding! 🚀**

For detailed information, see `docs/ARCHITECTURE.md`

