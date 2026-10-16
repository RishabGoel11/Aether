# AI Engineering Learning Path

> **A systematic, hands-on curriculum for mastering production AI engineering through building Aether.**

Aether serves two complementary goals:
1. Building a production-quality, local-first AI assistant.
2. Providing a comprehensive, reproducible learning curriculum in modern AI systems engineering.

This document maps out the key computer science, software design, and AI engineering concepts introduced and mastered across each phase of the project.

---

## Curriculum Overview

| Phase | Milestone | Core Engineering Concepts |
|---|---|---|
| **Phase 0** | Engineering Foundations | Modern Python, `uv`, `pyproject.toml`, Ruff, Pytest, Git workflow |
| **Phase 1** | Core Conversation Engine | Local LLM inference, Prompt engineering, Session state, Error hierarchies |
| **Phase 2** | Engineering Excellence | Dependency injection, Diagnostics subsystem, Debug collector, CI/CD |
| **Phase 3** | Memory System | Semantic vector search, Cosine similarity, Memory consolidation, Deduplication |
| **Phase 4** | Tool Framework | LLM function calling, Pydantic schemas, AST code inspection, Subprocess sandboxing |
| **Phase 5** | Retrieval-Augmented Generation | Document chunking, Boundary snapping, Embedding storage, Citation injection |
| **Phase 6** | Agentic ReAct Loop | Autonomous Reason-Act-Observe loops, Step budgeting, Fallback synthesis |
| **Phase 7** | Framework Integrations | Adapter pattern, Framework decoupling, LangChain / LangGraph |
| **Phase 8** | Web Intelligence | Headless browser automation, Scraping, DOM extraction |
| **Phase 9** | Voice Systems | Local Speech-to-Text (Whisper), Text-to-Speech (Piper), Audio streaming |
| **Phase 10** | Multi-Agent Collaboration | Agent coordination, Role specialization, Inter-agent message protocols |
| **Phase 11** | Production Systems | REST APIs, Fastify/FastAPI, Containerization, Desktop packaging |

---

## Detailed Phase Breakdown

### Phase 0 — Engineering Foundations ✅
- **Modern Packaging**: Transitioning from `setup.py` / `requirements.txt` to PEP 621 `pyproject.toml` managed by `uv`.
- **Fast Linting and Formatting**: Using `ruff` for ultra-fast, unified static analysis and PEP 8 formatting.
- **Test-Driven Design**: Setting up `pytest` with `pytest-cov`, fixture isolation, and zero-dependency testing.
- **Git Hygiene**: Conventional commits, branch isolation, and automated pre-push lint/test validation.

### Phase 1 — Core Conversation Engine ✅
- **Local Model Serving**: Integrating with local Ollama daemons for private, zero-cost model inference.
- **Provider Abstraction**: Creating `BaseLLM` interfaces to decouple application logic from vendor APIs.
- **Context & Session Modeling**: Managing conversation sliding windows to respect model context constraints.
- **Prompt Composition**: Structured prompt builders separating system instructions, context, and conversation history.

### Phase 2 — Production Engineering & Observability ✅
- **Dependency Injection & Bootstrap**: Establishing the Composition Root pattern (`ApplicationBuilder`) to wire services cleanly.
- **Diagnostics & Health Checks**: Self-healing subsystem (`aether doctor`) inspecting Python runtimes, daemon ports, and model availability.
- **Telemetry & Debugging**: Non-intrusive latency tracking, token estimation, and execution trace inspection.

### Phase 3 — Long-Term Memory Systems ✅
- **Memory Categorization**: Differentiating between episodic chat history, user preferences, and profile records.
- **Vector Embeddings**: Dense representation of text using embedding models (`nomic-embed-text`).
- **Vector Search Mathematics**: Implementing in-memory cosine similarity and top-k ranking algorithms.
- **Memory Consolidation**: LLM-driven summarization and deduplication to maintain clean, bounded memory stores.

### Phase 4 — Function Calling & Tool Sandboxing ✅
- **Tool Protocol**: Transforming Pydantic model definitions into standard tool definitions for LLMs.
- **Multi-Round Execution**: Parsing model tool calls, dispatching execution, and feeding results back for multi-turn answers.
- **Execution Sandboxing**: Isolating Python script execution and terminal commands into separate subprocesses with strict timeouts.
- **Static Security Analysis**: Inspecting Python Abstract Syntax Trees (AST) to prevent import of unsafe modules (`os`, `subprocess`) or builtins (`eval`, `exec`).

### Phase 5 — Retrieval-Augmented Generation (RAG) ✅
- **Document Ingestion**: Parsing structured and unstructured documents (`.txt`, `.md`, directories).
- **Chunking Algorithms**: Designing character sliding windows with natural boundary snapping on whitespace and newlines.
- **Dual-Tier Storage**: Decoupling raw chunk metadata storage (`JsonChunkStore`) from ephemeral vector indexes (`InMemoryVectorStore`).
- **Citation Mechanics**: Injecting retrieved passages into system prompts with bracketed source references (`[1]`, `[2]`).

### Phase 6 — Agentic ReAct Loops ✅
- **The ReAct Pattern**: Implementing the Synergizing Reasoning and Acting loop (Reason -> Act -> Observe).
- **Thought Extraction**: Preserving the model's internal rationale alongside action calls.
- **Execution Budgeting**: Guarding against infinite cycles with step caps and graceful fallback synthesis.
- **Fault Recovery**: Feeding execution errors back into the loop as observations, empowering the model to self-correct.

### Phase 7+ — Advanced AI Engineering (Roadmap)
- **Framework Adapters**: Integrating LangChain and LangGraph as optional plugins while preserving core architectural autonomy.
- **Autonomous Web Navigation**: Controlling headless browser sessions for web research and information extraction.
- **Edge Voice Processing**: Low-latency, local streaming speech-to-text and text-to-speech pipelines.
- **Distributed Multi-Agent Systems**: Coordinating specialized planner, researcher, coder, and reviewer agents.
