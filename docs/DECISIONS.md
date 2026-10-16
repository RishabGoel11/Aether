# ADR-001 — Use a src Layout

## Status

Accepted

---

## Context

Aether is intended to become a production-quality AI engineering platform with a modular architecture.

The project will eventually contain many packages including memory, RAG, tools, agents, automation, voice, and model management.

A scalable project layout is therefore required from the beginning.

---

## Decision

The project will use the modern Python `src` layout.

## Alternatives Considered

### Option A

Flat project structure
Example-
* memory.py
* rag.py
* agent.py
-Rejected because it becomes difficult to maintain as the codebase grows.   

### Option B(selected)
src/
    aether/
Chosen because it:
* follows modern Python standards
* prevents accidental import issues
* improves packaging
* scales well



---

# ADR-002

```markdown
# ADR-002 — Local-First Philosophy

## Status

Accepted

## Context

The primary goal of Aether is to provide a privacy-focused AI platform while remaining accessible without recurring costs.

## Decision

The project will prioritize local execution using open-source technologies whenever practical.

Cloud services may be supported as optional enhancements but will never be mandatory.

## Consequences

Positive

- Better privacy
- No mandatory API costs
- Offline capability

Negative

- Higher local hardware requirements
- Potentially slower inference compared to premium hosted models
```

# ADR-003 — Documentation-Driven Development

```markdown

## Status

Accepted

## Context

Large software projects become difficult to maintain when architecture exists only in the developers' heads.

## Decision

Documentation will be created before and updated after implementation.

Every major feature should include corresponding documentation and architectural updates.

## Consequences

Positive

- Easier onboarding
- Better maintainability
- Clear project history

Negative

- Slightly more work during development
```


# ADR-004 — Dependency Injection

## Status

Accepted

---

## Context

As Aether grows, components such as the conversation engine, memory system, retrieval engine, tool framework, and agent system will depend on multiple services.

Creating dependencies directly inside classes would tightly couple implementations and make testing difficult.

---

## Decision

Dependencies will be created only inside the Bootstrap Layer (`ApplicationBuilder`).

Application services receive their dependencies through constructor injection.

Examples include:

* ConversationEngine receives a BaseLLM.
* MemoryManager receives a BaseMemoryStore.
* Application receives both the ConversationEngine and MemoryManager.

---

## Consequences

### Positive

* Loose coupling
* Easier testing
* Replaceable implementations
* Cleaner architecture

### Negative

* Slightly more verbose construction code
* Requires a composition root

---

# ADR-005 — Abstract Infrastructure Interfaces

## Status

Accepted

---

## Context

Multiple infrastructure implementations are expected throughout the project's lifetime.

Examples include:

* Ollama
* OpenAI
* LM Studio
* JSON storage
* SQLite
* Vector databases

Business logic should remain independent from implementation details.

---

## Decision

Infrastructure will communicate through abstract interfaces.

Current abstractions include:

* BaseLLM
* BaseMemoryStore

Future abstractions may include:

* BaseVectorStore
* BaseTool
* BaseRetriever

---

## Consequences

### Positive

* Replaceable implementations
* Easier testing
* Better modularity
* Supports future extensions

### Negative

* Slightly more initial design work

---

# ADR-006 — JSON as the Initial Memory Store

## Status

Accepted

---

## Context

The first implementation of the Memory System requires persistent local storage.

Several options were considered:

* JSON
* SQLite
* DuckDB

At the current stage, Aether is a single-user local application.

---

## Decision

The first memory store will use a JSON file.

Persistence is provided by `JsonMemoryStore`.

The application interacts only through `BaseMemoryStore`.

Future storage implementations can be introduced without modifying business logic.

---

## Alternatives Considered

### SQLite

Pros

* Better querying
* Better scalability

Cons

* More complexity
* Harder to inspect manually

---

### DuckDB

Pros

* Excellent analytical capabilities

Cons

* Unnecessary for the current requirements

---

## Consequences

### Positive

* Human-readable
* Easy debugging
* Simple backups
* Minimal dependencies

### Negative

* Not suitable for very large datasets

---

# ADR-007 — Layered Architecture

## Status

Accepted

---

## Context

As Aether grows beyond a conversational assistant into a complete AI platform, clear architectural boundaries become increasingly important.

Without layering, business logic, infrastructure, and presentation would become tightly coupled.

---

## Decision

Aether adopts a layered architecture consisting of:

* Presentation Layer
* Bootstrap Layer
* Application Layer
* Domain Layer
* Infrastructure Layer

Each layer may depend only on lower-level abstractions and never on higher-level implementations.

---

## Consequences

### Positive

* Better maintainability
* Clear responsibilities
* Easier testing
* Scalable architecture

### Negative

* More project structure
* Slightly more boilerplate during development

---

# ADR-008 — Tool Calling and Subprocess Execution Safety

## Status

Accepted

---

## Context

Allowing an LLM to invoke external tools (such as Python code execution or terminal commands) introduces security, stability, and resource exhaustion risks.

We needed a tool execution architecture that balances capability with safety while remaining testable in isolation.

---

## Decision

1. Tools inherit from `BaseTool` and define strongly-typed input schemas via Pydantic.
2. Tool execution is managed via a dedicated `ToolExecutor` and governed by `ToolPolicy`.
3. Hazardous tools (Python execution, Terminal commands) execute inside isolated subprocesses with strict timeouts rather than within the main application process.
4. Python code is pre-validated with AST analysis to block unsafe module imports (`os`, `subprocess`, `shutil`, `socket`) and unsafe builtins (`eval`, `exec`, `compile`).
5. Destructive terminal commands (`del`, `format`, `shutdown`, `rmdir`) are blocked via command token inspection.

---

## Consequences

### Positive

* Subprocess isolation prevents runaway processes or memory leaks from crashing the assistant.
* AST inspection prevents accidental or malicious execution of hazardous libraries.
* Uniform `ToolResult` interface simplifies multi-round tool loops.

### Negative

* Subprocess creation has a small latency overhead.
* Static validation cannot prevent all theoretical sandboxing escapes without OS-level containerization.

---

# ADR-009 — RAG Document Chunking and Dual-Tier Chunk Storage

## Status

Accepted

---

## Context

Retrieval-Augmented Generation (RAG) requires partitioning external documents into semantically coherent passages, embedding them, and retrieving them during user queries.

Re-embedding entire documents on every application run with local models is slow. Conversely, storing only vectors in memory loses chunk text across restarts.

---

## Decision

1. Adopt a character-level sliding-window chunker (`TextChunker`) with configurable chunk size and overlap, snapping to whitespace and newline boundaries to preserve sentence integrity.
2. Use a dual-tier storage architecture:
   - Persistent `JsonChunkStore` (`data/rag_chunks.json`) stores chunk metadata and raw text across sessions.
   - Vector Store (`InMemoryVectorStore`) indexes embeddings for high-speed cosine similarity retrieval.
3. At application bootstrap, `rag_pipeline.reindex()` embeds all stored chunks into the vector store so previously indexed files are instantly queryable without re-reading source files.
4. Document indexing deduplicates chunks by source file path, allowing clean in-place re-indexing.

---

## Consequences

### Positive

* Chunks persist across CLI sessions on disk.
* Natural boundary snapping avoids slicing words or sentences mid-character.
* Source file deduplication prevents index bloat when files are re-indexed.

### Negative

* Embedding all persistent chunks on startup incurs an initialization delay when thousands of chunks are stored.
* Future scale will necessitate persistent vector database integration (e.g. ChromaDB or SQLite-vec).

---

# ADR-010 — Decoupled Agentic ReAct Loop (AgentRunner)

## Status

Accepted

---

## Context

Phase 6 required multi-step autonomous task planning and execution. We needed to choose whether to embed autonomous ReAct looping directly inside `ConversationEngine` or create a dedicated agent orchestrator.

---

## Decision

1. Create a dedicated, standalone `AgentRunner` in `app/agent/runner.py`, completely decoupled from `ConversationEngine`.
2. Implement the explicit ReAct pattern (Reason -> Act -> Observe -> Reason...):
   - Extract the LLM's thought text alongside tool calling requests as `THOUGHT` steps.
   - Execute tools and feed results back as `OBSERVATION` steps.
   - Continue until the LLM produces a final natural language `ANSWER` or the step budget is exhausted.
3. If `max_steps` is exhausted, prompt the LLM for a graceful fallback synthesis summarizing what was accomplished so far.
4. Treat tool errors and policy denials as informative observation steps rather than raising fatal exceptions, allowing the agent to self-correct.

---

## Consequences

### Positive

* Clean separation between interactive conversational chat (`ConversationEngine`) and goal-oriented autonomous problem solving (`AgentRunner`).
* Rich, structured `AgentTrace` containing typed `AgentStep` records enables detailed debugging and UI visualization (`--show-trace`).
* Graceful synthesis ensures users always receive a meaningful answer even if complex multi-step reasoning hits limits.

### Negative

* Distinct message formatting requirements between chat and agent loops require independent prompt construction.
