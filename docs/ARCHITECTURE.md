# Aether System Architecture

> **Version:** v0.3.0-alpha.1 (Memory Foundation)
> This document describes the current architecture of Aether and its intended long-term evolution.

---

# Overview

Aether is a modular, local-first AI engineering platform built around clean architecture, dependency injection, and replaceable components.

The project emphasizes:

* Local-first execution
* Privacy-first design
* Modular architecture
* Testability
* Production-quality engineering

Each subsystem has a single responsibility and communicates through well-defined interfaces.

---

# High-Level Architecture

```text
                                    +----------------------+
                                   |        User          |
                                   +----------+-----------+
                                              |
                                              v
                                   +----------------------+
                                   |        CLI           |
                                   +----------+-----------+
                                              |
                                              v
                               +-------------------------------+
                               |      ApplicationBuilder       |
                               +---------------+---------------+
                                               |
                                               v
                               +-------------------------------+
                               |     ConversationEngine        |
                               +---------------+---------------+
                                               |
                      +------------------------+------------------------+
                      |                         |                        |
                      v                         v                        v
            +----------------+       +--------------------+    +------------------+
            | PromptBuilder  |       |      Session       |    |  DebugCollector  |
            +----------------+       +--------------------+    +------------------+
                                               |
                                               v
                               +-------------------------------+
                               |        MemoryRetriever        |
                               +---------------+---------------+
                                               |
                                               v
                               +-------------------------------+
                               |        MemoryManager          |
                               +------+-------------+----------+
                                      |             |
                   +------------------+             +------------------+
                   |                                         |
                   v                                         v
         +----------------------+                +----------------------+
         |  JsonMemoryStore     |                |   VectorStore        |
         | (Persistent Memory)  |                | (Semantic Index)     |
         +----------------------+                +----------+-----------+
                                                            |
                                                            |
                                                            v
                                                +----------------------+
                                                |      Embedder        |
                                                | (Ollama Embeddings)  |
                                                +----------------------+

                     Background / Maintenance Components
                     -----------------------------------

                    +-------------------------------+
                    |      MemoryConsolidator       |
                    +---------------+---------------+
                                    |
                                    v
                    +-------------------------------+
                    |      MemorySummarizer         |
                    +---------------+---------------+
                                    |
                                    v
                           +-------------------+
                           |      BaseLLM      |
                           |    (OllamaLLM)    |
                           +-------------------+
```

---

# Architectural Principles

## Separation of Concerns

Every module owns exactly one responsibility.

Business logic, infrastructure, persistence, and presentation remain independent.

---

## Dependency Inversion

High-level components depend on abstractions rather than implementations.

Example:

```text
ConversationEngine
        │
        ▼
MemoryManager
        │
        ▼
BaseMemoryStore
        │
        ▼
JsonMemoryStore
```

Implementations may change without affecting higher layers.

---

## Dependency Injection

Object creation occurs only inside the bootstrap layer.

Components never instantiate their own dependencies.

Example:

* ConversationEngine receives an LLM.
* MemoryManager receives a BaseMemoryStore.
* Application receives both Engine and MemoryManager.

---

## Local First

The default implementation avoids unnecessary cloud dependencies.

Current implementation uses:

* Ollama
* Local JSON storage

Future cloud providers will remain optional.

---

## Privacy First

User conversations and memories remain on the local machine unless explicitly configured otherwise.

Runtime data is excluded from version control.

---

## Extensibility

New functionality should be added by introducing new modules rather than modifying existing ones.

Examples include:

* Additional LLM providers
* New memory stores
* Tool plugins
* Retrieval engines

---

# Layered Architecture

---

## Presentation Layer

Responsible for user interaction.

### Current Components

* CLI
* Commands
* Parser

### Responsibilities

* Accept user input
* Display responses
* Handle user-facing errors

---

## Bootstrap Layer

Responsible for constructing the application.

### Current Components

* Application
* ApplicationBuilder

### Responsibilities

* Load configuration
* Configure logging
* Create services
* Wire dependencies
* Perform dependency injection

---

## Application Layer

Coordinates workflows.

### Current Components

* ConversationEngine
* Session
* PromptBuilder
* MemoryManager

### Responsibilities

* Coordinate conversations
* Maintain session state
* Coordinate memory operations
* Build prompts

---

## Domain Layer

Defines business models and contracts.

### Current Components

* BaseLLM
* BaseMemoryStore
* Message
* Role
* LLMResponse
* MemoryRecord
* Custom Exceptions

### Responsibilities

* Define interfaces
* Define shared models
* Remain independent of infrastructure

---

## Infrastructure Layer

Provides concrete implementations.

### Current Components

* OllamaLLM
* LLMFactory
* JsonMemoryStore
* ConfigLoader
* Logger
* Diagnostics

### Responsibilities

* Access external systems
* Persist data
* Configure runtime services
* Translate external APIs into domain abstractions

---

# Current Runtime Flow

```text
User
 │
 ▼
CLI
 │
 ▼
ApplicationBuilder
 │
 ▼
Application
 │
 ▼
ConversationEngine
 │
 ├───────────────┐
 ▼               ▼
Session     PromptBuilder
                 │
                 ▼
             LLMFactory
                 │
                 ▼
             OllamaLLM
                 │
                 ▼
            Local Ollama
```

---

# Memory Architecture

The Memory Foundation has been implemented.

Current architecture:

```text
ConversationEngine

MemoryManager

BaseMemoryStore

JsonMemoryStore

data/memories.json
```

Current capabilities:

* Typed memory models
* Persistent JSON storage
* Memory manager
* Storage abstraction
* Dependency injection

Future capabilities:

* Conversation persistence
* Memory retrieval
* Prompt integration
* Automatic memory extraction
* Semantic search
* Vector databases

---

# Diagnostics Architecture

```text
Diagnostic Checks
        │
        ▼
Doctor
        │
        ▼
Diagnostic Renderer
        │
        ▼
CLI
```

Current checks include:

* Python version
* Configuration loading
* Ollama package
* Ollama server
* Configured model

---

# Debug Architecture

```text
ConversationEngine
        │
        ▼
DebugCollector
        │
        ▼
DebugRenderer
```

Captured information includes:

* Response time
* Prompt length
* Message count
* Debug events

---

# Testing Architecture

Aether separates production code from testing infrastructure.

Current structure:

```text
tests/

├── unit/
├── integration/
├── fakes/
└── conftest.py
```

Testing philosophy:

* Unit tests verify isolated components.
* Integration tests verify collaboration between components.
* Fake implementations replace external services.
* Production code never depends on testing utilities.

---

# Current Core Modules

Implemented

* Configuration System
* Logging System
* Conversation Engine
* Session Management
* Prompt Builder
* LLM Abstraction
* Ollama Provider
* Memory Foundation
* Diagnostics
* Debug System
* Bootstrap Layer
* CLI

Planned

* Retrieval (RAG)
* Tool Framework
* Agent Orchestrator
* Voice System
* Automation Framework
* Multi-Agent Coordination
* Desktop Interface
* Web Interface

---

# Future Direction

The long-term architecture will evolve toward:

```text
Presentation

↓

Bootstrap

↓

Application Services

├── Conversation
├── Memory
├── Agents
├── Tools
├── Retrieval

↓

Domain Contracts

↓

Infrastructure
```

Each subsystem should remain independently testable, replaceable, and extensible.

---

# Current Status

Current Version

**v0.3.0-alpha.1**

Completed

* Engineering Foundations
* Core Conversation Engine
* Engineering Excellence
* Memory Foundation

The next architectural milestone is integrating memory retrieval into the conversation pipeline, allowing Aether to actively use persistent memories during conversations.
