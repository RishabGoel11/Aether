# Aether

> **A modular, local-first AI engineering platform built with privacy, transparency, extensibility, and software engineering best practices at its core.**

![Version](https://img.shields.io/badge/version-v0.2.0-blue)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB)
![License](https://img.shields.io/badge/License-MIT-green)

---

# What is Aether?

Aether is an open-source AI engineering project focused on building a **production-quality local AI assistant** from the ground up.

Rather than being developed as a rapid prototype, Aether is intentionally engineered using professional software engineering principles including modular architecture, clean design, testing, documentation, and long-term maintainability.

The project serves two complementary purposes:

- Build a capable local-first AI assistant.
- Demonstrate modern AI engineering through incremental, production-quality development.

Every phase introduces new architectural concepts while maintaining a stable and extensible codebase.

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
- Prompt Builder
- YAML Configuration System
- Typed Configuration Models
- Structured Logging
- Custom Exception Hierarchy
- Factory Pattern
- Application Bootstrap
- Interactive Command-Line Interface

## Engineering Excellence

- Modern Python packaging with `uv`
- PEP 621 compliant project configuration
- Hatchling build backend
- GitHub Actions Continuous Integration
- Ruff linting
- Pytest unit & integration testing
- 92% code coverage
- Debug subsystem
- Diagnostics subsystem
- Documentation-first development workflow

---

# Planned Capabilities

Aether's long-term roadmap includes:

- Persistent Memory
- Tool Framework
- Retrieval-Augmented Generation (RAG)
- LangChain Integration
- LangGraph Integration
- Web Intelligence
- Voice Interface
- Multi-Agent Collaboration
- Production Deployment

A detailed development roadmap is available in **docs/ROADMAP.md**.

---

# Architecture

Aether follows a layered architecture designed to keep business logic independent from infrastructure.

```text
                    User
                      │
                      ▼
              Command-Line Interface
                      │
                      ▼
             Application Bootstrap
                      │
                      ▼
                Conversation Engine
                      │
          ┌───────────┼────────────┐
          ▼           ▼            ▼
      Session     Debugger     Diagnostics
          │
          ▼
     Prompt Builder
          │
          ▼
     LLM Abstraction
          │
          ▼
      Provider Layer
          │
          ▼
      Local Ollama
```

Future subsystems—including Memory, Tool Execution, Retrieval-Augmented Generation (RAG), Web Intelligence, Voice, and Multi-Agent Collaboration—will integrate into this architecture while preserving the separation of concerns established during the first two development phases.

Detailed architectural documentation is available in **docs/ARCHITECTURE.md**.

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
uv run python -m app.cli.main chat
```

Run diagnostics:

```bash
uv run python -m app.cli.main doctor
```

Display the version:

```bash
uv run python -m app.cli.main version
```

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

| Phase | Status |
|--------|--------|
| Phase 0 – Engineering Foundations | ✅ Complete |
| Phase 1 – Core Conversation Engine | ✅ Complete |
| Phase 2 – Software Engineering | ✅ Complete |
| Phase 3 – Memory System | ⬜ Planned |
| Phase 4 – Tool Framework | ⬜ Planned |
| Phase 5 – Retrieval-Augmented Generation | ⬜ Planned |
| Phase 6 – AI Framework Integrations | ⬜ Planned |
| Phase 7 – Web Intelligence | ⬜ Planned |
| Phase 8 – Voice | ⬜ Planned |
| Phase 9 – Multi-Agent System | ⬜ Planned |
| Phase 10 – Production | ⬜ Planned |

For detailed milestones and implementation tasks, see **docs/ROADMAP.md**.

---

# Latest Release

## v0.2.0 — Engineering Excellence

Highlights of this release:

- Application bootstrap architecture
- Modular command-line interface
- Debug subsystem
- Diagnostics subsystem
- GitHub Actions CI pipeline
- 92% automated test coverage
- Improved project architecture and developer experience

The next major milestone is **Phase 3 – Memory System**, which introduces persistent conversational memory and lays the foundation for long-term AI capabilities.

# Documentation

The **docs/** directory contains the project's technical documentation, including:

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

This workflow ensures Aether evolves through disciplined, production-quality engineering practices.

---

# Contributing

Aether is currently under active development.

Contribution guidelines will be added once the core architecture reaches a stable state.

---

# License

Licensed under the **MIT License**.