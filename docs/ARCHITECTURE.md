# Aether System Architecture

> **Version:** v0.6.0 (Agentic ReAct Loop)
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
               +-------------------------------------------------------------+
               |                  Command-Line Interface                     |
               |         chat   |   run   |   index   |  doctor  |  version  |
               +-----------------------------+-------------------------------+
                                             |
                                             v
                              +-------------------------------+
                              |      ApplicationBuilder       |
                              +---------------+---------------+
                                              |
                     +------------------------+------------------------+
                     |                                                 |
                     v                                                 v
      +-------------------------------+                 +-------------------------------+
      |      ConversationEngine       |                 |          AgentRunner          |
      |   (Interactive Multi-Turn)    |                 |   (Autonomous ReAct Loop)     |
      +---------------+---------------+                 +---------------+---------------+
                      |                                                 |
      +---------------+---------------+----------------+                |
      |               |               |                |                |
      v               v               v                v                v
+------------+ +-------------+ +--------------+ +-------------------------------+
|PromptBuildr| |   Session   | |DebugCollector| |        Tool Framework         |
+-----+------+ +------+------+ +--------------+ |  Registry | Executor | Policy |
      |               |                         +---------------+---------------+
      v               v                                         |
+-------------+ +-------------+                                 v
| RAGPipeline | |MemoryManager|                         +---------------+
+------+------+ +------+------+                         | Builtin Tools |
       |               |                                | Python | Term |
       v               v                                | Calc | Time   |
+-------------+ +-------------+                         +---------------+
|JsonChunkStor| |JsonMemStore |
| (Disk RAG)  | | (Disk Mem)  |
+------+------+ +------+------+
       \               /
        v             v
      +-----------------+
      |   VectorStore   |
      | (Cosine Search) |
      +--------+--------+
               |
               v
      +-----------------+
      |    Embedder     |
      | (Ollama Embed)  |
      +-----------------+
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

Responsible for user interaction and command dispatching.

### Current Components

* CLI (`main.py`, `parser.py`)
* Commands: `chat`, `run`, `index`, `doctor`, `version`

### Responsibilities

* Parse command-line flags and positional arguments
* Display formatted responses, streaming output, and diagnostic check tables
* Present full agent execution traces when `--show-trace` is supplied
* Handle user-facing errors gracefully

---

## Bootstrap Layer

Responsible for constructing and wiring the application composition root.

### Current Components

* `Application`
* `ApplicationBuilder`

### Responsibilities

* Load configuration (`Settings`, `RAGSettings`, `ToolPolicyConfig`)
* Configure structured logging
* Instantiate infrastructure providers (`OllamaLLM`, `OllamaEmbedder`, `JsonMemoryStore`, `JsonChunkStore`, `InMemoryVectorStore`)
* Instantiate application services (`ConversationEngine`, `AgentRunner`, `RAGPipeline`, `MemoryManager`, `ToolRegistry`, `ToolExecutor`)
* Perform automated startup re-indexing (`rag_pipeline.reindex()`)

---

## Application Layer

Coordinates high-level AI workflows, agentic loops, and context assembly.

### Current Components

* `ConversationEngine` (interactive multi-turn dialogue with memory and RAG context injection)
* `AgentRunner` (autonomous multi-step ReAct Reason->Act->Observe execution)
* `RAGPipeline` (high-level facade unifying indexing, vector retrieval, and citation formatting)
* `MemoryManager` (semantic retrieval, rule extraction, consolidation, summarization)
* `PromptBuilder` (dynamic prompt composition)
* `Session` (sliding window message history)

### Responsibilities

* Coordinate conversations and autonomous agent loops
* Maintain conversation state across turns
* Execute tool calls and feed back observations
* Format retrieved documents into citations

---

## Domain Layer

Defines core business models, contracts, and abstract interfaces.

### Current Components

* LLM Interfaces: `BaseLLM`, `LLMResponse`, `Message`, `Role`, `ToolCallRequest`
* Memory Interfaces: `BaseMemoryStore`, `MemoryRecord`, `MemoryCategory`
* Tool Interfaces: `BaseTool`, `ToolResult`, `ToolDefinition`
* RAG Interfaces: `BaseChunkStore`, `Document`, `Chunk`, `SearchResult`
* Agent Interfaces: `AgentStep`, `AgentTrace`, `AgentResult`, `StepType`
* Vector Store Interfaces: `BaseVectorStore`, `BaseEmbedder`
* Custom Exception Hierarchy

### Responsibilities

* Define abstract contracts and interfaces
* Define shared Pydantic data models
* Remain strictly independent of infrastructure details

---

## Infrastructure Layer

Provides concrete external service integrations and persistent storage.

### Current Components

* `OllamaLLM` (local Ollama text completion / chat API)
* `OllamaEmbedder` (local Ollama embeddings via `nomic-embed-text`)
* `JsonMemoryStore` (`data/memories.json`)
* `JsonChunkStore` (`data/rag_chunks.json`)
* `InMemoryVectorStore` (cosine similarity search)
* Built-in Tools: `PythonExecutionTool`, `TerminalExecutionTool`, `CalculatorTool`, `DateTimeTool`, `FileInfoTool`
* `ConfigLoader` (YAML configuration parser)
* `Logger` (structured JSON / console logging)
* Diagnostics (`Doctor`, checks runner)

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

# RAG Architecture (Retrieval-Augmented Generation)

Aether includes a local-first RAG subsystem for external knowledge retrieval:

```text
Document (file / directory)
     │
     ▼
DocumentLoaderFactory (TextLoader, MarkdownLoader)
     │
     ▼
TextChunker (Sliding window + boundary snapping)
     │
     ▼
DocumentIndexer
     ├──► BaseChunkStore (JsonChunkStore -> data/rag_chunks.json)
     └──► BaseVectorStore (InMemoryVectorStore -> Cosine Similarity)

User Query
     │
     ▼
DocumentRetriever (OllamaEmbedder / nomic-embed-text)
     │
     ▼
SearchResult (Ranked passages + similarity scores)
     │
     ▼
RAGPipeline.format_context() (Source citations [N])
     │
     ▼
PromptBuilder (Injected into System Context)
     │
     ▼
ConversationEngine -> LLM Response
```

Components:
* **Models**: `Document`, `Chunk`, `SearchResult`
* **Loaders**: Extensible loaders (`TextLoader`, `MarkdownLoader`, `DocumentLoaderFactory`) with directory traversal
* **Chunker**: Character-level sliding window with natural boundary snapping on whitespace/newlines
* **Storage**: Persistent `JsonChunkStore` with startup re-indexing into `InMemoryVectorStore`
* **Retriever**: Cosine similarity search with score thresholding
* **CLI**: `aether index <path>` command for ingestion

---

# Agentic Architecture (ReAct Loop)

Aether includes an autonomous multi-step reasoning and action loop (`AgentRunner`) implementing the ReAct pattern:

```text
User Goal: "Calculate 15 factorial and save to file"
      │
      ▼
AgentRunner.run(goal, max_steps=20)
      │
      ▼
┌───► Step N: Reason -> Act -> Observe
│       │
│       ├── 1. PROMPT: System prompt + Tool schemas + Trace history
│       │
│       ├── 2. REASON: LLM outputs Thought + ToolCallRequest
│       │      Record: AgentStep(type=StepType.THOUGHT, content="...")
│       │      Record: AgentStep(type=StepType.ACTION, tool="python_exec", input={...})
│       │
│       ├── 3. ACT: ToolExecutor dispatches via ToolPolicy
│       │      Subprocess executes isolated Python / Terminal command
│       │
│       ├── 4. OBSERVE: Output captured
│       │      Record: AgentStep(type=StepType.OBSERVATION, content="...")
│       │
│       └── 5. EVALUATE:
│              ├── LLM answered with final text? ──► Terminate: StepType.ANSWER
│              ├── Max steps reached? ────────────► Fallback LLM synthesis
│              └── More work needed? ─────────────► Loop back to Step N+1
└──────────────────────────────────────────────────┘
      │
      ▼
AgentResult(success=True, answer="...", trace=AgentTrace, total_steps=N)
```

### Components (`app/agent/`)

* **`models.py`**:
  - `StepType`: `THOUGHT`, `ACTION`, `OBSERVATION`, `ANSWER`
  - `AgentStep`: Immutable record of a single step in the reasoning chain
  - `AgentTrace`: Collection of steps with formatted printable output
  - `AgentResult`: Final outcome containing the final answer, trace, success status, and step count
* **`runner.py` (`AgentRunner`)**:
  - Decoupled from `ConversationEngine`
  - Drives autonomous multi-turn loops up to `max_steps`
  - Tolerates missing tools and policy rejections by passing error messages as observations
  - Executes fallback synthesis if step budget is exhausted

---

# Current Core Modules

### Implemented

* Configuration System (YAML loader, typed Pydantic models)
* Logging System (structured logs, console + file handlers)
* Conversation Engine (multi-turn dialogue management)
* Session Management (sliding history window)
* Prompt Builder (dynamic context composition with memory and RAG injection)
* LLM Abstraction (`BaseLLM`, `LLMFactory`) & Ollama Provider
* Memory Foundation (`BaseMemoryStore`, `JsonMemoryStore`, semantic vector retrieval, consolidation)
* Tool Framework (`BaseTool`, `ToolRegistry`, `ToolExecutor`, `ToolPolicy`, built-in tools)
* Retrieval-Augmented Generation (`RAGPipeline`, `DocumentLoaderFactory`, `TextChunker`, `JsonChunkStore`, startup re-indexing)
* Agentic ReAct Loop (`AgentRunner`, `AgentTrace`, multi-step autonomous execution)
* Diagnostics (`Doctor`, environment & daemon check suite)
* Debug System (`DebugCollector`, `DebugRenderer`)
* Bootstrap Layer (`ApplicationBuilder` composition root)
* CLI (`chat`, `run`, `index`, `doctor`, `version`)

### Planned

* AI Framework Integrations (LangChain & LangGraph adapters)
* Web Intelligence & Browser Automation
* Voice System (Whisper STT, Piper TTS)
* Multi-Agent Collaboration & Role Delegation
* Production REST API & Packaging

---

# Current Status

### Current Version

**v0.6.0**

### Completed Epics

* Phase 0 – Engineering Foundations ✅
* Phase 1 – Core Conversation Engine ✅
* Phase 2 – Engineering Excellence ✅
* Phase 3 – Long-Term Memory System ✅
* Phase 4 – Extensible Tool Framework ✅
* Phase 5 – Retrieval-Augmented Generation (RAG) ✅
* Phase 6 – Agentic ReAct Loop ✅

The next architectural milestone is **Phase 7: AI Framework Integrations (LangChain & LangGraph)**.

