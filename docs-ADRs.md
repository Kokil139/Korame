# Architecture Decision Records (ADRs)

ADRs document important architectural decisions, including the context, decision, and consequences. These form the historical record of technical choices and their rationale.

## ADR Template

```markdown
# ADR-XXX: [Decision Title]

## Status
[PROPOSED | ACCEPTED | DEPRECATED | SUPERSEDED BY ADR-YYY]

## Context
[Describe the issue or problem that necessitates this decision. Include relevant background, constraints, and alternatives considered.]

## Decision
[Clearly state the architectural decision made. Use active voice and be specific about what is being decided.]

## Rationale
[Explain why this decision was made. Include benefits, trade-offs, and why alternatives were rejected.]

## Consequences
### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Drawback 1]
- [Drawback 2]

### Neutral
- [Side effect 1]

## Alternatives Considered
1. [Alternative 1] - Why rejected?
2. [Alternative 2] - Why rejected?

## Related Decisions
- ADR-XXX: [Related decision]

## Implementation Notes
[Any specific guidance for implementers, configurations, or gotchas to watch for]

## References
- [Reference 1]
- [Reference 2]

---
**Decided By:** [Name/Team]  
**Date:** [YYYY-MM-DD]  
**Last Updated:** [YYYY-MM-DD]  
**Supersedes:** [ADR-XXX if applicable]
```

---

## ADR-001: Event-Driven Architecture

## Status
ACCEPTED

## Context
Korame needs to coordinate work between multiple independent agents (RTE, Architect, Developer, Reviewer, Security, Testing, UAT, DevOps). Early designs considered:
1. **Direct function calls:** Agent A calls Agent B directly
2. **Synchronous RPC:** Agents communicate via remote procedure calls
3. **Event-driven async:** Agents publish events; orchestrator routes to listeners
4. **Job queue:** Dedicated job server (Celery-like)

Requirements:
- Agents should be independently deployable
- Failures in one agent shouldn't cascade to others
- Full audit trail of all actions
- Support for retries and recovery
- Ability to replay events for debugging
- Scale to 1000+ events/second
- Support parallel execution of independent tasks

## Decision
**Adopt event-driven asynchronous architecture using Redis pub/sub as the event bus.**

Korame uses an event-driven model where:
- Agents never call each other directly
- All inter-agent communication flows through Redis Event Bus
- Workflow Orchestrator listens to events and makes routing decisions
- Events are published to topics like "task.code_review.ready"
- Agents subscribe to relevant topics
- All events are logged for audit trail and replay capability

## Rationale

### Why Event-Driven?
1. **Decoupling:** Agents don't need to know about each other; adds new agents without modifying existing ones
2. **Resilience:** One failed agent doesn't block others; orchestrator handles retries
3. **Scalability:** Event bus can handle async communication at scale
4. **Auditability:** Every action is logged as an event; perfect for compliance
5. **Debuggability:** Can replay events from any point for investigation
6. **Testability:** Can inject mock events to test agent behavior

### Why Redis?
1. **Simplicity:** Minimal operational overhead; runs anywhere (laptop to cloud)
2. **Performance:** Sub-millisecond latency for pub/sub
3. **Ordering:** Can guarantee message ordering within a topic
4. **Features:** Built-in expiration, pattern matching, Lua scripting
5. **Cost:** Free, open-source
6. **Ecosystem:** Excellent monitoring and debugging tools
7. **Migration path:** Easy to upgrade to Redis Cloud or replace with RabbitMQ/Kafka later

### Why Not Alternatives?

**Direct Calls:** Tightly couples agents; can't be independently deployed; single point of failure

**Synchronous RPC:** Requires both parties to be available; harder to handle failures; less scalable

**Job Queue (Celery):** More overhead; overkill for Korame's needs; Redis is simpler alternative

**Message Queue (RabbitMQ):** More complex to operate; more overhead; Redis sufficient for Phase 1-4

## Consequences

### Positive
- ✓ True service independence; agents can restart without affecting others
- ✓ Complete audit trail; every action logged
- ✓ Easy to debug by replaying events
- ✓ Can simulate agent failures and test recovery
- ✓ Can add monitoring and logging without changing agents
- ✓ Supports both synchronous and asynchronous patterns

### Negative
- ✗ Eventual consistency; requires additional complexity for distributed state
- ✗ Harder to trace state changes vs. procedural code
- ✗ Potential for event loops if not careful with routing logic
- ✗ Requires careful deadletter queue management
- ✗ Testing is more complex (needs fake event emitter)

### Neutral
- Event ordering is per-topic; global ordering not guaranteed (acceptable; only matters within single artifact)

## Alternatives Considered

1. **Job Queue (Celery/RQ)** - More heavyweight; Redis simpler for our needs
2. **Message Queue (RabbitMQ)** - Overly complex for Phase 1-4; can migrate later
3. **gRPC/Direct Calls** - Tight coupling defeats modular design
4. **Webhook-based** - Not suitable for internal orchestration

## Related Decisions
- ADR-002: Model-Agnostic Agent Design (agents don't depend on specific LLM)
- ADR-003: Immutable Artifact Versioning (events are source of truth)

## Implementation Notes

1. **Correlation IDs:** Always attach correlation_id to events for tracing
2. **Ordering:** Events for same artifact must be processed serially
3. **Dead Letter Queue:** Undeliverable events go to DLQ after N retries
4. **Timeout:** Each task must have timeout; hung tasks are detected and retried
5. **Idempotency:** All event handlers must be idempotent (can be replayed safely)

## References
- Enterprise Integration Patterns (Gregor Hohpe)
- Event Sourcing pattern (Martin Fowler)
- Temporal.io - Durable execution framework inspiration

---

## ADR-002: Model-Agnostic Design via Model Router

## Status
ACCEPTED

## Context
Early designs bound agents directly to specific LLMs:
- Developer Agent → Code Llama
- Security Agent → Custom security model
- Testing Agent → Testing specialist model

Problems with fixed binding:
1. Can't swap models without code changes
2. Can't route to different models based on task complexity
3. Can't fall back to alternative models if primary is unavailable
4. Can't A/B test different models
5. Blocks experiments with new models
6. Expensive to lock into large models for simple tasks

Requirements:
- Support local models (Ollama) for development
- Support cloud models (Azure GPU) for production
- Select appropriate model based on task complexity
- Minimize cost while maintaining quality
- Support model fallback if primary unavailable
- Enable A/B testing and continuous improvement

## Decision
**Create a Model Router component that dynamically selects the appropriate LLM for each task, based on complexity, context, cost, and availability.**

Model Router is inserted between agents and LLMs:
- Agent requests task execution without specifying model
- Model Router analyzes task characteristics
- Model Router ranks candidate models by suitability
- Model Router selects primary model + fallback chain
- If primary fails or unavailable, automatically try fallback
- Metrics collected on model quality/speed/cost

## Rationale

### Why Model Router?
1. **Flexibility:** Try new models without changing agent code
2. **Cost Optimization:** Use cheapest model that meets quality bar
3. **Resilience:** Fallback to alternative models if primary unavailable
4. **Experimentation:** A/B test different models on same task
5. **Future-Proofing:** Tomorrow's better models automatically used
6. **Scale:** Can route to different infrastructure (local, Azure, etc.)

### Why Not Alternatives?

**Hardcoded Agents:** Tightly couples to specific models; inflexible

**Single Global Model:** Wasteful; complex tasks need big model, simple tasks don't

**Agent Chooses Model:** Duplicates decision logic; agents should focus on task, not infrastructure

## Consequences

### Positive
- ✓ Easy to swap models without code changes
- ✓ Can optimize cost/quality trade-off
- ✓ Supports local→cloud migration path
- ✓ Enables continuous model improvements
- ✓ Reduces vendor lock-in

### Negative
- ✗ Additional complexity in request path
- ✗ Need metrics to inform model selection
- ✗ Requires testing with multiple models
- ✗ Decision logic can become complex

## Alternatives Considered

1. **Hardcoded models in agents** - Inflexible; requires code changes
2. **Agent selects model** - Duplicates logic; agents shouldn't know about infrastructure
3. **Single large model for all** - Wasteful; expensive; slow

## Related Decisions
- ADR-001: Event-Driven Architecture (Model Router fits well with async model)
- ADR-004: Hybrid Local/Azure Execution (Model Router enables this)

## Implementation Notes

1. **Task Classification:** Classify tasks by complexity in O(1) time
2. **Context Windowing:** Estimate token requirements; select model with sufficient context
3. **Fallback Chain:** Each model has backup; tested and ranked
4. **Metrics:** Track success rate, latency, and cost for each model/task combination
5. **Cost Optimization:** Use algorithms to suggest cheapest model combo

---

## ADR-003: Immutable Artifact Versioning

## Status
ACCEPTED

## Context
Artifacts (requirements, designs, code, test results) evolve through the pipeline. Need to track:
- What changed?
- When did it change?
- Who changed it?
- Why did it change?
- Can we revert?

Old approaches considered:
1. **In-place updates:** Overwrite artifact (lose history)
2. **Timestamps only:** Keep old versions but no metadata
3. **Git-based:** Use Git for everything (doesn't work well for non-code artifacts)
4. **Full immutability:** Every change creates new version

Requirements:
- Complete audit trail for compliance
- Ability to revert to previous versions
- Efficient storage (don't duplicate everything)
- Fast retrieval of latest version
- Support rollback in case of errors
- Work across artifact types (requirements, designs, code, etc.)

## Decision
**Implement write-once artifact versioning where each change creates a new immutable version. Latest version always referenced in main artifact record.**

```
Artifact {
  id: "story-123"
  current_version: 3
  
  versions: {
    1: { content: "...", timestamp: t1, actor: rte-agent, reason: "Created" }
    2: { content: "...", timestamp: t2, actor: developer-agent, reason: "Updated AC" }
    3: { content: "...", timestamp: t3, actor: reviewer-agent, reason: "Final review feedback" }
  }
}
```

## Rationale

### Why Immutable Versions?
1. **Compliance:** Audit trail is immutable; legally sound
2. **Debugging:** Can replay any version to understand what went wrong
3. **Safety:** Can always revert; no risk of losing work
4. **Traceability:** Who changed what and when is clear
5. **Collaboration:** Easy to understand evolution of artifact

### Why Not Alternatives?

**In-place updates:** Loses history; not compliant; can't revert

**Git only:** Doesn't work for non-code (designs, requirements, test results); adds complexity

**Timestamps only:** Lacks context; need to know who, why, what changed

## Consequences

### Positive
- ✓ Perfect audit trail for compliance
- ✓ Can safely experiment (revert if needed)
- ✓ Easy debugging via version history
- ✓ No accidental deletions

### Negative
- ✗ Storage overhead for large artifacts
- ✗ Slightly more complex retrieval logic
- ✗ Need to manage garbage collection of old versions

## Storage Strategy

- Keep all versions (no deletion)
- Compress old versions (gzip)
- Archive to cheap storage after 1 year
- Restore from archive if needed

## Alternatives Considered

1. **In-place updates** - No audit trail; not compliant
2. **Git-based** - Works for code only; not suitable for structured artifacts
3. **Time-series DB** - Overkill; simpler to use PostgreSQL

## Related Decisions
- ADR-001: Event-Driven Architecture (state transitions trigger new versions)

---

## ADR-004: Hybrid Local/Azure Execution Model

## Status
ACCEPTED

## Context
Korame needs to support:
- **Development:** Work on laptops with local models (Ollama)
- **Production:** Enterprise customers needing high-quality inference
- **Cost:** Don't pay for Azure if local sufficient
- **Quality:** Use best model for each task

Options:
1. **Local only:** Limited to available local models; expensive for complex tasks
2. **Azure only:** Requires cloud subscription; slower iteration during development; higher cost
3. **Hybrid:** Route to local if sufficient, else Azure

Requirements:
- Developers can work offline
- Local development doesn't require Azure subscription
- Production deployments use Azure GPU for critical tasks
- Automatic fallback if one location unavailable
- Transparent routing (agents don't know which model location)

## Decision
**Implement hybrid execution where Model Router dynamically routes tasks to either local Ollama or Azure GPU pool based on task complexity, resource availability, and cost.**

```
Simple task (< 500 tokens) → Local Ollama (free, 10ms)
Medium task (500-2K) → Local if available, else Azure
Complex task (> 2K) → Azure GPU (high quality, 200ms)
Code generation → Prefer Azure (better quality)
Emergency → Use cheapest available
```

## Rationale

### Why Hybrid?
1. **Development:** Local models enable offline work, faster iteration
2. **Cost:** Simple tasks on free local models; complex tasks on paid Azure
3. **Quality:** Mission-critical tasks use best (most expensive) models
4. **Availability:** If one location down, fallback to other
5. **Flexibility:** Choose right tool for job

### Why Not Alternatives?

**Local only:** Limits quality; complex tasks need better models

**Azure only:** Expensive for simple tasks; requires connectivity; breaks offline development

## Consequences

### Positive
- ✓ Works offline during development
- ✓ Cost-effective for simple tasks
- ✓ Best model quality for important decisions
- ✓ Resilient to outages in either location

### Negative
- ✗ Operational complexity (manage two model sources)
- ✗ Latency variance (local fast, Azure slower)
- ✗ Need to test against both

## Configuration

```yaml
# config/local.yaml (development)
models:
  - name: qwen3_8b
    provider: ollama
    location: local
    
  - name: code_llama_7b
    provider: ollama
    location: local
    
  - name: gpt4_32k
    provider: azure
    location: azure
    (disabled for local dev to avoid costs)

# config/azure.yaml (production)
models:
  - name: qwen3_8b
    provider: ollama
    location: local  # Still available
    
  - name: gpt4_32k
    provider: azure
    location: azure
    (enabled for production)
```

## Related Decisions
- ADR-002: Model-Agnostic Design (enables this)
- ADR-001: Event-Driven Architecture (Model Router fits into async flow)

---

## ADR-005: Quality Gates Cannot Be Skipped

## Status
ACCEPTED

## Context
Early discussions: "Can we skip code review if we're confident?" or "Can we deploy without testing?"

Arguments for skipping:
- Speed; trust developer
- Reduce latency
- Emergency fixes (security patches)

Arguments against:
- Inconsistency; different standards for different artifacts
- Human judgment fallible; even experts miss issues
- Creates precedent; "just this once" becomes policy
- Audit trail incomplete; questions compliance
- False economy; fixing later more expensive than fixing now

## Decision
**No quality gate can be skipped, period. Every artifact must pass Code Review → Security → Testing → UAT in order. No exceptions.**

Exceptions for emergency fixes follow same process:
1. Fix evaluated for security risk
2. Fast-tracked (1-hour SLA instead of normal)
3. Still passes all gates
4. Incident documentation mandatory

## Rationale

### Consistency
All artifacts treated equally; no special cases erode standards over time

### Compliance
Full audit trail required for regulations (SOC2, HIPAA, PCI-DSS, etc.)

### Quality
Defects caught early are cheaper to fix than in production

### Trust
Consistent enforcement builds confidence in process

## Consequences

### Positive
- ✓ Consistent quality for all artifacts
- ✓ Clear audit trail; no exceptions to explain
- ✓ Defects caught before production
- ✓ Team alignment; everyone knows the rules

### Negative
- ✗ Slightly slower for urgent fixes
- ✗ Team must adapt to stricter process
- ✗ Cannot do "quick patches"

## Emergency Process

For actual emergencies (security breach, data loss, service down):
1. Fix implemented (minimal code change)
2. Fast-tracked gate review (1 hour, not 24 hours)
3. All gates still run; just faster
4. Executive approval required
5. Post-incident review mandatory

## Related Decisions
- ADR-001: Event-Driven Architecture (gates implemented as events)
- ADR-003: Immutable Artifact Versioning (gates recorded as version metadata)

---

## How to Add New ADRs

1. Copy the template above
2. Give it next number (ADR-006, ADR-007, etc.)
3. Write in Markdown format
4. Get team consensus before marking as ACCEPTED
5. Link related ADRs
6. Store in `docs/ADRs/` directory
7. Reference in relevant sections of SAS

**Current ADRs:**
- ADR-001: Event-Driven Architecture
- ADR-002: Model-Agnostic Design via Model Router
- ADR-003: Immutable Artifact Versioning
- ADR-004: Hybrid Local/Azure Execution
- ADR-005: Quality Gates Cannot Be Skipped

