# Aether

> **A modular, local-first AI engineering platform built with privacy, transparency, extensibility, and software engineering best practices at its core.**

![Version](https://img.shields.io/badge/version-v0.4.0-blue)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB)
![License](https://img.shields.io/badge/License-MIT-green)

---

# What is Aether?

Aether is an open-source AI engineering project focused on building a **production-quality local AI assistant** from the ground up.

Rather than being developed as a rapid prototype, Aether is intentionally engineered using professional software engineering principles including modular architecture, clean design, testing, documentation, and long-term maintainability.

The project serves two complementary purposes:

- Build a capable local-first AI assistant.
- Demonstrate modern AI engineering through incremental, production-quality development.

Every epic introduces new architectural concepts while maintaining a stable and extensible codebase.

---

# Vision

Aether aims to evolve into a complete AI engineering platform capable of:

- Natural conversation
- Long-term memory
- Tool execution
- Retrieval-Augmented Generation (RAG)
- Web intelligence
- Voice interaction
- Multi-agent collaboration
- Local-first execution
- Privacy-preserving AI

---

# Engineering Principles

The project is guided by a small set of engineering principles:

- **Local First** — Execute locally whenever practical.
- **Privacy Focused** — User data remains under the user's control.
- **Framework Independent** — External frameworks remain integrations, not architectural foundations.
- **Modular Architecture** — Components are independently replaceable.
- **Production over Prototype** — Prioritize maintainability, testing, and documentation.
- **Documentation First** — Architecture and design before implementation.
- **Engineering Excellence** — Build features on top of strong engineering foundations.

---

# Current Features

## Core AI Platform

- Local LLM integration using Ollama
- Modular Conversation Engine
- Session Management
- Persistent conversation history
- Conversation clearing with `/clear`
- Prompt Builder
- YAML Configuration System
- Typed Configuration Models
- Structured Logging
- Custom Exception Hierarchy
- Factory Pattern
- Application Bootstrap
- Interactive Command-Line Interface
- Local-first conversations

## Memory System

Aether includes a modular, persistent, local-first long-term memory system.

Current capabilities:

- Persistent JSON-based memory storage
- Typed memory models using Pydantic
- Modular memory architecture
- Dependency-injected `MemoryManager`
- Abstract storage interface (`BaseMemoryStore`)
- JSON storage backend (`JsonMemoryStore`)
- Rule-based automatic memory extraction
- Profile, preference, and project memory categories
- Memory deduplication
- Memory update and deletion
- Embedding abstraction
- Ollama-based embeddings
- Abstract vector store interface (`BaseVectorStore`)
- In-memory vector store
- Semantic memory retrieval
- Memory summarization
- Memory consolidation
- Integration with the `ConversationEngine`

The current memory extractor uses deterministic rule-based patterns. This provides a reliable foundation for future LLM-based memory extraction.

## Tool Framework

Aether includes a modular tool execution framework that allows the LLM to perform actions through registered tools.

Current capabilities:

- Generic `BaseTool` abstraction
- Typed tool arguments using Pydantic
- Tool definitions with descriptions and input schemas
- Tool registry for managing available tools
- Tool execution pipeline
- Tool policy for controlling tool access
- Multi-round LLM tool calling
- Tool result handling
- Tool execution error handling
- Maximum tool round protection

### Built-in Tools

- Calculator
- Date and time lookup
- File information
- Python code execution
- Terminal command execution

### Safety Mechanisms

The current tool framework includes basic execution safety mechanisms:

- Tool access control through `ToolPolicy`
- Configurable maximum tool execution rounds
- Python execution timeout handling
- Terminal execution timeout handling
- Python execution in a separate subprocess
- Temporary Python file cleanup
- Basic AST-based Python safety validation
- Blocking of unsafe Python modules including:
  - `os`
  - `subprocess`
  - `shutil`
  - `socket`
- Blocking of unsafe Python functions including:
  - `eval`
  - `exec`
  - `compile`
  - `__import__`
- Blocking of destructive terminal commands including:
  - `del`
  - `erase`
  - `rmdir`
  - `rd`
  - `format`
  - `shutdown`
  - `restart`
- Basic detection of unsafe terminal commands in chained commands

These mechanisms provide a basic safety layer and are intended as a foundation for stronger sandboxing and permission systems in future development.

## Engineering Excellence

- Modern Python packaging with `uv`
- PEP 621 compliant project configuration
- Hatchling build backend
- GitHub Actions Continuous Integration
- Ruff linting and formatting
- Pytest unit and integration testing
- Automated code coverage
- Debug subsystem
- Diagnostics subsystem
- Documentation-first development workflow

---

# Planned Capabilities

Aether's long-term roadmap includes:

- Retrieval-Augmented Generation (RAG)
- LangChain Integration
- LangGraph Integration
- Web Intelligence
- Voice Interface
- Multi-Agent Collaboration
- Production Deployment

A detailed development roadmap is available in `docs/ROADMAP.md`.

---

# Architecture

Aether follows a layered architecture designed to keep business logic independent from infrastructure.

```text
                                  +----------------------+
                                  |        User          |
                                  +----------+-----------+
                                             |
                                             v
                                  +----------------------+
                                  |         CLI          |
                                  +----------+-----------+
                                             |
                                             v
                               +-------------------------------+
                               |      ApplicationBuilder       |
                               +---------------+---------------+
                                               |
                                               v
                               +-------------------------------+
                               |      ConversationEngine       |
                               +---------------+---------------+
                                               |
              +----------------+---------------+---------------+----------------+
              |                |                               |                |
              v                v                               v                v
     +----------------+ +--------------------+      +------------------+ +------------------+
     | PromptBuilder  | |      Session       |      |  DebugCollector  | |  Tool Framework  |
     +----------------+ +--------------------+      +------------------+ +--------+---------+
                             |                                           |
                             v                                           v
               +-------------------------------+              +----------------------+
               |       MemoryExtractor         |              |     ToolRegistry     |
               +---------------+---------------+              +----------+-----------+
                               |                                         |
                               v                                         v
               +-------------------------------+              +----------------------+
               |        MemoryManager          |              |    ToolExecutor      |
               +------+-------------+----------+              +----------+-----------+
                      |             |                                    |
          +-----------+             +-----------+                        v
          |                                     |              +----------------------+
          v                                     v              |     ToolPolicy       |
+----------------------+             +----------------------+   +----------------------+
|  JsonMemoryStore     |             |     VectorStore      |
| (Persistent Memory)  |             |  (Semantic Index)    |
+----------------------+             +----------+-----------+
                                               |
                                               v
                                     +----------------------+
                                     |      Embedder        |
                                     | (Ollama Embeddings)  |
                                     +----------------------+

```

Future subsystems—including Retrieval-Augmented Generation (RAG), Web Intelligence, Voice, and Multi-Agent Collaboration—will integrate into this architecture while preserving the separation of concerns established during previous epics.

Detailed architectural documentation is available in `docs/ARCHITECTURE.md`.

---

# Technology Stack

## Current

- Python
- Ollama
- Pydantic
- PyYAML
- uv
- Hatchling
- Ruff
- Pytest

## Planned

- LangChain
- LangGraph
- SQLite
- ChromaDB
- FastAPI
- Playwright
- Faster-Whisper
- Piper

---

# Installation

Clone the repository:

```bash
git clone https://github.com/RishabGoel11/Aether.git
cd Aether
```

Install dependencies:

```bash
uv sync --extra dev
```

Run the interactive chat:

```bash
uv run aether chat
```

Run diagnostics:

```bash
uv run aether doctor
```

Display the version:

```bash
uv run aether version
```

Aether requires a locally running Ollama installation with the configured LLM and embedding model available.

---

# Development

Run tests:

```bash
uv run pytest
```

Run linting:

```bash
uv run ruff check .
```

Format code:

```bash
uv run ruff format .
```

Aether uses:

- `pyproject.toml` as the single source of truth for project configuration.
- `uv.lock` to ensure reproducible development environments.

---

# Project Status

| Epic | Status |
| --- | --- |
| Epic 0 – Engineering Foundations | ✅ Complete |
| Epic 1 – Core Conversation Engine | ✅ Complete |
| Epic 2 – Engineering Excellence | ✅ Complete |
| Epic 3 – Memory System | ✅ Complete |
| Epic 4 – Tool Framework | ✅ Complete |
| Epic 5 – Retrieval-Augmented Generation | ⬜ Planned |
| Epic 6 – AI Framework Integrations | ⬜ Planned |
| Epic 7 – Web Intelligence | ⬜ Planned |
| Epic 8 – Voice | ⬜ Planned |
| Epic 9 – Multi-Agent System | ⬜ Planned |
| Epic 10 – Production | ⬜ Planned |

For detailed milestones and implementation tasks, see `docs/ROADMAP.md`.

---

# Latest Release

## v0.4.0 — Tool Framework

Highlights of this release:

- Modular `BaseTool` abstraction
- Typed tool definitions and argument validation
- Tool registry
- Tool execution pipeline
- Tool policy support
- Multi-round LLM tool calling
- Calculator tool
- Date and time tool
- File information tool
- Python execution tool
- Terminal execution tool
- Tool execution error handling
- Execution timeout handling
- Terminal command safety restrictions
- Python code safety restrictions
- Persistent conversation clearing with `/clear`
- Empty assistant response handling
- Continued unit and integration test coverage

The next major milestone is **Epic 5 – Retrieval-Augmented Generation (RAG)**.

---

# Documentation

The `docs/` directory contains the project's technical documentation, including:

- Architecture
- Development Roadmap
- Engineering Decisions
- Project Master
- Engineering Journal
- Changelog

---

# Development Workflow

Every feature in Aether follows a structured engineering lifecycle:

1. Architecture discussion
2. Design review
3. Implementation
4. Testing
5. Documentation
6. Pull Request review
7. Git commit
8. GitHub release

This workflow ensures Aether evolves through disciplined, production-quality engineering.

---

# Contributing

Aether is currently under active development.

Contribution guidelines will be added once the core architecture reaches a stable state.

---

# License

Licensed under the **MIT License**.