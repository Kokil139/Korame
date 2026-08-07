# KORAME - Quick Reference Guide

> 📌 **This describes the long-term target architecture** (event bus,
> Postgres/Neo4j/ChromaDB, 8 agents, Ollama↔Azure GPU routing). It has not
> been built yet. For what's actually implemented and running today
> ("Phase 1" — RTE/Developer/Testing agents, direct method calls, in-memory
> storage, single local Ollama model), see [BUILD-SUMMARY.md](BUILD-SUMMARY.md).

## Key Principles (Remember These!)

1. **Workflow Orchestrator is the execution engine** - Central control, all communication through events
2. **RTE is the business owner** - Final approval authority, manages releases
3. **Agents communicate through events** - Never direct calls; async, auditable, scalable
4. **Artifacts move through defined states** - NEW → PLANNED → ARCHITECTED → IN_DEVELOPMENT → CODE_REVIEW → SECURITY_SCAN → AUTOMATED_TESTING → READY_FOR_UAT → UAT → READY_FOR_DEPLOYMENT → DEPLOYED → COMPLETED
5. **Failed gates always loop to Developer** - No skipping; Developer must fix and resubmit
6. **Only validated artifacts reach UAT** - Protects UAT team; ensures engineering quality
7. **Only UAT-approved artifacts reach DevOps** - Production confidence; audit trail

## Core Architecture

```
RTE → Workflow Orchestrator → Agents (via Events) → Quality Gates → UAT → DevOps → Production
         ↓
    Knowledge Fabric (PostgreSQL, Neo4j, ChromaDB, Git)
    Event Bus (Redis)
    Model Router (Ollama → Azure GPU)
```

## Agent Responsibilities Matrix

| Agent | Can Approve Own Work? | Can Block? | Primary Task |
|-------|----------------------|-----------|--------------|
| RTE | Yes | - | Requirements, release decisions |
| Architect | No | No | Solution design |
| Developer | No | No | Implementation |
| Reviewer | No | Yes | Code quality |
| Security | No | Yes | Vulnerability scanning |
| Testing | No | Yes | Test coverage |
| UAT | No | Yes | Business acceptance |
| DevOps | Yes | No | Deployment |

## State Transitions Quick Rules

| From State | To State | Gate Required | Can Fail? |
|-----------|----------|--------------|-----------|
| NEW | PLANNED | None | No |
| PLANNED | ARCHITECTED | None | No |
| ARCHITECTED | IN_DEVELOPMENT | None | No |
| IN_DEVELOPMENT | CODE_REVIEW | None | - |
| CODE_REVIEW | SECURITY_SCAN | ✓ Approved | Yes → loops back |
| SECURITY_SCAN | AUTOMATED_TESTING | ✓ Passed | Yes → loops back |
| AUTOMATED_TESTING | READY_FOR_UAT | ✓ Coverage ≥ 80% | Yes → loops back |
| READY_FOR_UAT | UAT | None | - |
| UAT | READY_FOR_DEPLOYMENT | ✓ Passed | Yes → full loop back |
| READY_FOR_DEPLOYMENT | DEPLOYED | None | - |
| DEPLOYED | COMPLETED | None | - |

**Key Rule:** UAT failure → artifact returns to IN_DEVELOPMENT + mandatory re-run of ALL engineering gates (Code Review → Security → Testing)

## Knowledge Fabric Storage

| Information Type | Storage | Query Method |
|-----------------|---------|--------------|
| Requirements, artifacts, state | PostgreSQL | SQL queries |
| Relationships, decisions, impact | Neo4j | Graph traversal |
| Vector embeddings, semantic search | ChromaDB | Vector similarity |
| Source code, commit history | Git | Git queries |
| Files, logs, raw data | Filesystem/Blob | File I/O |

## Model Router Rules

| Task Complexity | Preferred Model | Location | Use Case |
|-----------------|-----------------|----------|----------|
| Simple (< 500 tokens) | Qwen3 8B | Local | Requirement analysis, planning |
| Medium (500-2K tokens) | Llama2 13B | Local/Azure | Architecture, code review |
| Complex (> 2K tokens) | GPT-4-32K | Azure | Complex reasoning, design |
| Code generation | Code Llama 7B | Local/Azure | Implementation |
| Security review | Claude 3 | Azure | Reasoning, compliance |
| Testing | Grok-1 | Azure | Complex test strategy |

## Event Flow Example: Story to Code

```
1. RTE creates story → Event: story.created
2. Orchestrator: NEW → PLANNED
3. Architect invoked → Event: task.architecture.ready
4. Design ready → Event: task.architecture.completed
5. Orchestrator: PLANNED → ARCHITECTED
6. Developer invoked → Event: task.code_generation.ready
7. Code ready → Event: task.code_generation.completed
8. Orchestrator: ARCHITECTED → IN_DEVELOPMENT → CODE_REVIEW
9. Code Reviewer invoked → Event: task.code_review.ready
10. Review result:
    - PASS: Event: gate.code_review.passed → move to SECURITY_SCAN
    - FAIL: Event: gate.code_review.failed → loop back to IN_DEVELOPMENT
11-15. (Security gate process similar)
16-20. (Testing gate process similar)
21. All gates passed → READY_FOR_UAT
22. UAT invoked → Event: task.uat.ready
23. UAT result:
    - PASS: Event: gate.uat.passed → READY_FOR_DEPLOYMENT
    - FAIL: Event: gate.uat.failed → loop back to IN_DEVELOPMENT (full loop)
24. DevOps invoked → Event: task.deployment.ready
25. Deployment complete → Event: task.deployment.completed
26. Orchestrator: DEPLOYED → COMPLETED
```

## API Quick Reference

### Create Artifact
```bash
curl -X POST http://localhost:8000/api/v1/artifacts \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "UserStory",
    "title": "...",
    "description": "...",
    "acceptance_criteria": [...]
  }'
```

### Get Artifact State
```bash
curl http://localhost:8000/api/v1/artifacts/story-123/state \
  -H "Authorization: Bearer <token>"
```

### Search Knowledge Fabric
```bash
curl "http://localhost:8000/api/v1/knowledge/search?q=jwt+validation&type=code&limit=5" \
  -H "Authorization: Bearer <token>"
```

### Get Metrics
```bash
curl "http://localhost:8000/api/v1/metrics/pipeline?timerange=7d" \
  -H "Authorization: Bearer <token>"
```

## Docker Compose Quick Start

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f korame

# Stop all services
docker-compose down

# Reset databases
docker-compose down -v && docker-compose up -d
```

## Development Environment Setup

```bash
# Clone repository
git clone <korame-repo>
cd korame

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Start Docker services
docker-compose up -d

# Run tests
pytest tests/ -v

# Start development server
python -m uvicorn korame.api.main:app --reload
```

## Troubleshooting Guide

### Artifact Stuck in State
- Check Event Bus: `redis-cli LLEN audit_log:<artifact_id>`
- View audit log: `GET /api/v1/artifacts/<artifact_id>/audit`
- Look for hung agents: `docker-compose logs korame | grep ERROR`

### Agent Not Processing Tasks
- Verify event subscription: `redis-cli PUBSUB CHANNELS`
- Check agent logs: `docker-compose logs <agent_container>`
- Restart agent: `docker-compose restart <agent_container>`

### High Latency
- Check Model Router selection: Add logging to model selection
- Monitor GPU usage: `nvidia-smi` (if using local GPU)
- Check Event Bus depth: `redis-cli DBSIZE`

### Security Gate Always Failing
- Check if using premium model (may be too strict): Adjust config
- Review findings: `GET /api/v1/artifacts/<artifact_id>/gates/security`
- Whitelist false positives: Update security agent config

## Configuration Hierarchy

```
1. Environment variables (highest priority)
2. .env file
3. config/local.yaml (development)
4. config/docker.yaml (Docker)
5. config/azure.yaml (production)
6. Agent-specific config in config/agents/*.yaml
7. Built-in defaults (lowest priority)
```

## Deployment Checklist

- [ ] All dependencies updated and tested
- [ ] No critical CVEs in dependencies
- [ ] Code coverage ≥ 80%
- [ ] All ADRs updated
- [ ] API documentation generated
- [ ] Monitoring alerts configured
- [ ] Backup strategy verified
- [ ] Disaster recovery plan tested
- [ ] Security audit passed
- [ ] Performance load tests passed

## Success Metrics Dashboard

**Key Metrics to Monitor:**
- Artifact pipeline throughput (artifacts/day)
- Average time to completion (hours)
- Gate pass rates (% passing by gate type)
- Agent success rate (% successful executions)
- System uptime (%)
- Model inference latency (ms)

**Target Values:**
- Throughput: 100+ artifacts/month
- Time to completion: < 1 hour average
- Code Review pass: > 95%
- Security pass: > 98%
- Testing pass: > 92%
- UAT pass: > 88%
- System uptime: > 99.5%

## Contact & Support

- **Architecture Questions:** Architecture team
- **Implementation Issues:** Development team
- **Deployment/DevOps:** DevOps team
- **Security Issues:** Security team
- **General:** Open GitHub issue in repository

---

**Last Updated:** July 25, 2026  
**Document Version:** 1.0 (Foundation Phase)

