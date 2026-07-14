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
