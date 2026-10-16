# About Aether

> **Version:** v0.6.0 (Agentic ReAct Loop)  
> **Status:** 7 of 12 Phases Completed (Epics 0–6)  
> **Test Suite:** 269 passed | 90% test coverage

Aether is a modular, local-first AI engineering platform built with privacy, transparency, extensibility, and software engineering best practices at its core.

---

## Core Purpose

Aether is an open-source project focused on building a production-quality local AI assistant from the ground up. It emphasizes professional software engineering principles over rapid prototyping, ensuring clean architecture, modular subsystem design, thorough test coverage, and long-term maintainability.

## Key Principles

- **Local First**: Execution happens locally whenever practical using open-source models (Ollama, nomic-embed-text).
- **Privacy Focused**: Conversations, memories, indexed files, and agent traces remain on the local machine under user control.
- **Framework Independent**: External frameworks (LangChain, LangGraph) are integrations, never architectural foundations.
- **Modular Architecture**: Subsystems communicate through abstract interfaces (`BaseLLM`, `BaseMemoryStore`, `BaseChunkStore`, `BaseVectorStore`, `BaseTool`) and are independently replaceable.
- **Production over Prototype**: Continuous testing, 90%+ code coverage, automated Ruff linting/formatting, and documentation-first development.

---

## Current Implemented Capabilities (v0.6.0)

1. **Core Conversation Engine**: Multi-turn dialogue, sliding session history, prompt building, structured logging, Ollama provider.
2. **Long-Term Memory System**: Persistent JSON storage, rule-based extraction, semantic vector search, memory summarization & consolidation.
3. **Tool Execution Framework**: Generic tool abstraction, registry, policy enforcement, multi-round tool calling, built-in tools (Calculator, Datetime, FileInfo, Python, Terminal).
4. **Retrieval-Augmented Generation (RAG)**: Extensible document loaders, sliding-window chunker with boundary snapping, persistent JSON chunk store, startup re-indexing, cosine similarity retrieval, and source citation injection.
5. **Agentic ReAct Loop**: Autonomous `AgentRunner` orchestrating Reason -> Act -> Observe loops with thought capture, structured tracing, step budgeting, and graceful fallback synthesis.

---

## CLI Usage

```bash
# Multi-turn chat with memory and RAG context
uv run aether chat

# Autonomous multi-step goal execution
uv run aether run "Calculate 15 factorial" --show-trace

# Ingest documents into local RAG knowledge base
uv run aether index ./docs

# Run environment and subsystem diagnostics
uv run aether doctor

# Display current application version
uv run aether version
```

For comprehensive technical specifications, see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and [`README.md`](README.md).
