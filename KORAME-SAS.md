# KORAME
## Software Architecture Specification (SAS)
**Version:** 1.0 (Foundation)  
**Status:** Foundation Phase  
**Last Updated:** July 25, 2026  
**Author:** Korame Architecture Team  

---

## Table of Contents

1. [Vision & Goals](#1-vision--goals)
2. [Functional Requirements](#2-functional-requirements)
3. [Non-Functional Requirements](#3-non-functional-requirements)
4. [High-Level Architecture](#4-high-level-architecture)
5. [Korame Kernel](#5-korame-kernel)
6. [Workflow Orchestrator](#6-workflow-orchestrator)
7. [Knowledge Fabric](#7-knowledge-fabric)
8. [Agent Framework](#8-agent-framework)
9. [Memory & RAG](#9-memory--rag)
10. [Plugin Architecture](#10-plugin-architecture)
11. [Event Bus](#11-event-bus)
12. [Model Router](#12-model-router)
13. [Agent SDK](#13-agent-sdk)
14. [APIs](#14-apis)
15. [Data Model](#15-data-model)
16. [Repository Structure](#16-repository-structure)
17. [Deployment Architecture](#17-deployment-architecture)
18. [Security](#18-security)
19. [Observability](#19-observability)
20. [Roadmap](#20-roadmap)

---

# 1. Vision & Goals

## 1.1 Vision Statement

Korame is an **AI-native Software Delivery Organization** composed of specialized agents that collaborate through a unified Workflow Orchestrator, shared project memory, and an event-driven architecture. It transforms business requirements into production-ready software while enforcing industry-standard quality gates, security validation, comprehensive testing, and controlled deployment practices.

Korame operates as a self-managing, autonomous software factory where human oversight (via Release Train Engineer) remains critical for business planning and final decisions, while the system handles execution, quality enforcement, and deployment orchestration.

## 1.2 Strategic Goals

### Transform Software Development
- **Objective:** Eliminate manual context switching between development phases
- **Success Metric:** Single artifact lifecycle from requirement to deployment, zero manual handoffs
- **Target State:** Agents understand context, maintain memory, and execute without human intervention between gates

### Enforce Quality & Security by Design
- **Objective:** Make quality and security non-negotiable from day one
- **Success Metric:** 100% of artifacts pass code review, security scan, and testing gates before UAT
- **Target State:** Failed gates automatically loop to Developer with actionable findings

### Enable Hybrid Execution
- **Objective:** Support local development today, Azure GPU execution tomorrow
- **Success Metric:** Model-agnostic architecture allows transparent scaling to cloud infrastructure
- **Target State:** Agents execute on appropriate infrastructure (local/cloud) without code changes

### Build Enterprise-Ready AI Platform
- **Objective:** Create a commercially viable, self-contained software delivery platform
- **Success Metric:** Deployable as standalone product to enterprises
- **Target State:** Multi-tenant capable, fully auditable, compliant with enterprise standards

## 1.3 Core Principles

### Principle 1: Workflow Orchestrator is the Execution Engine
The Workflow Orchestrator is the single source of truth for task scheduling, state management, and quality gate enforcement. All agents communicate asynchronously through events, never through direct function calls. This ensures:
- **Decoupling:** Agents can be deployed independently
- **Observability:** All state transitions are auditable
- **Resilience:** Failed agents don't cascade failures

### Principle 2: Release Train Engineer (RTE) is the Business Owner
The RTE represents stakeholder interests and maintains final approval authority for release decisions. The RTE:
- Creates epics and user stories
- Receives status reports and quality metrics
- Approves artifacts for deployment
- Controls release scheduling

The RTE delegates execution to the Workflow Orchestrator but never surrenders decision authority.

### Principle 3: Agents Communicate Through Events, Never Direct Calls
All inter-agent communication flows through the Event Bus. This ensures:
- **Asynchronous Execution:** Agents don't block waiting for responses
- **Audit Trail:** All actions are logged and traceable
- **Scalability:** Adding agents doesn't require coordinator changes
- **Fault Isolation:** Failed agents don't bring down other agents

### Principle 4: Artifacts Move Through Defined Lifecycle States
Every artifact (requirement, design, code, test result) moves through a well-defined state machine. State transitions are immutable and auditable. Backward movement only occurs when quality gates fail, never for convenience.

### Principle 5: Failed Quality Gates Always Loop Back to Developer
When any gate fails (Code Review, Security, Testing), the artifact returns to the Developer Agent with detailed findings. The developer cannot skip gates—they must fix the issue and re-submit. Only after the developer addresses the failure does the artifact progress.

### Principle 6: Only Fully Validated Artifacts Reach UAT
UAT occurs only after all engineering gates pass (Code Review, Security, Automated Testing). This protects the UAT team from incomplete work and ensures UAT failure is a business decision, not an engineering issue.

### Principle 7: Only UAT-Approved Artifacts Reach DevOps
The DevOps Agent only receives artifacts approved by UAT. This ensures:
- **Production Confidence:** No untested code reaches deployment infrastructure
- **Fast CI/CD:** DevOps can assume validity and focus on infrastructure
- **Audit Trail:** Every deployed artifact has business sign-off

---

# 2. Functional Requirements

## 2.1 Requirement Management

### FR-REQ-001: Create and Organize Requirements
- The RTE can create epics, features, and user stories in natural language
- Each story automatically receives a unique identifier and timestamp
- Stories can be organized into epics with rollup tracking
- Stories can include acceptance criteria, priority, and business value

### FR-REQ-002: Generate Artifacts from Requirements
- The Architect Agent receives a story and generates a design document
- The Developer Agent receives a design and generates:
  - Implementation plan (tasks, modules, dependencies)
  - Source code (following the design)
  - Unit tests
- The artifact is versioned and linked to the source requirement

### FR-REQ-003: Manage Artifact Lifecycle
- Artifacts move through defined states: NEW → PLANNED → ARCHITECTED → IN_DEVELOPMENT → CODE_REVIEW → SECURITY_SCAN → AUTOMATED_TESTING → READY_FOR_UAT → UAT → READY_FOR_DEPLOYMENT → DEPLOYED → COMPLETED
- State transitions are immutable once recorded
- Failed quality gates return artifacts to IN_DEVELOPMENT
- All transitions are timestamped and auditable

## 2.2 Quality & Review Workflows

### FR-QA-001: Code Review Process
- Code Reviewer Agent receives completed code
- Reviewer checks against defined standards (style, documentation, patterns, performance)
- Reviewer can APPROVE, REQUEST_CHANGES, or BLOCK (security-level issues)
- REQUEST_CHANGES loops to Developer; BLOCK escalates findings
- APPROVE moves artifact to SECURITY_SCAN state

### FR-QA-002: Security Validation
- Security Agent receives code and design documentation
- Security scan checks for:
  - Known vulnerabilities in dependencies
  - Common OWASP Top 10 issues
  - Secrets in source code
  - Compliance violations
- Security can APPROVE, REQUEST_CHANGES, or BLOCK
- BLOCK artifacts cannot proceed to testing and require developer remediation

### FR-QA-003: Automated Testing Coordination
- Testing Agent receives implementation and generates/runs test suites
- Tests include:
  - Unit tests (inherited from Developer)
  - Integration tests (generated by Testing Agent)
  - Performance tests
  - Coverage analysis
- Testing can APPROVE (coverage ≥ 80%), REQUEST_CHANGES, or BLOCK
- Test results are stored for audit and trend analysis

## 2.3 UAT & Deployment

### FR-UAT-001: Business Validation
- UAT Agent (or human tester) receives fully validated engineering artifacts
- UAT performs business-level acceptance testing against original requirements
- UAT can APPROVE, REQUEST_CHANGES, or BLOCK
- UAT failure returns artifact to Developer (full loop: Code Review → Security → Testing)
- APPROVE moves artifact to READY_FOR_DEPLOYMENT

### FR-DEPLOY-001: Deployment Orchestration
- DevOps Agent receives UAT-approved artifacts
- DevOps:
  - Prepares deployment infrastructure
  - Executes blue-green or canary deployment
  - Validates deployment health
  - Backs off if health checks fail
- Deployment status is reported to RTE dashboard

## 2.4 Knowledge Management

### FR-KNL-001: Ingest Project Context
- Workspace files are indexed and stored in Knowledge Fabric
- Git history is analyzed and stored (commits, authors, branches, PRs)
- Architecture documents are parsed and linked to code
- API specifications and test cases are indexed
- Decisions and conversations are recorded

### FR-KNL-002: Semantic Search & Retrieval
- Agents can query Knowledge Fabric to retrieve:
  - Relevant source code examples
  - Previous design decisions
  - Similar test patterns
  - API documentation
- Retrieval uses semantic search (vector similarity) + graph traversal
- Results are ranked by relevance and recency

### FR-KNL-003: Context Assembly
- Before invoking an agent, Workflow Orchestrator assembles context:
  - Relevant requirements and acceptance criteria
  - Related source code and architecture
  - Previous decisions and discussions
  - Available APIs and dependencies
- Context is injected into agent prompts as structured data

## 2.5 Configuration & Extensibility

### FR-CONFIG-001: Configuration Management
- All agent behaviors are configurable via YAML/JSON
- Thresholds for quality gates (e.g., code coverage minimum, security severity threshold)
- Model selection and routing rules
- Event routing rules
- Timeout and retry policies

### FR-PLUGIN-001: Plugin Architecture
- Custom agents can be registered without modifying core orchestrator
- Plugins receive standardized input (artifact, context, config)
- Plugins emit standardized events (APPROVED, CHANGES_REQUESTED, BLOCKED)
- Plugin Manager handles lifecycle (register, validate, load, unload)

---

# 3. Non-Functional Requirements

## 3.1 Performance

### NFR-PERF-001: Latency
- Story-to-code generation: < 15 minutes (after architecture completes)
- Code review feedback: < 5 minutes
- Security scan: < 10 minutes
- Full pipeline (requirement to UAT-ready): < 1 hour for typical story

### NFR-PERF-002: Throughput
- Support concurrent processing of 10+ artifacts in pipeline
- Handle 100+ stories/month without degradation
- Model routing engine selects appropriate model in < 100ms

### NFR-PERF-003: Resource Efficiency
- Local model inference on consumer-grade hardware (8GB+ RAM)
- Efficient vector search: < 200ms for 1M vector queries
- Event processing: < 50ms latency end-to-end

## 3.2 Scalability

### NFR-SCALE-001: Horizontal Scalability
- Orchestrator can distribute agent execution across multiple workers
- Event bus scales to 10,000+ events/second
- Knowledge Fabric can scale to 1M+ document vectors

### NFR-SCALE-002: Cloud-Ready Architecture
- Architecture designed for multi-agent deployment on Azure AKS
- Stateless agent design allows dynamic scaling
- Database and event bus use cloud-native services

## 3.3 Reliability

### NFR-REL-001: Availability
- Workflow Orchestrator: 99.5% uptime SLA
- Event bus: 99.9% uptime SLA
- Graceful degradation: failed agents don't block entire pipeline

### NFR-REL-002: Recoverability
- All state is persisted; recovered from last known good state
- Failed jobs auto-retry with exponential backoff (max 3 retries)
- Dead letter queue for unrecoverable failures with operator alert

### NFR-REL-003: Data Integrity
- All artifact state transitions are immutable (write-once, read-many)
- Distributed transactions use event sourcing pattern
- Backup strategy: daily snapshots, tested recovery procedures

## 3.4 Security

### NFR-SEC-001: Authentication & Authorization
- All API calls require bearer token (JWT)
- Role-based access control: RTE, DevOps, Architect, Developer, Reviewer, Security, Testing
- All agents authenticate to event bus and database

### NFR-SEC-002: Data Protection
- Sensitive data (secrets, credentials) encrypted at rest and in transit
- No secrets in logs or debug output
- Audit log immutable, restricted read access

### NFR-SEC-003: Compliance
- OWASP Top 10 compliance built into Security Agent
- Dependency scanning for known CVEs
- Compliance reports available for audits

## 3.5 Maintainability

### NFR-MAIN-001: Observability
- Every significant action logged with context
- Structured logging (JSON) for log aggregation
- Metrics: agent execution time, gate pass/fail rates, pipeline throughput
- Distributed tracing of artifact flow through pipeline

### NFR-MAIN-002: Documentation
- Architecture decisions recorded in ADRs
- API specifications auto-generated from code
- Agent prompts and behaviors documented
- Runbook for common operations

### NFR-MAIN-003: Testability
- Unit test coverage ≥ 80% for core components
- Integration tests for full artifact pipeline
- Load tests for performance verification
- Chaos engineering tests for failure scenarios

## 3.6 Usability

### NFR-USE-001: RTE Dashboard
- Single-page dashboard showing:
  - Current artifacts and states
  - Quality gate pass/fail metrics
  - Pipeline throughput and velocity
  - Team productivity metrics
- Real-time updates via WebSocket

### NFR-USE-002: Natural Language Interface
- RTE creates stories in plain English
- No special syntax or markup required
- Agents understand context from conversation history

---

# 4. High-Level Architecture

## 4.1 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        RTE Dashboard                         │
│                                                              │
│   - Story creation                                           │
│   - Pipeline visibility                                      │
│   - Quality metrics                                          │
│   - Deployment approval                                      │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│              WORKFLOW ORCHESTRATOR                          │
│                                                              │
│   - Task scheduling & dependency resolution                │
│   - State machine enforcement                               │
│   - Quality gate management                                 │
│   - Event routing & correlation                             │
│   - Context assembly                                        │
│   - Model router                                            │
└─────────────────────────────────────────────────────────────┘
     │                     │                      │
     │                     │                      │
┌────▼───────┐  ┌─────────▼──────┐  ┌───────────▼────┐
│  Event Bus  │  │ Knowledge      │  │  Configuration │
│  (Redis)    │  │  Fabric        │  │  Manager       │
│             │  │  (PostgreSQL,  │  │                │
│  - Pub/Sub  │  │   Neo4j,       │  │  - YAML/JSON   │
│  - Routing  │  │   ChromaDB,    │  │  - Validation  │
│  - Replay   │  │   Git)         │  │  - Versioning  │
└─────────────┘  └────────────────┘  └────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      AGENT POOL                             │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   RTE    │  │Architect │  │Developer │  │ Reviewer │   │
│  │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Security │  │ Testing  │  │   UAT    │  │ DevOps   │   │
│  │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  Each agent:                                               │
│  - Receives input via event                                │
│  - Uses Knowledge Fabric context                           │
│  - Invokes LLM via Model Router                            │
│  - Emits completion event                                  │
└─────────────────────────────────────────────────────────────┘
```

## 4.2 Data Flow: Story to Deployment

```
RTE Creates Story (Natural Language)
         │
         ▼
Orchestrator: NEW → PLANNED
         │
         ▼
Architect Agent: Generates Design
         │
         ▼
Orchestrator: PLANNED → ARCHITECTED
         │
         ▼
Developer Agent: Generates Code + Unit Tests
         │
         ▼
Orchestrator: ARCHITECTED → IN_DEVELOPMENT
         │
         ▼
Code Reviewer Agent: Review Code
         │
    ┌────┴────┐
    │          │
    ▼ PASS     ▼ FAIL
    │      Return to Developer
    │          │
    ▼          └──────────┐
Orchestrator:                │
CODE_REVIEW → SECURITY_SCAN  │
    │                        │
    ├─ Security Agent ───┐   │
    │                    │   │
    │    ┌───PASS────────┤   │
    │    │               │   │
    ▼    ▼               │   │
Orchestrator:           │   │
SECURITY_SCAN → AUTOMATED_TESTING
    │                   │   │
    ├─ Testing Agent ───┤   │
    │                   │   │
    │    ┌──PASS────────┤   │
    │    │              │   │
    ▼    ▼              │   │
Orchestrator:          │   │
AUTOMATED_TESTING → READY_FOR_UAT
         │             │   │
         ▼             │   │
    UAT Agent          │   │
         │             │   │
    ┌────┴────┐        │   │
    │          │        │   │
    ▼ PASS     ▼ FAIL   │   │
    │      Return to Dev─┘   │
    │          │            │
    ▼          └────────────┘
Orchestrator:
READY_FOR_UAT → READY_FOR_DEPLOYMENT
         │
         ▼
DevOps Agent: Deploy to Production
         │
         ▼
Orchestrator:
READY_FOR_DEPLOYMENT → DEPLOYED → COMPLETED
         │
         ▼
RTE Dashboard: Deployment Complete
```

## 4.3 Artifact State Machine

```
                        ┌─────────────┐
                        │     NEW     │
                        └──────┬──────┘
                               │
                        ┌──────▼──────┐
                        │   PLANNED   │
                        └──────┬──────┘
                               │
                        ┌──────▼────────────┐
                        │  ARCHITECTED     │
                        └──────┬───────────┘
                               │
                        ┌──────▼────────────┐
                        │ IN_DEVELOPMENT   │
                        └──┬──────────────┬─┘
                           │              │
                      (Development Complete)
                           │              │
                        ┌──▼──────────┐   │
                        │ CODE_REVIEW │   │
                        └──┬────────┬─┘   │
                      Pass │        │Fail │
                           │        └─────┘
                           │         (Loops back)
                        ┌──▼────────────┐
                        │SECURITY_SCAN  │
                        └──┬────────┬──┘
                      Pass │        │Fail
                           │        └─────┐
                           │          (Loops back)
                        ┌──▼─────────────┐
                        │AUTOMATED_TEST  │
                        └──┬────────┬───┘
                      Pass │        │Fail
                           │        └─────┐
                           │          (Loops back)
                        ┌──▼──────────────┐
                        │READY_FOR_UAT    │
                        └──┬────────┬────┘
                           │        │
                        ┌──▼─┐    ┌┴──────┐
                        │UAT │    │ Fail  │
                        └──┬─┘    └──┬────┘
                      Pass │   (Full Loop back)
                           │         │
                        ┌──▼────────────┐
                        │READY_FOR_DEP  │
                        └──┬────────────┘
                           │
                        ┌──▼────────┐
                        │ DEPLOYED  │
                        └──┬────────┘
                           │
                        ┌──▼────────┐
                        │COMPLETED  │
                        └───────────┘
```

---

# 5. Korame Kernel

## 5.1 Kernel Philosophy

The Korame Kernel is the foundational runtime that every future agent, integration, and extension depends on. It is intentionally **model-agnostic** and **execution-environment agnostic**, supporting local models today (Ollama) and transparent scaling to Azure GPU worker pools in the future.

The Kernel does not depend on any specific LLM vendor, model size, or compute infrastructure. This ensures:
- **Portability:** Code works on laptop today, scales to cloud tomorrow
- **Cost Efficiency:** Choose the right model for each task
- **Independence:** Not locked into any vendor's ecosystem
- **Future-Proofing:** Can adopt better models without architectural changes

## 5.2 Core Kernel Components

### 5.2.1 Workflow Orchestrator
The heart of Korame. Responsible for:
- **Task Scheduling:** Determines which agent should execute next
- **Dependency Resolution:** Ensures upstream tasks complete before downstream tasks start
- **State Machine Enforcement:** Transitions artifacts through lifecycle states
- **Quality Gate Management:** Ensures failed gates route artifacts back to Developer
- **Event Routing:** Matches events to listeners and maintains message ordering
- **Context Assembly:** Retrieves relevant information from Knowledge Fabric before invoking agents
- **Timeout Handling:** Cancels stuck tasks and triggers retries
- **Audit Logging:** Records every state transition and decision

See Section 6 for detailed Workflow Orchestrator design.

### 5.2.2 Event Bus (Redis)
Asynchronous pub/sub system for inter-agent communication. Features:
- **Pub/Sub Model:** Agents publish events without knowing subscribers
- **Topic Routing:** Events routed to relevant listeners based on topic + artifact type
- **Ordering Guarantees:** Events for same artifact processed in order
- **Dead Letter Queue:** Undeliverable messages logged for operator review
- **Event Replay:** Support replaying events for debugging and recovery
- **Persistence:** Events stored for audit trail

See Section 11 for detailed Event Bus design.

### 5.2.3 Agent SDK
Standardized interface all agents implement. Features:
- **Consistent Input/Output Format:** All agents receive artifact + context, emit events
- **Error Handling:** Standard error codes and retry semantics
- **Logging Integration:** Agents inherit logging configuration
- **Model Invocation:** Agents use Model Router to invoke LLMs
- **Context Access:** Simple API to query Knowledge Fabric
- **Plugin Registration:** Agents self-register with Orchestrator

See Section 13 for detailed Agent SDK design.

### 5.2.4 Knowledge Fabric Interface
Unified interface to all project knowledge stores. Features:
- **Multi-Store Support:** Abstracts PostgreSQL, Neo4j, ChromaDB, Git, filesystem
- **Query API:** Semantic search, graph queries, full-text search
- **Context Assembly:** Retrieves relevant information based on artifact type and history
- **Caching:** In-memory cache for hot data (requirements, recent decisions)
- **Indexing:** Automatic indexing of new artifacts as they're created

See Section 7 for detailed Knowledge Fabric design.

### 5.2.5 Artifact Manager
Manages artifact versioning, storage, and retrieval. Features:
- **Versioning:** Every artifact change creates new version
- **Immutable History:** Full edit history for compliance and rollback
- **Storage Abstraction:** Works with filesystem (local) or Azure Blob Storage (cloud)
- **Compression:** Efficient storage of large artifacts (code, logs)
- **Garbage Collection:** Retains immutable copies for audit, purges obsolete versions

### 5.2.6 Plugin Manager
Framework for extending Korame without modifying core. Features:
- **Plugin Registration:** Custom agents register with standard interface
- **Lifecycle Management:** Load, enable, disable, unload plugins
- **Configuration Isolation:** Each plugin gets separate config namespace
- **Dependency Resolution:** Handles plugin interdependencies
- **Hot Reload:** Add/remove plugins without restarting core

See Section 10 for detailed Plugin Architecture.

### 5.2.7 Configuration Manager
Centralized configuration for all components. Features:
- **YAML/JSON Format:** Human-readable, version-controlled configuration
- **Environment Overrides:** Environment variables override file-based config
- **Validation:** Schema validation on startup
- **Versioning:** Track config changes alongside code changes
- **Multi-Environment:** Separate configs for local/dev/staging/production

### 5.2.8 Logging & Telemetry
Observability foundation for the entire system. Features:
- **Structured Logging:** JSON logs for log aggregation systems
- **Log Levels:** Debug, Info, Warn, Error with context
- **Distributed Tracing:** Correlation IDs track artifact flow through pipeline
- **Metrics:** Prometheus-compatible metrics for monitoring
- **Alerting:** Anomaly detection (slow agents, failed gates, hung tasks)

See Section 19 for detailed Observability design.

### 5.2.9 Model Router
Intelligent model selection engine. Features:
- **Task-Based Routing:** Different tasks use different models
- **Resource Awareness:** Routes to available compute (local/Azure)
- **Cost Optimization:** Prefers cheaper models when performance allows
- **Fallback Strategy:** Cascading model options if primary unavailable
- **Performance Monitoring:** Tracks model quality and speed over time

See Section 12 for detailed Model Router design.

## 5.3 Kernel Interfaces (High-Level)

### Orchestrator Interface
```python
class WorkflowOrchestrator:
    def schedule_artifact(artifact_id, task_type, context) -> Task
    def update_artifact_state(artifact_id, new_state) -> State
    def route_event(event: Event) -> None
    def assemble_context(artifact_id, agent_type) -> Context
    def check_quality_gate(artifact_id, gate_type) -> GateResult
    def handle_failure(artifact_id, reason) -> None
    def get_audit_log(artifact_id) -> List[AuditEntry]
```

### Agent Interface (implemented by all agents)
```python
class Agent:
    def can_handle(event: Event) -> bool
    def execute(artifact, context, config) -> Result
    def emit_event(event: Event) -> None
```

### Knowledge Fabric Interface
```python
class KnowledgeFabric:
    def search(query: str, context_type: str) -> List[Document]
    def get_graph_neighbors(entity_id, relationship_type) -> List[Entity]
    def ingest_artifact(artifact_id, artifact_data) -> None
    def get_decisions(artifact_id) -> List[Decision]
    def get_similar_code(query: str, limit: int) -> List[CodeSnippet]
```

---

# 6. Workflow Orchestrator

## 6.1 Orchestrator Responsibilities

### Core Responsibilities
1. **Artifact Lifecycle Management:** Transitions artifacts through state machine
2. **Task Scheduling:** Determines which agent executes next
3. **Dependency Resolution:** Ensures prerequisites complete before dependent tasks
4. **Quality Gate Enforcement:** Blocks invalid state transitions, routes failures to Developer
5. **Event Routing:** Matches incoming events to interested listeners
6. **Context Assembly:** Retrieves and structures context before agent invocation
7. **Timeout Management:** Detects and handles hung tasks
8. **Retry Logic:** Implements backoff strategy for transient failures
9. **Audit Logging:** Records immutable history of all actions
10. **Metric Collection:** Tracks pipeline health and performance

## 6.2 State Machine Enforcement

### State Definitions

| State | Entered When | Can Transition To | Gate Enforcement |
|-------|--------------|------------------|------------------|
| NEW | Artifact created | PLANNED | RTE initiates planning |
| PLANNED | Planning complete | ARCHITECTED | Story approved by RTE |
| ARCHITECTED | Architecture complete | IN_DEVELOPMENT | Design approved by Architect |
| IN_DEVELOPMENT | Development starts | CODE_REVIEW | Developer marks complete |
| CODE_REVIEW | Code ready for review | SECURITY_SCAN (pass) or IN_DEVELOPMENT (fail) | Code Reviewer approval required |
| SECURITY_SCAN | Security review starts | AUTOMATED_TESTING (pass) or IN_DEVELOPMENT (fail) | Security Agent approval required |
| AUTOMATED_TESTING | Testing starts | READY_FOR_UAT (pass) or IN_DEVELOPMENT (fail) | Testing Agent approval + coverage ≥ 80% |
| READY_FOR_UAT | All engineering gates pass | UAT | No gates; UAT can proceed |
| UAT | Business validation | READY_FOR_DEPLOYMENT (pass) or IN_DEVELOPMENT (fail) | UAT approval required; full loop back on fail |
| READY_FOR_DEPLOYMENT | UAT approved | DEPLOYED | DevOps permission required |
| DEPLOYED | Deployment complete | COMPLETED | DevOps confirmation |
| COMPLETED | Deployment verified | (terminal state) | Archive eligible |

### State Transition Rules

```python
class StateTransition:
    def from_state: str
    def to_state: str
    def required_gate: Optional[GateType]  # Gate that must pass
    def responsible_agent: str  # Agent that triggered transition
    def timestamp: datetime
    def reason: str  # Why transition occurred
    def gate_result: Optional[GateResult]  # Pass/Fail/Blocked with findings
```

### Quality Gate Enforcement Rules

1. **Code Review → Security:** Cannot skip; must pass before moving forward
2. **Security → Testing:** Cannot skip; must pass before moving forward
3. **Testing → UAT:** Cannot skip; coverage must be ≥ 80%
4. **Any gate fails:** Artifact returns to IN_DEVELOPMENT
5. **UAT fails:** Artifact returns to IN_DEVELOPMENT, followed by mandatory re-run of Code Review, Security, and Testing
6. **No backward transitions:** Artifacts only move forward or reset to IN_DEVELOPMENT

## 6.3 Task Scheduling Algorithm

### Scheduling Strategy: Event-Driven with Priority Queue

```
When artifact enters new state:
  1. Look up applicable tasks for new state
  2. Determine task dependencies (prerequisites)
  3. For each task with met dependencies:
     a. Assemble context from Knowledge Fabric
     b. Determine target agent (via plugin registry or default)
     c. Create Task object with priority
     d. Publish "TaskReady" event to agent's topic
  4. If dependencies unmet, add to waiting queue with dependency callback
  5. If dependencies cycle, return error and halt artifact
```

### Priority Determination

```
Base Priority = Gate Criticality:
  - Code Review: 100 (critical path)
  - Security: 100 (critical path)  
  - Testing: 90 (critical path)
  - UAT: 80 (blocking deployment)
  - DevOps: 70 (final stage)

Adjusted Priority = Base + Boost Factors:
  - High Business Value: +20
  - Urgent flag set: +30
  - Stakeholder escalation: +40
  - SLA near deadline: +50

Result: Priority Queue processed by (Priority DESC, Created ASC)
```

## 6.4 Context Assembly

### Context Assembly Pipeline

Before invoking any agent, Orchestrator assembles a Context object:

```python
context = {
    "artifact": {
        "id": "story-123",
        "type": "UserStory",
        "title": "...",
        "description": "...",
        "acceptance_criteria": [...],
        "priority": "High",
        "estimated_hours": 8,
        "status": "IN_DEVELOPMENT"
    },
    
    "history": {
        "created_at": "2026-07-25T10:00Z",
        "last_modified": "2026-07-25T11:30Z",
        "created_by": "rte-agent",
        "modifications": [...]
    },
    
    "related": {
        "epic": { "id": "epic-5", "title": "..."},
        "architecture": { "id": "design-123", "content": "..."},
        "previous_similar": [
            {"artifact_id": "story-100", "similarity": 0.89, "outcome": "success"},
            {"artifact_id": "story-101", "similarity": 0.75, "outcome": "required_rework"}
        ]
    },
    
    "codebase": {
        "recent_changes": [...],  # Last 5 commits
        "affected_modules": ["auth", "payment"],
        "api_endpoints": [...],  # Related endpoints
        "test_coverage": 0.82,
        "dependencies": [...]  # Transitive dependency tree
    },
    
    "decisions": {
        "architectural_decisions": [...],  # ADRs relevant to this artifact
        "security_decisions": [...],
        "previous_feedback": [...]  # From prior attempts if any
    },
    
    "standards": {
        "code_style_guide": "PEP 8 + company extensions",
        "test_expectations": "Unit + integration tests required",
        "security_checklist": [...]
    }
}
```

### Context Retrieval Algorithm

```
For each context category:
  1. Identify context type needed (e.g., "related code", "previous decisions")
  2. Query Knowledge Fabric with artifact metadata
  3. Rank results by relevance (semantic + recency)
  4. Apply context token budget (don't exceed 80% of model context window)
  5. Fetch top-K results that fit in budget
  6. Return structured context object
```

## 6.5 Event Routing & Correlation

### Event Structure

```python
class Event:
    event_id: str  # UUID
    event_type: str  # "TaskReady", "TaskComplete", "GateFailed", etc.
    artifact_id: str  # Which artifact triggered this
    source_agent: str  # Which agent emitted this
    source_task: str  # Which task type
    timestamp: datetime
    payload: dict  # Task-specific data
    correlation_id: str  # Groups related events (for tracing)
    causation_id: str  # Event that caused this one
```

### Event Routing Rules

```
When event received:
  1. Validate event structure (schema validation)
  2. Retrieve correlation_id; if missing, create new one
  3. Look up routing rules for (event_type, artifact_type)
  4. For each matching rule:
     a. Determine target agent or task
     b. Check preconditions (state, gates, dependencies)
     c. If preconditions met, emit "TaskReady" event to target agent topic
     d. If preconditions unmet, add to waiting queue
  5. Log event in audit trail with correlation_id
```

### Guaranteed Ordering

Within a single artifact:
- Events for same artifact processed serially (no interleaving)
- Maintains artifact state consistency
- Prevents race conditions in state machine

Across different artifacts:
- Events processed concurrently
- Independent artifacts don't block each other
- Failure in one artifact doesn't affect others

## 6.6 Failure Handling & Retries

### Failure Detection

```python
class FailureDetector:
    def detect_hung_task(task, timeout_secs=600):
        if now - task.start_time > timeout_secs:
            # Task hung; trigger retry or escalation
            return True
    
    def detect_agent_failure(agent, heartbeat_timeout=30):
        if now - agent.last_heartbeat > heartbeat_timeout:
            # Agent not responding; trigger recovery
            return True
    
    def detect_event_deadlock(artifact_id, wait_time=300):
        if artifact.state not changed for wait_time:
            # Artifact stuck; operator notification needed
            return True
```

### Retry Strategy

```python
Retry Logic:
  Attempt 1: Immediate retry
  Attempt 2: Wait 2 seconds, retry
  Attempt 3: Wait 5 seconds, retry
  
  If all attempts fail:
    - Move artifact to BLOCKED state
    - Create incident ticket for operator
    - Notify RTE
    - Prevent further progress until manual intervention
```

## 6.7 Audit Logging

Every significant action is logged:

```python
class AuditLog:
    timestamp: datetime
    action_type: str  # "StateTransition", "TaskCreated", "GatePassed", etc.
    artifact_id: str
    actor: str  # Agent that initiated action
    from_state: Optional[str]
    to_state: Optional[str]
    metadata: dict  # Task-specific details
    correlation_id: str  # For tracing
    
    # Audit log is write-once, immutable
    def serialize() -> str  # JSON format
    def hash() -> str  # Cryptographic hash for integrity
```

---

# 7. Knowledge Fabric

## 7.1 Knowledge Fabric Architecture

The Knowledge Fabric is a unified interface to all project knowledge stores. It abstracts the complexity of multiple backends (PostgreSQL, Neo4j, ChromaDB, Git, filesystem) and provides agents with a consistent API to query and retrieve context.

### Multi-Store Backend

```
Knowledge Fabric Interface (unified API)
    │
    ├─ PostgreSQL (project state, requirements, artifacts)
    ├─ Neo4j (relationships, decisions, impact analysis)
    ├─ ChromaDB (vector embeddings, semantic search)
    ├─ Git Repository (source code, commit history, branches)
    └─ Filesystem/Blob Storage (workspace files, logs, reports)
```

### Information Categories

| Category | Stored In | Use Case |
|----------|-----------|----------|
| Requirements | PostgreSQL | Retrieve user stories, acceptance criteria |
| Source Code | Git + Filesystem | Code examples, implementation patterns |
| Architecture | Neo4j + PostgreSQL | Design decisions, module relationships |
| Decisions | Neo4j + PostgreSQL | ADRs, previous design choices |
| API Specs | PostgreSQL + Filesystem | Available endpoints, request/response schemas |
| Test Cases | PostgreSQL + Filesystem | Test patterns, coverage data |
| Security Reports | PostgreSQL | Vulnerability findings, compliance issues |
| CI/CD History | PostgreSQL | Build results, deployment history |
| Logs | Blob Storage | Debugging info, error traces |
| Conversations | PostgreSQL | Discussion history, team decisions |

## 7.2 Storage Architecture

### PostgreSQL: Project State

```sql
-- Requirements & Artifacts
CREATE TABLE artifacts (
    id UUID PRIMARY KEY,
    artifact_type VARCHAR(50),  -- UserStory, Design, Code, etc.
    title VARCHAR(255),
    description TEXT,
    status VARCHAR(50),  -- NEW, PLANNED, IN_DEVELOPMENT, etc.
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(100),
    content JSONB,  -- Full artifact data
    version INT
);

-- Artifact Versions (immutable history)
CREATE TABLE artifact_versions (
    id UUID,
    version INT,
    content JSONB,
    timestamp TIMESTAMP,
    actor VARCHAR(100),
    change_reason VARCHAR(500),
    PRIMARY KEY (id, version)
);

-- State Transitions
CREATE TABLE state_transitions (
    id UUID PRIMARY KEY,
    artifact_id UUID REFERENCES artifacts(id),
    from_state VARCHAR(50),
    to_state VARCHAR(50),
    timestamp TIMESTAMP,
    actor VARCHAR(100),
    reason VARCHAR(500),
    gate_result JSONB
);

-- Quality Gate Results
CREATE TABLE gate_results (
    id UUID PRIMARY KEY,
    artifact_id UUID REFERENCES artifacts(id),
    gate_type VARCHAR(50),  -- CodeReview, Security, Testing, UAT
    status VARCHAR(20),  -- PASSED, FAILED, BLOCKED
    findings JSONB,  -- Detailed issues found
    timestamp TIMESTAMP,
    evaluated_by VARCHAR(100)
);
```

### Neo4j: Relationships & Decisions

```cypher
-- Architecture Decision Records (ADRs)
CREATE (adr:ADR {
    id: "adr-123",
    title: "Use event-driven architecture",
    status: "ACCEPTED",
    created: timestamp(),
    related_artifacts: ["story-100", "story-101"]
})

-- Module Relationships
CREATE (module1:Module {name: "auth"})
CREATE (module2:Module {name: "payment"})
CREATE (module1)-[:DEPENDS_ON]->(module2)

-- Decision Impact Analysis
(artifact1)-[:INFLUENCED_BY]->(adr1)
(artifact2)-[:INFLUENCED_BY]->(adr1)
(artifact2)-[:CONFLICTS_WITH]->(design1)
```

### ChromaDB: Vector Embeddings

```python
# Semantic search index
embeddings = {
    "story-100": vector_of("Create user authentication flow"),
    "design-50": vector_of("JWT-based authentication using OAuth2"),
    "code-snippet-1": vector_of("def validate_token(token): ..."),
}

# Enables queries like:
results = chromadb.search(
    query="How do we handle user login?",
    top_k=5
)
# Returns: [story-100, design-50, code-snippet-1, ...]
```

### Git Repository: Source Code History

```python
# Retrieve code examples
git_search.find_similar_function(
    query="parse JWT token",
    language="python",
    max_results=3
)
# Returns: [auth/jwt_parser.py:line_50, security/token.py:line_120, ...]

# Analyze file history
git_history.get_file_blame("src/auth/jwt_parser.py")
# Shows who wrote each line and when

# Review recent changes
git_log.recent_commits(since="7 days ago", files=["src/auth/*"])
# Returns: [commit1, commit2, ...]
```

### Filesystem/Blob Storage: Raw Artifacts

```
workspace/
├── docs/
│   ├── architecture/
│   │   ├── adr-001-event-driven.md
│   │   └── component-diagram.png
│   ├── api/
│   │   └── openapi.yaml
│   └── requirements/
│       └── features.md
├── src/
│   ├── (source code)
├── tests/
│   └── (test files)
└── logs/
    ├── deployment-2026-07-25.log
    └── security-scan-2026-07-25.log
```

## 7.3 Context Assembly Engine

### Query Types

The Knowledge Fabric supports multiple query types:

#### 1. Semantic Search
```python
results = knowledge_fabric.semantic_search(
    query="How do we handle database transactions?",
    context_type="code_and_design",
    max_results=5,
    min_similarity=0.7
)
# Returns ranked results: [(item, score), ...]
```

#### 2. Graph Traversal
```python
results = knowledge_fabric.graph_traverse(
    start_node="story-123",
    relationship_types=["DEPENDS_ON", "INFLUENCED_BY"],
    max_depth=3
)
# Returns all connected nodes (dependencies, decisions, conflicts)
```

#### 3. Full-Text Search
```python
results = knowledge_fabric.full_text_search(
    query="authentication security",
    fields=["title", "description"],
    artifact_types=["ADR", "Design"]
)
# Returns documents with matching text
```

#### 4. Similar Artifacts
```python
results = knowledge_fabric.find_similar(
    artifact_id="story-123",
    artifact_type="UserStory",
    similarity_threshold=0.75
)
# Returns stories with similar goals/patterns
```

## 7.4 Ingestion Pipeline

### Automatic Ingestion

When new artifacts are created or modified:

```python
class IngestionPipeline:
    def ingest_artifact(artifact):
        # 1. Store in PostgreSQL
        postgres.insert(artifact)
        
        # 2. Extract text and generate embeddings
        text = extract_text(artifact)
        embedding = embed_text(text)
        chromadb.insert(artifact.id, embedding)
        
        # 3. Extract relationships and update graph
        relationships = extract_relationships(artifact)
        for rel in relationships:
            neo4j.create_relationship(rel)
        
        # 4. If code, add to git
        if artifact.type == "Code":
            git.commit(artifact)
        
        # 5. Index in search engine
        search_index.add(artifact)
```

### Manual Ingestion

Agents can explicitly ingest context:

```python
knowledge_fabric.ingest(
    artifact_id="new-design-doc",
    artifact_type="Architecture",
    content=content,
    relationships={
        "influences": ["story-100", "story-101"],
        "conflicts_with": ["design-50"]
    }
)
```

## 7.5 Caching Strategy

### In-Memory Cache

Frequently accessed data is cached:

```python
class KnowledgeFabricCache:
    def get_artifact(artifact_id):
        # Check in-memory cache first
        if artifact_id in hot_cache:
            return hot_cache[artifact_id]
        
        # Miss: fetch from PostgreSQL
        artifact = postgres.fetch(artifact_id)
        hot_cache[artifact_id] = artifact  # Add to cache
        return artifact
    
    # Cache invalidation on update
    def update_artifact(artifact):
        postgres.update(artifact)
        if artifact.id in hot_cache:
            del hot_cache[artifact.id]  # Invalidate
```

### Cache Eviction

```
Cache: LRU (Least Recently Used)
Size: 1GB (configurable)
TTL: 1 hour (configurable)
```

---

# 8. Agent Framework

## 8.1 Agent Responsibilities

Each agent in Korame has well-defined responsibilities and cannot exceed them. This prevents agents from acting outside their domain and ensures clear accountability.

### RTE Agent
**Primary:** Requirements management, business planning, release decisions  
**Cannot Do:** Write code, approve code quality, run tests  
**Capabilities:**
- Parse business requirements in natural language
- Generate or refine user stories and acceptance criteria
- Create epics and organize backlog
- Approve artifacts for release
- Report on project status and metrics

### Architect Agent
**Primary:** Solution design, technical decisions  
**Cannot Do:** Write production code, approve deployments  
**Capabilities:**
- Analyze requirements and create architectural designs
- Document module decomposition and interfaces
- Record architectural decision records (ADRs)
- Design system scalability and resilience patterns
- Recommend technology selections

### Developer Agent
**Primary:** Implementation, unit testing  
**Cannot Do:** Approve own code, approve deployments  
**Capabilities:**
- Generate implementation code from designs
- Write unit tests covering their code
- Generate implementation documentation
- Fix issues identified by review gates
- Suggest code improvements

### Code Reviewer Agent
**Primary:** Code quality and standards enforcement  
**Cannot Do:** Approve security, approve deployment, approve testing strategy  
**Capabilities:**
- Review code against style guides
- Check documentation and comments
- Identify performance issues
- Suggest refactoring for maintainability
- Can block code with critical issues (→ BLOCKED status)

### Security Agent
**Primary:** Security validation and compliance  
**Cannot Do:** Write code, approve testing strategy  
**Capabilities:**
- Scan code for security vulnerabilities
- Check dependencies for known CVEs
- Verify no secrets in codebase
- Confirm compliance with security standards
- Can block code with security violations (→ BLOCKED status)

### Testing Agent
**Primary:** Automated test coverage and verification  
**Cannot Do:** Approve code quality, approve deployment  
**Capabilities:**
- Generate comprehensive test suites
- Execute tests and measure coverage
- Identify gaps in test coverage
- Can block code if coverage < 80% (→ BLOCKED status)

### UAT Agent
**Primary:** Business acceptance validation  
**Cannot Do:** Approve code quality, fix bugs, deploy code  
**Capabilities:**
- Execute business-level acceptance tests
- Validate against original requirements
- Can block deployment if requirements not met
- Provide feedback on business functionality

### DevOps Agent
**Primary:** Deployment orchestration and infrastructure  
**Cannot Do:** Approve code, approve business decisions  
**Capabilities:**
- Prepare deployment infrastructure
- Execute deployments (blue-green, canary)
- Monitor deployment health
- Trigger rollbacks if needed
- Report deployment status

---

# 9. Memory & RAG

## 9.1 Memory Architecture

Korame maintains multiple forms of memory to understand context and avoid repeating past mistakes:

### Short-Term Memory
Artifacts and events currently in pipeline:
- Current task being executed
- Recent event history (last 24 hours)
- Current project state
- TTL: 24 hours or until artifact completes

### Medium-Term Memory
Project knowledge and decisions:
- All requirements and designs for current/recent projects
- Architectural decisions and rationale
- Code patterns and examples
- Test patterns and coverage metrics
- TTL: 30 days or until project closes

### Long-Term Memory
Historical patterns and lessons learned:
- Similar projects and their outcomes
- Common failure patterns
- Best practices identified
- Dependency vulnerability history
- TTL: Indefinite

## 9.2 RAG (Retrieval-Augmented Generation)

### RAG Pipeline

When Developer Agent needs to write code:

```
1. Receive artifact:
   - Requirement: "Implement JWT token validation"
   - Design: "Use HS256 algorithm, 1-hour expiration"
   
2. Retrieve relevant knowledge:
   - Similar code examples (semantic search)
   - Design patterns (graph traversal)
   - Security best practices (knowledge fabric)
   - API specifications (full-text search)
   - Test patterns (similar artifacts)
   
3. Assemble context:
   - {
       "requirement": "Implement JWT token validation",
       "design": "...",
       "similar_code_examples": [...],
       "security_checklist": [...],
       "test_patterns": [...]
     }
   
4. Invoke LLM with context:
   - Prompt: "Based on these examples and best practices, implement JWT validation"
   - Model: Uses context to generate code
   
5. Validate output:
   - Check against design
   - Verify test coverage
   - Scan for security issues
   
6. Store in knowledge fabric:
   - New code added to examples
   - New patterns identified
   - Decisions recorded
```

### RAG Quality Metrics

```
Metric: Retrieval Precision
- Are retrieved examples actually relevant?
- Target: > 85%

Metric: Retrieval Recall
- Are all relevant examples retrieved?
- Target: > 90%

Metric: Generation Quality
- Does generated code follow retrieved patterns?
- Target: > 80% pass rate on code review

Metric: RAG Usefulness
- Does RAG improve agent quality vs. no context?
- Target: > 20% improvement in pass rates
```

---

# 10. Plugin Architecture

## 10.1 Plugin Philosophy

The Plugin Architecture allows extending Korame without modifying core components. Anyone can build a custom agent and integrate it into Korame by:

1. Implementing the Agent interface
2. Registering with Plugin Manager
3. Declaring event handlers and dependencies
4. Providing configuration schema

### Plugin Types

| Plugin Type | Example | Purpose |
|------------|---------|---------|
| Agent | Custom ReviewerAgent | Add domain-specific review logic |
| Model | LocalOllamaModel | Add new model provider |
| Storage | AzureBlobStorage | Add new storage backend |
| Analyzer | CachePerformanceAnalyzer | Add custom metrics/analysis |
| Transformer | CodeFormatterPlugin | Transform artifacts (formatting, refactoring) |

## 10.2 Plugin Interface

All plugins implement this interface:

```python
class Plugin:
    # Plugin metadata
    name: str
    version: str
    description: str
    author: str
    
    # Lifecycle
    def initialize(config: Config) -> None:
        """Called on plugin load"""
        pass
    
    def shutdown() -> None:
        """Called on plugin unload"""
        pass
    
    # Capability declaration
    def get_capabilities() -> PluginCapabilities:
        return {
            "handles_events": ["TaskReady"],
            "publishes_events": ["TaskComplete", "TaskFailed"],
            "data_sources": ["Knowledge_Fabric"],
            "config_schema": {...}
        }
    
    # Dependency declaration
    def get_dependencies() -> List[Dependency]:
        return [
            Dependency(plugin="SecurityScanner", version=">=1.0"),
        ]
```

## 10.3 Plugin Lifecycle

### Registration

```python
plugin_manager.register(
    plugin_class=CustomReviewerAgent,
    config={
        "enabled": True,
        "priority": 10,
        "custom_rules_file": "/path/to/rules.yaml"
    }
)
```

### Loading

```
On startup:
  1. Scan plugin directory
  2. Load plugin metadata
  3. Check dependencies (must load in order)
  4. Validate configuration against schema
  5. Call plugin.initialize()
  6. Register event handlers
  7. Notify Orchestrator of new agent
```

### Execution

```
When plugin event arrives:
  1. Look up handler in plugin registry
  2. Check preconditions (state, gates, dependencies)
  3. Assemble context
  4. Invoke plugin handler
  5. Validate output format
  6. Publish completion event
  7. Log execution metadata
```

### Unloading

```
On shutdown or plugin removal:
  1. Drain in-flight tasks
  2. Call plugin.shutdown()
  3. Deregister event handlers
  4. Notify Orchestrator
  5. Clean up resources
  6. Allow pending tasks to fail gracefully
```

---

# 11. Event Bus

## 11.1 Event Bus Architecture

The Event Bus (Redis) is the communication backbone of Korame. All inter-agent communication flows through the Event Bus using a publish-subscribe model.

### Core Concepts

**Topic:** Event routing path (e.g., "task.code_review.ready", "gate.security.failed")  
**Event:** Message published to topic (contains artifact_id, payload, etc.)  
**Publisher:** Agent emitting the event (e.g., Developer Agent)  
**Subscriber:** Agent listening for events (e.g., Code Reviewer Agent)  

### Event Categories

```
Task Lifecycle Events:
  - task.{task_type}.ready      (new task available)
  - task.{task_type}.started    (agent started work)
  - task.{task_type}.completed  (agent finished, success)
  - task.{task_type}.failed     (agent finished, failure)

Gate Events:
  - gate.code_review.passed
  - gate.code_review.failed
  - gate.security.blocked
  - ...

State Transition Events:
  - artifact.state.changed
  - artifact.state.transition_failed

System Events:
  - agent.heartbeat
  - agent.unavailable
  - system.error
```

## 11.2 Event Schema

All events follow a standard schema:

```json
{
  "event_id": "uuid",
  "event_type": "task.code_review.completed",
  "timestamp": "2026-07-25T11:30:00Z",
  "correlation_id": "uuid",
  "causation_id": "previous_event_id",
  
  "artifact": {
    "id": "story-123",
    "type": "UserStory"
  },
  
  "source": {
    "agent": "developer-agent",
    "task": "code_generation",
    "instance": "dev-agent-1"
  },
  
  "payload": {
    "status": "success",
    "code": "...",
    "test_coverage": 0.85,
    "duration_ms": 12000
  },
  
  "errors": null  // or { "code": "ERROR_CODE", "message": "..." }
}
```

## 11.3 Event Bus Implementation (Redis)

```python
class EventBus:
    def __init__(self, redis_url="redis://localhost:6379"):
        self.redis = redis.from_url(redis_url)
    
    def publish(event: Event):
        """Publish event to all subscribers"""
        topic = f"{event.event_type}"
        self.redis.publish(topic, json.dumps(event.to_dict()))
        self.redis.lpush(f"audit_log:{event.artifact_id}", event.to_json())
    
    def subscribe(listener_id: str, topics: List[str]):
        """Subscribe listener to events"""
        pubsub = self.redis.pubsub()
        pubsub.subscribe(*topics)
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                event = Event.from_dict(json.loads(message['data']))
                handle_event(event)
    
    def get_audit_log(artifact_id: str):
        """Retrieve immutable audit log for artifact"""
        events = self.redis.lrange(f"audit_log:{artifact_id}", 0, -1)
        return [Event.from_json(e) for e in events]
    
    def replay_events(artifact_id: str, from_event_id: str):
        """Replay events from specific point (for recovery)"""
        events = self.get_audit_log(artifact_id)
        start_idx = next(i for i, e in enumerate(events) if e.event_id == from_event_id)
        for event in events[start_idx:]:
            self.publish(event)
```

## 11.4 Guaranteed Delivery

### Ordering Guarantees

Within a single artifact:
- Events processed serially
- Prevents race conditions in state machine

Across different artifacts:
- Events processed concurrently
- No ordering guarantees

### At-Least-Once Delivery

```python
# Handler acknowledges only after successful processing
def handle_event(event):
    try:
        process_event(event)
        # Only acknowledge after processing complete
        acknowledge(event.event_id)
    except Exception as e:
        # Negative acknowledge; event will be replayed
        negative_acknowledge(event.event_id)
        log_error(e)
```

### Dead Letter Queue

```python
# Undeliverable events after retries
if max_retries_exceeded:
    dead_letter_queue.add({
        "original_event": event,
        "failed_at": now,
        "error_reason": error_msg,
        "requires_manual_intervention": True
    })
    alert_operator()
```

---

# 12. Model Router

## 12.1 Model Routing Philosophy

Rather than binding each agent to a single LLM, the Model Router dynamically selects the most appropriate model based on:

- **Task Complexity:** Simple tasks use smaller, faster models; complex tasks use larger models
- **Context Length:** Tasks needing many examples use models with larger context windows
- **Latency Requirements:** UAT/deployment tasks need fast inference
- **Cost Optimization:** Prefer cheaper models when quality is similar
- **GPU Availability:** Route to available infrastructure (local/Azure)
- **Model Specialty:** Some models excel at reasoning, others at code generation

### Execution Strategy

```
┌─────────────────────────────────────┐
│   Agent Requests Task Execution     │
│   (e.g., "Generate JWT validation") │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│    Model Router                     │
│                                     │
│  1. Classify task complexity        │
│  2. Estimate context requirements   │
│  3. Check resource availability     │
│  4. Rank candidate models           │
│  5. Select primary model            │
│  6. Identify fallback models        │
└────────────┬────────────────────────┘
             │
      ┌──────┴──────┬──────────┐
      │             │          │
      ▼             ▼          ▼
  Local GPU    Local CPU    Azure GPU
  (Ollama)     (Small LM)   (Premium)
```

## 12.2 Model Registry

### Supported Models

| Model | Provider | Specialty | Context | Speed | Cost | Best For |
|-------|----------|-----------|---------|-------|------|----------|
| Qwen3 8B | Ollama | General | 4K | Fast | Free | Requirements, planning |
| Llama2 13B | Ollama | Reasoning | 4K | Medium | Free | Architecture |
| Code Llama 7B | Ollama | Code gen | 4K | Medium | Free | Development |
| GPT-4-32K | Azure | Reasoning | 32K | Slow | High | Complex decisions |
| Claude 3 | Azure | Analysis | 100K | Medium | Medium | Security review |
| Grok-1 | Azure | Code + Reasoning | 16K | Medium | Medium | Testing strategy |

## 12.3 Model Selection Algorithm

```python
def select_model(task: Task) -> ModelSelection:
    # Step 1: Classify task
    task_class = classify_task(task.type, task.complexity)
    # Returns: "simple", "medium", "complex", "special_reasoning"
    
    # Step 2: Determine context budget
    context_budget = estimate_context_needs(
        task_description=task.description,
        artifact_size=len(task.artifact),
        examples_needed=count_examples(task.type)
    )
    
    # Step 3: Check infrastructure availability
    available_local = check_local_gpu_availability()  # Ollama
    available_azure = check_azure_gpu_availability()  # Azure GPU pool
    
    # Step 4: Candidate models based on class
    candidates = {
        "simple": [Qwen3_8B, Llama2_13B],
        "medium": [Llama2_13B, CodeLlama_7B],
        "complex": [GPT4_32K, Claude3],
        "special_reasoning": [Grok1, GPT4_32K]
    }[task_class]
    
    # Step 5: Filter by availability + score
    best_model = None
    for model in candidates:
        if task_class == "simple" and available_local:
            return Model(name=Qwen3_8B, location="local", priority=1)
        elif task_class == "medium" and available_local:
            return Model(name=CodeLlama_7B, location="local", priority=1)
        elif available_azure and model in azure_models:
            return Model(name=model, location="azure", priority=2)
    
    # Step 6: Fallback strategy
    return get_primary_fallback() or raise InsufficientResourcesError()
```

## 12.4 Fallback Strategy

```python
class FallbackStrategy:
    def get_fallback_models(primary: Model) -> List[Model]:
        """Return fallback models in priority order"""
        
        # Example fallback chain for Code Llama:
        return [
            Model(CodeLlama_13B, location="azure"),    # Similar, larger
            Model(Llama2_13B, location="local"),        # Local fallback
            Model(GPT4, location="azure"),              # Premium fallback
        ]
    
    def handle_model_failure(model: Model, error: Exception):
        """Route to next available model"""
        next_model = get_fallback_models(model)[0]
        log_model_downgrade(from_model=model, to_model=next_model)
        return retry_with_model(next_model)
```

## 12.5 Cost Optimization

```python
class CostOptimizer:
    # Token pricing per model
    pricing = {
        "Qwen3_8B": 0,  # Free (local)
        "CodeLlama_7B": 0,  # Free (local)
        "GPT4_32K": 0.06 / 1000,  # $0.06 per 1K tokens
        "Claude3": 0.015 / 1000,  # $0.015 per 1K tokens
    }
    
    def estimate_cost(model: Model, task: Task) -> float:
        """Estimate cost of running task on model"""
        estimated_tokens = estimate_tokens(task)
        rate = pricing[model.name]
        return estimated_tokens * rate
    
    def should_use_premium(task: Task) -> bool:
        """Decide if task complexity justifies premium model cost"""
        
        # For high-value tasks, always use best model regardless of cost
        if task.priority == "CRITICAL":
            return True
        
        # For tasks where output quality impacts downstream work:
        if task.type in ["ArchitectureDesign", "SecurityReview"]:
            cost = estimate_cost(premium_model, task)
            risk_of_rework = estimate_rework_probability(task)
            rework_cost = cost_of_rework(task)
            
            # If rework cost > premium cost, use premium
            return (risk_of_rework * rework_cost) > cost
        
        # Default: use cheapest model
        return False
```

---

# 13. Agent SDK

## 13.1 SDK Overview

The Agent SDK provides a standardized interface for all agents to:
- Receive tasks
- Access context (Knowledge Fabric)
- Invoke LLMs (via Model Router)
- Emit completion/failure events
- Log and trace execution

### SDK Components

```python
class KorameAgentSDK:
    # Core components
    event_bus: EventBus              # Publish/subscribe
    knowledge_fabric: KnowledgeFabric # Retrieve context
    model_router: ModelRouter         # Select & invoke LLMs
    artifact_manager: ArtifactManager  # Store/retrieve artifacts
    configuration: Configuration      # Agent-specific config
    logger: Logger                    # Structured logging
    
    # Utilities
    context_assembler: ContextAssembler
    validation: SchemaValidator
    metrics: MetricsCollector
```

## 13.2 Agent Implementation Template

```python
from korame.sdk import Agent, EventBus, KnowledgeFabric, ModelRouter
from korame.events import TaskReady, TaskComplete, TaskFailed

class MyCustomAgent(Agent):
    def __init__(self, config):
        self.event_bus = EventBus(config.redis_url)
        self.knowledge_fabric = KnowledgeFabric(config.db_urls)
        self.model_router = ModelRouter(config.model_config)
        self.config = config
    
    def initialize(self):
        """Called on startup"""
        # Subscribe to relevant events
        self.event_bus.subscribe(
            listener_id="my-agent",
            topics=["task.my_task_type.ready"]
        )
    
    def can_handle(self, event: Event) -> bool:
        """Check if this agent should handle the event"""
        return event.event_type == "task.my_task_type.ready"
    
    def execute(self, artifact, context, config):
        """Main execution method"""
        
        # 1. Validate input
        self.validate_input(artifact, context)
        
        # 2. Retrieve additional context
        additional_context = self.knowledge_fabric.get_context(
            artifact_id=artifact.id,
            context_types=["similar_artifacts", "decisions"]
        )
        
        # 3. Select model
        model = self.model_router.select_model(
            task_type=artifact.type,
            complexity=artifact.complexity,
            context_size=len(context)
        )
        
        # 4. Invoke model with context
        prompt = self.build_prompt(artifact, context, additional_context)
        result = model.invoke(prompt, max_tokens=2000)
        
        # 5. Validate output
        validated_result = self.validate_output(result)
        
        # 6. Store result
        artifact.result = validated_result
        self.artifact_manager.update(artifact)
        
        # 7. Emit completion event
        self.event_bus.publish(TaskComplete(
            artifact_id=artifact.id,
            agent=self.name,
            status="success",
            result=validated_result
        ))
        
        return validated_result
    
    def build_prompt(self, artifact, context, additional_context):
        """Construct prompt for LLM"""
        return f"""
        Task: {artifact.description}
        
        Context:
        {json.dumps(context, indent=2)}
        
        Additional Examples:
        {json.dumps(additional_context, indent=2)}
        
        Instructions:
        - Follow the existing patterns shown in examples
        - Ensure output conforms to schema
        - Include comments explaining logic
        """
    
    def validate_output(self, output):
        """Validate model output against expected schema"""
        schema = self.config.get_output_schema()
        validator = SchemaValidator(schema)
        return validator.validate(output)
```

## 13.3 SDK APIs

### Event Publishing

```python
def publish_event(event_type: str, payload: dict):
    """Publish event to event bus"""
    event = Event(
        event_type=event_type,
        artifact_id=self.current_artifact_id,
        source_agent=self.agent_name,
        payload=payload,
        timestamp=now(),
        correlation_id=get_correlation_id()
    )
    self.event_bus.publish(event)
```

### Knowledge Fabric Access

```python
def query_knowledge(query: str, context_type: str):
    """Query knowledge fabric for context"""
    results = self.knowledge_fabric.search(
        query=query,
        context_type=context_type,  # "code", "design", "decisions", etc.
        max_results=5,
        min_similarity=0.7
    )
    return results

def get_artifact_context(artifact_id: str):
    """Get all available context for artifact"""
    context = self.knowledge_fabric.get_full_context(artifact_id)
    return context
```

### Model Invocation

```python
def invoke_model(prompt: str, model_hint: str = None):
    """Invoke LLM with automatic model selection"""
    model = self.model_router.select_model(
        task_type=self.current_task_type,
        complexity=self.estimate_complexity(prompt),
        preferred_model=model_hint
    )
    
    result = model.invoke(
        prompt=prompt,
        max_tokens=2000,
        temperature=0.7
    )
    
    return result
```

### Logging & Metrics

```python
def log(self, level: str, message: str, context: dict = None):
    """Log message with context"""
    self.logger.log(
        level=level,
        message=message,
        correlation_id=get_correlation_id(),
        artifact_id=self.current_artifact_id,
        context=context
    )

def record_metric(name: str, value: float, unit: str = ""):
    """Record metric for monitoring"""
    self.metrics.record(
        name=name,
        value=value,
        unit=unit,
        timestamp=now(),
        agent=self.agent_name
    )
```

---

# 14. APIs

## 14.1 Orchestrator API

### Create Artifact

```http
POST /api/v1/artifacts
Content-Type: application/json
Authorization: Bearer <token>

{
  "type": "UserStory",
  "title": "Implement JWT token validation",
  "description": "As a developer, I want JWT tokens to be validated...",
  "acceptance_criteria": [
    "Validates token signature",
    "Checks token expiration",
    "Returns clear error messages"
  ],
  "priority": "HIGH",
  "estimated_hours": 8
}

Response:
{
  "id": "story-123",
  "status": "NEW",
  "created_at": "2026-07-25T10:00Z",
  "_links": {
    "self": "/api/v1/artifacts/story-123",
    "state": "/api/v1/artifacts/story-123/state"
  }
}
```

### Get Artifact State

```http
GET /api/v1/artifacts/story-123/state
Authorization: Bearer <token>

Response:
{
  "artifact_id": "story-123",
  "current_state": "IN_DEVELOPMENT",
  "history": [
    {"state": "NEW", "timestamp": "2026-07-25T10:00Z", "actor": "rte-agent"},
    {"state": "PLANNED", "timestamp": "2026-07-25T10:05Z", "actor": "rte-agent"},
    {"state": "ARCHITECTED", "timestamp": "2026-07-25T10:15Z", "actor": "architect-agent"},
    {"state": "IN_DEVELOPMENT", "timestamp": "2026-07-25T10:20Z", "actor": "developer-agent"}
  ],
  "gates": {
    "code_review": "PENDING",
    "security": "PENDING",
    "testing": "PENDING"
  }
}
```

### Get Audit Log

```http
GET /api/v1/artifacts/story-123/audit
Authorization: Bearer <token>

Response:
{
  "artifact_id": "story-123",
  "events": [
    {
      "event_id": "evt-123",
      "timestamp": "2026-07-25T10:00Z",
      "action": "StateTransition",
      "from_state": "NEW",
      "to_state": "PLANNED",
      "actor": "rte-agent",
      "reason": "Story approved by RTE"
    },
    ...
  ]
}
```

## 14.2 Knowledge Fabric API

### Semantic Search

```http
GET /api/v1/knowledge/search?q=JWT+validation&type=code&limit=5
Authorization: Bearer <token>

Response:
{
  "query": "JWT validation",
  "results": [
    {
      "artifact_id": "code-123",
      "artifact_type": "CodeSnippet",
      "title": "validate_jwt_token function",
      "similarity": 0.94,
      "excerpt": "def validate_jwt_token(token):\n    # Validate JWT signature...",
      "_links": {"self": "/api/v1/artifacts/code-123"}
    },
    ...
  ]
}
```

### Graph Traversal

```http
POST /api/v1/knowledge/graph/traverse
Content-Type: application/json
Authorization: Bearer <token>

{
  "start_node": "story-123",
  "relationship_types": ["DEPENDS_ON", "INFLUENCED_BY"],
  "max_depth": 3
}

Response:
{
  "nodes": [
    {"id": "story-123", "type": "UserStory", ...},
    {"id": "design-50", "type": "Architecture", ...},
    {"id": "adr-5", "type": "ADR", ...}
  ],
  "edges": [
    {"from": "story-123", "to": "design-50", "relationship": "INFLUENCED_BY"},
    {"from": "design-50", "to": "adr-5", "relationship": "BASED_ON"}
  ]
}
```

## 14.3 Metrics & Monitoring API

### Get Pipeline Metrics

```http
GET /api/v1/metrics/pipeline?timerange=7d
Authorization: Bearer <token>

Response:
{
  "timerange": "7 days",
  "artifacts_created": 42,
  "artifacts_completed": 38,
  "artifacts_in_progress": 4,
  "average_pipeline_time": "4.2 hours",
  "gate_pass_rates": {
    "code_review": 0.95,
    "security": 0.98,
    "testing": 0.92,
    "uat": 0.88
  },
  "most_common_failures": [
    {
      "gate": "testing",
      "reason": "Coverage < 80%",
      "frequency": 0.08
    }
  ]
}
```

---

# 15. Data Model

## 15.1 Core Entities

### Artifact

```python
@dataclass
class Artifact:
    id: str  # UUID
    artifact_type: str  # "UserStory", "Design", "Code", etc.
    title: str
    description: str
    
    # Lifecycle
    status: ArtifactStatus  # NEW, PLANNED, IN_DEVELOPMENT, etc.
    created_at: datetime
    updated_at: datetime
    created_by: str  # Agent that created this
    
    # Content (type-specific)
    content: dict  # Full artifact data (story, design doc, code, etc.)
    version: int
    
    # Relationships
    parent_epic_id: Optional[str]
    related_artifacts: List[str]  # IDs of related artifacts
    
    # Gates
    quality_gates: Dict[str, GateResult]  # CodeReview, Security, Testing, UAT
    
    # Metadata
    priority: Priority  # LOW, MEDIUM, HIGH, CRITICAL
    estimated_hours: Optional[float]
    acceptance_criteria: List[str]
    tags: List[str]
```

### Event

```python
@dataclass
class Event:
    event_id: str  # UUID
    event_type: str
    timestamp: datetime
    correlation_id: str  # Groups related events
    causation_id: Optional[str]  # Event that triggered this
    
    artifact: ArtifactRef  # Minimal artifact info
    source: EventSource  # Who published this
    payload: dict  # Event-specific data
    errors: Optional[ErrorInfo]
```

### GateResult

```python
@dataclass
class GateResult:
    gate_type: str  # "CodeReview", "Security", "Testing", "UAT"
    status: str  # "PASSED", "FAILED", "BLOCKED", "PENDING"
    evaluated_at: datetime
    evaluated_by: str  # Agent that evaluated
    findings: List[Finding]  # Issues discovered
    evidence: dict  # Supporting data (coverage %, scan results, etc.)
```

### Finding

```python
@dataclass
class Finding:
    id: str
    severity: str  # "INFO", "WARN", "ERROR", "CRITICAL"
    category: str  # "CodeQuality", "Security", "Performance", etc.
    message: str
    location: Optional[str]  # File:line if applicable
    suggestion: Optional[str]  # How to fix
```

---

# 16. Repository Structure

The Korame repository is organized to support parallel development of core components, agents, and integrations.

```
korame/
│
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── Dockerfile
├── docker-compose.yml
│
├── docs/
│   ├── KORAME-SAS.md          # This file
│   ├── ADRs/
│   │   ├── adr-001-event-driven.md
│   │   ├── adr-002-model-agnostic.md
│   │   └── ...
│   ├── API/
│   │   ├── orchestrator-api.md
│   │   ├── agent-sdk.md
│   │   └── knowledge-fabric-api.md
│   └── DEVELOPMENT.md
│
├── src/
│   ├── korame/
│   │   ├── __init__.py
│   │   │
│   │   ├── kernel/
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py         # Workflow Orchestrator
│   │   │   ├── event_bus.py            # Event Bus
│   │   │   ├── artifact_manager.py     # Artifact Manager
│   │   │   ├── configuration.py        # Config Manager
│   │   │   └── plugin_manager.py       # Plugin Manager
│   │   │
│   │   ├── sdk/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py                # Base Agent class
│   │   │   ├── context.py              # Context assembly
│   │   │   └── decorators.py           # Agent decorators
│   │   │
│   │   ├── knowledge/
│   │   │   ├── __init__.py
│   │   │   ├── fabric.py               # Knowledge Fabric interface
│   │   │   ├── storage/
│   │   │   │   ├── postgres_store.py
│   │   │   │   ├── neo4j_store.py
│   │   │   │   ├── chromadb_store.py
│   │   │   │   └── git_store.py
│   │   │   └── ingestion/
│   │   │       ├── artifact_ingester.py
│   │   │       └── code_indexer.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── router.py               # Model Router
│   │   │   ├── providers/
│   │   │   │   ├── ollama.py
│   │   │   │   ├── azure_gpt.py
│   │   │   │   └── anthropic.py
│   │   │   └── cache.py
│   │   │
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── rte_agent.py            # Release Train Engineer
│   │   │   ├── architect_agent.py      # Architect
│   │   │   ├── developer_agent.py      # Developer
│   │   │   ├── reviewer_agent.py       # Code Reviewer
│   │   │   ├── security_agent.py       # Security
│   │   │   ├── testing_agent.py        # Testing
│   │   │   ├── uat_agent.py            # UAT
│   │   │   └── devops_agent.py         # DevOps
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── main.py                 # FastAPI app
│   │   │   ├── routes/
│   │   │   │   ├── artifacts.py
│   │   │   │   ├── knowledge.py
│   │   │   │   ├── metrics.py
│   │   │   │   └── admin.py
│   │   │   └── auth.py
│   │   │
│   │   ├── observability/
│   │   │   ├── __init__.py
│   │   │   ├── logging.py              # Structured logging
│   │   │   ├── tracing.py              # Distributed tracing
│   │   │   ├── metrics.py              # Metrics collection
│   │   │   └── alerts.py               # Alerting
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── validation.py
│   │       ├── serialization.py
│   │       └── retry.py
│   │
│   └── tests/
│       ├── __init__.py
│       ├── unit/
│       │   ├── test_orchestrator.py
│       │   ├── test_event_bus.py
│       │   ├── test_agent_sdk.py
│       │   └── ...
│       ├── integration/
│       │   ├── test_artifact_lifecycle.py
│       │   ├── test_gate_enforcement.py
│       │   └── ...
│       └── fixtures/
│           └── sample_artifacts.py
│
├── config/
│   ├── local.yaml              # Local development config
│   ├── docker.yaml             # Docker environment config
│   ├── azure.yaml              # Azure deployment config
│   └── agents/
│       ├── developer.yaml      # Developer Agent config
│       ├── security.yaml       # Security Agent config
│       └── ...
│
├── plugins/
│   └── examples/
│       └── custom_reviewer/    # Example plugin
│           ├── plugin.py
│           ├── config.yaml
│           └── tests/
│
├── scripts/
│   ├── init_db.py              # Initialize databases
│   ├── migrate.py              # Database migrations
│   ├── seed_knowledge.py       # Seed with sample data
│   └── deploy.sh               # Deployment scripts
│
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Development dependencies
└── .github/
    └── workflows/
        ├── test.yml            # Test pipeline
        ├── lint.yml            # Code quality
        └── build.yml           # Docker build
```

---

# 17. Deployment Architecture

## 17.1 Local Development Environment

For development and initial testing:

```
Developer Laptop
├── Korame Container (Docker)
│   ├── Python 3.11
│   ├── FastAPI server
│   ├── Workflow Orchestrator
│   ├── Agent pool (RTE, Architect, Developer, etc.)
│   └── Event bus client
│
├── Infrastructure Containers
│   ├── Redis (event bus)
│   ├── PostgreSQL (project state)
│   ├── Neo4j (relationships)
│   └── ChromaDB (embeddings)
│
└── Local Models (Ollama)
    ├── Qwen3 8B
    ├── Llama2 13B
    └── Code Llama 7B
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  korame:
    image: korame:latest
    ports:
      - "8000:8000"  # API
    environment:
      REDIS_URL: redis://redis:6379
      DATABASE_URL: postgresql://postgres:password@postgres:5432/korame
    depends_on:
      - redis
      - postgres
      - neo4j
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: korame
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
  
  neo4j:
    image: neo4j:5-community
    environment:
      NEO4J_AUTH: neo4j/password
    ports:
      - "7687:7687"
      - "7474:7474"

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
```

## 17.2 Azure Cloud Deployment

For production deployment:

```
Azure Resource Group: Korame
├── AKS Cluster
│   ├── Orchestrator Pod (replicas=3)
│   ├── Agent Pool (autoscale 1-10 pods)
│   ├── Redis Pod (replicas=3)
│   └── System Pod (logging, monitoring)
│
├── Data Services
│   ├── Azure Database for PostgreSQL (managed)
│   ├── Azure Cosmos DB (Neo4j compatibility, future)
│   └── Azure Blob Storage (artifacts, logs)
│
├── GPU Worker Pool
│   ├── NV100 nodes (NVIDIA A100 GPU)
│   ├── Auto-scaling based on workload
│   └── Model inference service
│
├── Networking
│   ├── Virtual Network
│   ├── Application Gateway (load balancer)
│   └── Private Link (secure connections)
│
└── Monitoring
    ├── Application Insights
    ├── Azure Monitor
    └── Log Analytics
```

### Kubernetes Deployment Manifest (AKS)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: korame-orchestrator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: korame-orchestrator
  template:
    metadata:
      labels:
        app: korame-orchestrator
    spec:
      containers:
      - name: orchestrator
        image: korame-registry.azurecr.io/korame:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: korame-config
              key: redis_url
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: korame-secrets
              key: database_url
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: korame-agent-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: korame-agent-pool
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## 17.3 Hybrid Execution Strategy

```
┌──────────────────────────────────────┐
│   Workflow Orchestrator (local)      │
│   - Task scheduling                  │
│   - State management                 │
│   - Context assembly                 │
└─────────┬──────────────┬─────────────┘
          │              │
          │              │
    ┌─────▼──┐      ┌────▼─────┐
    │ Local  │      │   Azure   │
    │ GPU    │      │   GPU     │
    │ Pool   │      │   Pool    │
    │        │      │           │
    │Simple  │      │ Complex   │
    │tasks   │      │ tasks     │
    │Fast    │      │ High-qual │
    │Free    │      │ Expensive │
    └────────┘      └───────────┘
```

### Task Routing Rules

```
Simple tasks (< 500 tokens) → Local GPU (Ollama)
Medium tasks (500-2K tokens) → Local GPU if available, else Azure
Complex tasks (> 2K tokens) → Azure GPU (premium models)
Code generation → Azure if available (higher quality)
Security review → Azure (need reasoning capability)
Testing strategy → Azure (complex reasoning)
```

---

# 18. Security

## 18.1 Authentication & Authorization

### API Authentication

All APIs require Bearer token (JWT):

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Role-Based Access Control (RBAC)

```python
class Role(Enum):
    RTE = "rte"                    # Business owner, approves releases
    ARCHITECT = "architect"        # Design authority
    DEVELOPER = "developer"        # Implementation
    REVIEWER = "reviewer"          # Code quality
    SECURITY = "security"          # Security validation
    TESTING = "testing"            # QA & testing
    UAT = "uat"                    # Business acceptance
    DEVOPS = "devops"              # Deployment & infrastructure
    ADMIN = "admin"                # System administration

class Permission(Enum):
    # Artifact management
    CREATE_ARTIFACT = "create_artifact"
    READ_ARTIFACT = "read_artifact"
    UPDATE_ARTIFACT = "update_artifact"
    
    # Gate management
    APPROVE_GATE = "approve_gate"
    BLOCK_GATE = "block_gate"
    
    # Deployment
    APPROVE_DEPLOYMENT = "approve_deployment"
    DEPLOY = "deploy"
    
    # Admin
    MANAGE_USERS = "manage_users"
    VIEW_AUDIT_LOG = "view_audit_log"
```

### Permission Matrix

| Role | Create | Review | Approve Gate | Approve UAT | Deploy |
|------|--------|--------|--------------|-------------|--------|
| RTE | ✓ | - | - | ✓ | - |
| Architect | - | ✓ | - | - | - |
| Developer | - | ✓ | - | - | - |
| Reviewer | - | ✓ | ✓ | - | - |
| Security | - | ✓ | ✓ | - | - |
| Testing | - | ✓ | ✓ | - | - |
| UAT | - | - | - | ✓ | - |
| DevOps | - | - | - | - | ✓ |
| Admin | ✓ | ✓ | ✓ | ✓ | ✓ |

## 18.2 Data Protection

### Encryption at Rest

```yaml
PostgreSQL:
  - Transparent Data Encryption (TDE) enabled
  - Key management: Azure Key Vault (production)

Neo4j:
  - Database encryption enabled
  - Connection encryption: TLS 1.3

Artifacts/Logs:
  - Azure Blob Storage: encryption at rest
  - Algorithm: AES-256
  - Key rotation: yearly
```

### Encryption in Transit

```
All APIs:
  - TLS 1.3 minimum
  - Certificate pinning (production)

Event Bus (Redis):
  - TLS encryption
  - AUTH password required

Database connections:
  - TLS required
  - Connection pooling with encrypted connections
```

### Secret Management

```
Sensitive Data Types:
  - Database credentials
  - API keys (LLM providers)
  - JWT signing keys
  - TLS certificates

Storage:
  - Never stored in code/config files
  - Azure Key Vault (production)
  - .env file (development, git-ignored)
  - Environment variables (deployment)

Access Control:
  - Minimal privilege (service accounts)
  - Rotation policy: quarterly
  - Audit logging of access
```

### No Secrets in Logs

```python
class SecureLogger:
    def sanitize_log(self, message: str) -> str:
        """Remove secrets from log messages"""
        patterns = [
            r'password["\']?\s*[:=]\s*["\']?([^"\'}\s]+)',
            r'token["\']?\s*[:=]\s*["\']?([^"\'}\s]+)',
            r'key["\']?\s*[:=]\s*["\']?([^"\'}\s]+)',
            r'secret["\']?\s*[:=]\s*["\']?([^"\'}\s]+)',
        ]
        for pattern in patterns:
            message = re.sub(pattern, r'\1***REDACTED***', message)
        return message
```

## 18.3 Vulnerability Management

### Dependency Scanning

```
Tools:
  - pip-audit (Python)
  - OWASP Dependency-Check
  - GitHub Dependabot

Scan Frequency:
  - On every commit (CI/CD)
  - Daily automated scan
  - Monthly manual audit

Policy:
  - Zero tolerance for HIGH/CRITICAL CVEs
  - Block deployment if unfixed CRITICAL CVEs
  - Quarterly review of MEDIUM CVEs
```

### Code Security Scanning

```
Tools:
  - Bandit (Python security issues)
  - SonarQube (code quality & security)
  - OWASP ZAP (API security testing)

Checks:
  - SQL injection prevention
  - XSS prevention
  - CSRF protection
  - Authentication bypass
  - Authorization bypass
  - Insecure deserialization
  - Secrets in code

Policy:
  - Block deployment if HIGH/CRITICAL issues
  - Fix before merge if MEDIUM issues
```

## 18.4 Audit & Compliance

### Audit Logging

```python
class AuditLogger:
    def log_action(self, action: str, actor: str, resource_id: str, result: str):
        """Log all significant actions"""
        log_entry = {
            "timestamp": now(),
            "action": action,
            "actor": actor,
            "resource_id": resource_id,
            "result": result,
            "ip_address": get_request_ip(),
            "user_agent": get_user_agent(),
            "correlation_id": get_correlation_id(),
            # Hash prevents tampering
            "hash": sha256(entry_string).hexdigest()
        }
        
        # Write to immutable log store
        self.immutable_log.append(log_entry)
```

### Compliance Requirements

```
OWASP Top 10:
  ✓ 1. Broken Access Control - RBAC enforced
  ✓ 2. Cryptographic Failures - TLS + encryption at rest
  ✓ 3. Injection - Parameterized queries, input validation
  ✓ 4. Insecure Design - Threat modeling + secure defaults
  ✓ 5. Security Misconfiguration - Hardened defaults
  ✓ 6. Vulnerable Components - Dependency scanning
  ✓ 7. Auth Failures - JWT + RBAC
  ✓ 8. Data Integrity Failures - Immutable audit log
  ✓ 9. Logging Failures - Comprehensive audit trail
  ✓ 10. SSRF - No external URL fetching

GDPR (if applicable):
  - Data minimization: Only store necessary data
  - Right to be forgotten: Data retention policy
  - Privacy by design: Encryption, access controls
  - Consent management: User acknowledgment
```

---

# 19. Observability

## 19.1 Logging

### Structured Logging

```json
{
  "timestamp": "2026-07-25T11:30:00Z",
  "level": "INFO",
  "logger": "korame.orchestrator",
  "message": "Artifact transitioned",
  "correlation_id": "corr-123",
  "artifact_id": "story-123",
  "from_state": "IN_DEVELOPMENT",
  "to_state": "CODE_REVIEW",
  "actor": "developer-agent",
  "duration_ms": 12000,
  "metadata": {
    "module": "state_machine",
    "function": "transition",
    "line": 245
  }
}
```

### Log Levels

```
DEBUG: Detailed execution flow, variable values (development only)
INFO: Significant actions, state transitions, milestone events
WARN: Unexpected conditions, degraded performance, retries
ERROR: Operation failure, exception, invalid state
CRITICAL: System failure, data integrity issue, security incident
```

### Log Retention

```
Local Development: 7 days
Staging: 30 days
Production: 90 days (audit trail longer)
Compliance: 7 years (for regulated data)
```

## 19.2 Distributed Tracing

### Correlation IDs

Every request gets a unique correlation_id that flows through the entire pipeline:

```
User Request
    │
    ├─ Correlation ID: corr-123
    │
    ├─ RTE Agent: Process requirement
    │   └─ Event: task.architecture.ready [corr-123]
    │
    ├─ Architect Agent: Generate design
    │   └─ Event: task.code_generation.ready [corr-123]
    │
    ├─ Developer Agent: Generate code
    │   └─ Event: task.code_review.ready [corr-123]
    │
    └─ (continues through all gates)
```

### Trace Example

```
Trace: story-123-review
├─ Span: code_review_gate_started [t=100ms]
│   ├─ Span: load_artifact [t=105ms, d=10ms]
│   ├─ Span: retrieve_context [t=120ms, d=50ms]
│   │   ├─ Span: query_knowledge_fabric [t=125ms, d=45ms]
│   │   └─ Span: get_standards [t=135ms, d=15ms]
│   ├─ Span: invoke_model [t=175ms, d=2000ms]
│   │   ├─ Span: select_model [t=176ms, d=5ms]
│   │   ├─ Span: model_inference [t=182ms, d=1990ms]
│   │   └─ Span: parse_result [t=2180ms, d=5ms]
│   ├─ Span: validate_output [t=2190ms, d=20ms]
│   └─ Span: publish_event [t=2215ms, d=10ms]
└─ Code_review_gate_completed [total=2225ms]
```

## 19.3 Metrics

### Key Metrics

```
Orchestrator Metrics:
  - artifacts_created (counter)
  - artifacts_completed (counter)
  - artifacts_in_progress (gauge)
  - state_transition_duration (histogram)
  - gate_pass_rate (gauge)
  
Agent Metrics:
  - agent_execution_duration (histogram)
  - agent_success_rate (gauge)
  - agent_failures_total (counter)
  - model_selection_distribution (histogram)
  
Gate Metrics:
  - gate_{gate_name}_pass_rate (gauge)
  - gate_{gate_name}_execution_duration (histogram)
  - gate_failures_by_reason (counter)
  
Event Bus Metrics:
  - events_published_total (counter)
  - events_processed_total (counter)
  - events_failed_total (counter)
  - event_processing_duration (histogram)
  - event_queue_depth (gauge)
  
Model Metrics:
  - model_invocations_total (counter)
  - model_tokens_used (counter)
  - model_inference_duration (histogram)
  - model_cost_total (counter)
```

### Prometheus Scrape Configuration

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'korame'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

## 19.4 Alerting

### Alert Rules

```yaml
groups:
  - name: korame_alerts
    rules:
      - alert: HighArtifactFailureRate
        expr: gate_pass_rate < 0.80
        for: 5m
        annotations:
          summary: "Gate pass rate below 80%"
          severity: "warning"
      
      - alert: OrchestrationServiceDown
        expr: up{job="korame"} == 0
        for: 1m
        annotations:
          summary: "Korame orchestrator is down"
          severity: "critical"
      
      - alert: EventBusBacklog
        expr: event_queue_depth > 1000
        for: 10m
        annotations:
          summary: "Event bus backlog exceeding 1000 events"
          severity: "warning"
      
      - alert: AgentFailureSpike
        expr: rate(agent_failures_total[5m]) > 0.1
        for: 2m
        annotations:
          summary: "Agent failure rate > 10%"
          severity: "critical"
```

### Dashboard Example (Grafana)

```
Korame System Dashboard
├─ Pipeline Health
│  ├─ Artifacts in progress (gauge)
│  ├─ Average time to completion (line chart)
│  └─ Throughput (artifacts/day)
│
├─ Quality Gates
│  ├─ Code Review pass rate (%)
│  ├─ Security scan pass rate (%)
│  ├─ Testing coverage (%)
│  └─ UAT pass rate (%)
│
├─ Agent Health
│  ├─ Agent availability (%)
│  ├─ Agent execution time (histogram)
│  └─ Top failures (table)
│
└─ Infrastructure
   ├─ Event bus depth
   ├─ Model inference latency
   └─ Database query time
```

---

# 20. Roadmap

## 20.1 Release Timeline

### Phase 1: Korame Kernel (Months 1-3)

**Goal:** Build the foundational runtime that every future agent depends on.

#### Deliverables
- ✓ Workflow Orchestrator (task scheduling, state machine, dependency resolution)
- ✓ Redis Event Bus (pub/sub, ordering, replay)
- ✓ Agent SDK (standardized interface for all agents)
- ✓ Knowledge Fabric Interface (unified context API)
- ✓ Artifact Manager (versioning, storage)
- ✓ Plugin Manager (extensibility)
- ✓ Configuration Manager (YAML/JSON)
- ✓ Logging & Telemetry (structured logging, tracing)
- ✓ Model Router (basic, Ollama-only)

#### Success Criteria
- [ ] Orchestrator processes 100 artifacts without failure
- [ ] Event ordering guaranteed within single artifact
- [ ] All logs structured and indexed in ElasticSearch
- [ ] Distributed tracing works end-to-end
- [ ] Plugins can be loaded/unloaded without restart

#### Technology
- Python 3.11 + FastAPI
- Redis (event bus)
- PostgreSQL (project state)
- Neo4j (relationships)
- ChromaDB (embeddings)
- Docker + Docker Compose
- Local Ollama models

---

### Phase 2: First Working Agents (Months 4-6)

**Goal:** Demonstrate story-to-code flow with all quality gates.

#### Deliverables
- ✓ RTE Agent (requirement parsing, story generation)
- ✓ Architect Agent (solution design, ADR generation)
- ✓ Developer Agent (code generation, unit tests)
- ✓ Code Reviewer Agent (style, documentation, patterns)
- ✓ Security Agent (vulnerability scanning, compliance)
- ✓ Testing Agent (test generation, coverage measurement)

#### Success Criteria
- [ ] End-to-end story-to-code flow (< 30 minutes)
- [ ] Code review gate blocks 95% of issues before manual review
- [ ] Security scan identifies 100% of intentional vulnerabilities in tests
- [ ] Testing agent generates tests with > 80% coverage
- [ ] Zero false negatives in security scanning

#### Technology
- Llama2 13B for architecture + code review
- Code Llama 7B for code generation
- Qwen3 8B for lightweight tasks
- Ollama for local inference
- Bandit + custom security scanning

---

### Phase 3: UAT & Dashboarding (Months 7-9)

**Goal:** Complete the engineering pipeline; add business validation and visibility.

#### Deliverables
- ✓ UAT Agent (business acceptance testing)
- ✓ RTE Dashboard (React single-page app)
- ✓ Real-time pipeline visibility
- ✓ Quality metrics and reporting
- ✓ Audit logging and compliance reports

#### Success Criteria
- [ ] Dashboard shows real-time artifact states
- [ ] RTE can track artifacts from requirement to deployment
- [ ] Quality metrics dashboard shows 30-day trends
- [ ] Audit logs are tamper-proof and complete
- [ ] Export compliance reports (OWASP, GDPR, etc.)

#### Technology
- React 18 for dashboard
- WebSocket for real-time updates
- Grafana for metrics
- ElasticSearch for log analysis
- Apache Superset for BI

---

### Phase 4: DevOps & Deployment (Months 10-12)

**Goal:** Enable production deployments with automation and safety.

#### Deliverables
- ✓ DevOps Agent (deployment automation)
- ✓ CI/CD integration (GitHub Actions / Azure Pipelines)
- ✓ Blue-green deployment strategy
- ✓ Canary deployments with health checks
- ✓ Automatic rollback on health check failure

#### Success Criteria
- [ ] Deployment to production < 10 minutes
- [ ] Zero-downtime deployments
- [ ] Automatic rollback on 5xx errors
- [ ] Deployment audit trail complete
- [ ] 99.5% uptime SLA for Korame system

#### Technology
- Docker containers
- Local Kubernetes (minikube for dev)
- GitHub Actions for CI/CD
- Blue-green deployment scripts
- Health check agents

---

### Phase 5: Azure & Enterprise Scale (Months 13-18)

**Goal:** Deploy to production-grade infrastructure; enable enterprise features.

#### Deliverables
- ✓ Azure AKS deployment
- ✓ Azure GPU worker pool (H100, A100)
- ✓ Multi-model routing with enterprise models
- ✓ Enterprise dashboard (advanced analytics)
- ✓ Multi-tenant support
- ✓ Advanced observability (APM, RUM)

#### Success Criteria
- [ ] Deploy to Azure AKS (3-node cluster)
- [ ] Scale to 100+ concurrent artifacts
- [ ] Azure GPU agent pool auto-scales 1-10 nodes
- [ ] 99.95% uptime SLA
- [ ] < 5% cost increase from enterprise features
- [ ] Support 10+ enterprise customers

#### Technology
- Azure AKS
- Azure VM H100/A100 GPU nodes
- Azure Database PostgreSQL (managed)
- Azure Cosmos DB for Neo4j
- Azure Blob Storage
- Application Insights + Azure Monitor
- Azure Key Vault
- Terraform for IaC

---

## 20.2 Future Enhancements

### Short Term (6-12 months)

- [ ] Multi-language support (Go, Rust, Java agents)
- [ ] Specialized domain agents (Mobile, Frontend, Backend)
- [ ] Advanced RAG with long-context models (GPT-4-128K, Claude 200K)
- [ ] Team collaboration features (real-time editing, comments)
- [ ] Integration marketplace (GitHub, GitLab, Jira, Azure DevOps)

### Medium Term (12-24 months)

- [ ] Zero-shot agent orchestration (agents negotiate their own workflow)
- [ ] Graph-based reasoning (complex dependency analysis)
- [ ] Emergent capabilities (agents learning from each other)
- [ ] Serverless deployment (AWS Lambda, Azure Functions)
- [ ] Federal learning for knowledge sharing across organizations

### Long Term (24+ months)

- [ ] Fully autonomous software factories
- [ ] Cross-organization collaboration networks
- [ ] AI-powered business optimization
- [ ] Real-time code synthesis from natural language
- [ ] Autonomous infrastructure management

---

## 20.3 Success Metrics

### System Health
- **Uptime:** 99.5%+ (Phase 1), 99.95%+ (Phase 5)
- **Latency (p95):** Story→Code < 15 minutes
- **Throughput:** 100+ artifacts/month
- **Quality Gate Pass Rate:** > 95% for code review, > 98% for security

### Business Impact
- **Developer Productivity:** 2x improvement (measured in artifacts/month/developer)
- **Code Quality:** Reduce defects 50% (via consistent review/testing)
- **Security:** Zero exploitable vulnerabilities (OWASP Top 10)
- **Time to Market:** Reduce from weeks to days

### Operational Excellence
- **MTTR (Mean Time To Recovery):** < 15 minutes
- **Change Failure Rate:** < 5%
- **Deployment Frequency:** Daily deployments capability
- **Documentation Completeness:** 100% of critical paths documented

---

# Appendix A: Glossary

- **Artifact:** Any output from the system (requirements, designs, code, test results)
- **Event Bus:** Redis pub/sub system for inter-agent communication
- **Gate:** Quality checkpoint (Code Review, Security, Testing, UAT)
- **Knowledge Fabric:** Unified interface to all project knowledge
- **Model Router:** Component that selects appropriate LLM for each task
- **Orchestrator:** Central task scheduling and state management engine
- **Plugin:** Extension mechanism for custom agents/features
- **RTE:** Release Train Engineer; business owner and project sponsor
- **State Machine:** Artifact lifecycle with defined state transitions
- **UAT:** User Acceptance Testing; business validation phase

---

# Appendix B: Acronyms

- **ADR:** Architectural Decision Record
- **AKS:** Azure Kubernetes Service
- **API:** Application Programming Interface
- **CI/CD:** Continuous Integration / Continuous Deployment
- **CVE:** Common Vulnerabilities and Exposures
- **GPU:** Graphics Processing Unit
- **OWASP:** Open Web Application Security Project
- **RAG:** Retrieval-Augmented Generation
- **RBAC:** Role-Based Access Control
- **RTE:** Release Train Engineer
- **SAS:** Software Architecture Specification
- **TDD:** Test-Driven Development
- **TLS:** Transport Layer Security
- **UAT:** User Acceptance Testing
- **UUID:** Universally Unique Identifier
- **VPC:** Virtual Private Cloud

---

**END OF DOCUMENT**

This Software Architecture Specification is the single source of truth for Korame. All implementation decisions must trace back to the principles and architecture defined herein.

*Status: Foundation Phase - Subject to refinement as implementation proceeds*

