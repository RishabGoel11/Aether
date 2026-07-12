# ARCHITECTURE.md

# Aether System Architecture

## High-Level Architecture

```
                        User
                          │
      ┌───────────────────┼───────────────────┐
      │                   │                   │
     CLI              Desktop               Web
                          │
                          ▼
             Conversation Controller
                          │
                          ▼
                Agent Orchestrator
                          │
      ┌────────────┬─────────────┬─────────────┐
      │            │             │             │
   Memory       Tool Hub        RAG      Model Manager
      │            │             │             │
      └────────────┴─────────────┴─────────────┘
                          │
                  Infrastructure Layer
      Logging • Configuration • Storage • Testing
```

---

## Architectural Principles

### Separation of Concerns

Every module has one clearly defined responsibility.

### Modularity

Components communicate through well-defined interfaces and should be replaceable.

### Local First

The default implementation should avoid unnecessary cloud dependencies.

### Privacy First

Runtime user data must remain outside version control.

### Extensibility

Future capabilities should be added by extending the architecture rather than rewriting existing components.

---

## Planned Core Modules

* Conversation Controller
* Agent Orchestrator
* Memory Manager
* Retrieval (RAG)
* Tool Framework
* Model Manager
* Configuration System
* Logging System
* Voice Module
* Automation Module

---

# Architecture

Aether follows a layered architecture to maintain separation of concerns and make the system modular, testable, and extensible.

---

## Presentation Layer

Responsible for interacting with the user.

Current components:

- `main.py`

Responsibilities:

- Read user input.
- Display responses.
- Handle user-facing exceptions.

---

## Application Layer

Coordinates the application's workflow.

Current components:

- `ConversationEngine`
- `Session`
- `PromptBuilder`

Responsibilities:

- Orchestrate conversations.
- Maintain session state.
- Build prompts.
- Coordinate communication between components.

---

## Infrastructure Layer

Provides implementations for external services and system resources.

Current components:

- `ConfigLoader`
- `OllamaLLM`
- `LLMFactory`
- Logger (planned)

Responsibilities:

- Load configuration.
- Communicate with LLM providers.
- Configure logging.
- Translate external APIs into Aether abstractions.

---

## Domain Layer

Defines Aether's core models and interfaces.

Current components:

- `BaseLLM`
- `Message`
- `LLMResponse`
- `Role`
- Custom Exceptions

Responsibilities:

- Define contracts.
- Define shared models.
- Remain independent of external libraries.


                 User
                  │
                  ▼
            Presentation
             (main.py)
                  │
                  ▼
            Application
       ┌──────────────────┐
       │ ConversationEngine│
       │ Session           │
       │ PromptBuilder     │
       └──────────────────┘
                  │
                  ▼
          Infrastructure
       ┌──────────────────┐
       │ ConfigLoader      │
       │ OllamaLLM         │
       │ Logger            │
       └──────────────────┘
                  │
                  ▼
          External Systems
      ┌────────────────────┐
      │ Ollama Server       │
      │ settings.yaml       │
      │ Terminal            │
      └────────────────────┘
      

## Testing Architecture

Aether separates production code from testing infrastructure.

- `tests/fakes/` contains reusable test doubles.
- `tests/conftest.py` provides reusable pytest fixtures.
- Unit tests verify isolated components.
- Integration tests verify collaboration between components using `FakeLLM`.

## Current Status

This document represents the initial architecture and will evolve throughout development.

Major architectural changes will be accompanied by updates to this document and corresponding Architecture Decision Records (ADRs).
