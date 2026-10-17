# Changelog

All notable changes to Aether will be documented in this file.

## [0.7.0] - Phase 7: AI Framework Integrations (LangChain & LangGraph)

### Added

- **Modular Framework Integrations (`app/integrations/`)**:
  - `langchain/prompts.py`: `LangChainPromptTemplate`, `MessagePromptTemplate`, `ChatPromptTemplate` supporting string and message templating with variable substitution.
  - `langchain/tools.py`: Bidirectional adapters:
    - `AetherToolAdapter`: Converts any Aether `BaseTool` into an LC-compatible tool with auto-inferred Pydantic `args_schema` and `invoke()` / `run()`.
    - `LangChainToolAdapter`: Wraps third-party LangChain tools into an Aether `BaseTool` with schema discovery for use in `ToolRegistry` and `AgentRunner`.
  - `langchain/llm.py`: `AetherLangChainLLM` wrapping Aether's `BaseLLM` with `.invoke()`, `.generate()`, and `.bind_tools()`.
  - `langchain/chains.py`: `AetherChain` supporting the LCEL pipe syntax (`prompt | llm | transform`) and `RouterChain` for conditional chain branch selection.
  - `langgraph/state.py`: `GraphState` schema and `append_reducer` for monotonic message/step state accumulation.
  - `langgraph/graph.py`: `StateGraph` and `CompiledGraph` supporting nodes, directed edges, conditional router edges, streaming state generators, and step budget protection.
  - `langgraph/agent.py`: `GraphReActAgent` orchestrating cyclic Reason -> Act -> Observe loops with state checkpointing using the graph engine.
- **Bootstrap integration**:
  - `Application.get_langchain_model()`: Factory method exposing the active LLM as a LangChain-compatible model.
  - `Application.create_graph_agent()`: Factory method instantiating a `GraphReActAgent` backed by the application's engine and tool executor.

### Tested

- 25 new unit tests across prompts, tools, LLMs, LCEL chains, graph states, state graphs, and graph agents.
- 294/294 tests passing with zero regressions and clean Ruff linting/formatting.

---

## [0.6.0] - Phase 6: Agentic ReAct Loop

### Added

- **Agent Module (`app/agent/`)**:
  - `models.py`: `AgentStep`, `AgentTrace`, `AgentResult`, `StepType` -- data models for the full reasoning trace.
  - `runner.py`: `AgentRunner` -- implements the ReAct (Reason -> Act -> Observe) agentic loop:
    - Iterates up to `max_steps` think/act/observe cycles.
    - Captures LLM reasoning as `THOUGHT` steps alongside tool calls.
    - Executes tools via `ToolExecutor` / `ToolPolicy` and records `OBSERVATION` steps.
    - Terminates cleanly when the LLM produces a plain-text answer.
    - Gracefully handles max-steps exhaustion by prompting the LLM for a best-effort synthesis.
    - Handles tool-not-found and policy-denial errors as observations (loop continues).
  - `__init__.py`: Public exports for the `app.agent` package.
- **Bootstrap integration**:
  - `ApplicationBuilder` constructs an `AgentRunner` and injects it into `Application.agent`.
  - `Application` now exposes `.agent` for any caller (CLI, API, tests).
- **CLI `run` command**:
  - `aether run GOAL` -- runs the agentic loop for any natural-language goal.
  - `--max-steps N` flag controls the step budget (default: 20).
  - `--show-trace` flag prints the full Thought/Action/Observation/Answer trace.

### Tested

- 21 new unit tests covering models, direct answers, single and multi-step tool calls, max-steps exhaustion, fallback synthesis, missing tools, and policy denials.
- 269/269 tests passing with 90% total test coverage.

---

## [0.5.0] - Phase 5: Retrieval-Augmented Generation (RAG)

### Added

- **RAG Architecture (`app/rag/`)**:
  - `models.py`: `Document`, `Chunk`, `SearchResult` models.
  - `stores/chunk_store.py`: `BaseChunkStore` interface and `InMemoryChunkStore`.
  - `stores/json_store.py`: `JsonChunkStore` for persistent on-disk chunk storage (`data/rag_chunks.json`).
  - `loader.py`: `TextLoader`, `MarkdownLoader`, and `DocumentLoaderFactory` with directory traversal.
  - `chunker.py`: `TextChunker` featuring configurable sliding window, overlap, and natural boundary snapping (newlines/whitespace).
  - `indexer.py`: `DocumentIndexer` orchestrating document loading, chunking, deduplication by source, embedding, and dual-storage.
  - `retriever.py`: `DocumentRetriever` supporting cosine similarity search, result scoring, and minimum score thresholding.
  - `pipeline.py`: `RAGPipeline` high-level facade unifying indexing, retrieval, startup re-indexing (`reindex()`), and contextual snippet formatting with citations.
- **Engine & System Prompt Integration**:
  - `ConversationEngine` supports optional `RAGPipeline` for automatic query retrieval per chat turn.
  - `PromptBuilder` formats retrieved passages with source citations directly into system context.
  - `DebugCollector` logs RAG retrieval events and chunk counts.
- **Configuration & Bootstrap**:
  - Added `RAGSettings` to `Settings` (`enabled`, `chunk_size`, `chunk_overlap`, `retrieval_limit`, `min_score`).
  - `ApplicationBuilder` wired to instantiate `JsonChunkStore` and automatically run `rag_pipeline.reindex()` on startup.
- **CLI `index` Command & Windows UTF-8 Support**:
  - Added `aether index <path>` CLI command with `--no-recursive` option to index files and directories from the command line into persistent storage.
  - Configured CLI `main.py` entry point with UTF-8 encoding support for Windows terminal diagnostics.

### Tested

- 44 new unit tests covering models, in-memory and persistent JSON chunk stores, loaders, chunkers, indexers, retrievers, pipelines, CLI commands, and engine RAG integration.
- 248/248 tests passing with 91% total test coverage.


## [0.4.1]

### Fixed

- **Memory semantic search on restart**: Existing memories from disk are now
  re-indexed into the in-memory vector store at startup so semantic search
  works immediately after a restart (`MemoryManager.reindex()`).
- **Near-duplicate memory extraction**: `MemoryExtractor` now returns at most
  one `MemoryRecord` per message (first matching pattern wins), preventing
  duplicate records when a message matches multiple patterns.
- **Duplicate extraction in `Application.chat()`**: Removed redundant second
  extraction pass that ran after the engine had already extracted memories,
  causing every memory to be stored twice per turn.
- **Tool history bug (context overflow)**: Added `history_window` to
  `Session.get_messages()` that limits the number of messages sent to the LLM.
  The window is aligned to a USER message boundary so tool-result / assistant
  pairs are never orphaned at the start of the context. Configurable via
  `settings.session.history_window` (default: 20 messages).

### Added

- `MemoryManager.reindex()` — re-embeds all persisted memories into the vector
  store on startup.
- `Session.get_messages(window=N)` — returns the most recent N messages,
  snapped to the nearest USER turn.
- `SessionSettings` config model with `history_window` field.

### Tested

- New unit tests for `MemoryManager.reindex()`.
- New unit tests for `Session.get_messages(window=...)`.
- Updated `test_extract_multiple_memories` to reflect new single-record behaviour.
- All builder tests now mock `MemoryManager.reindex` to stay unit-level.

## [0.2.0] 

### Added

- Application bootstrap
- ApplicationBuilder
- Command-line interface
- Version command
- Chat command
- Diagnostics subsystem
- Debug subsystem

### Improved

- Project architecture
- Test coverage to 92%
- Continuous Integration


## v0.3.0

### Added
- Persistent memory system
- Semantic retrieval
- Embedding abstraction
- Vector store
- Memory summarization
- Memory consolidation

### Improved
- Cleaner retrieval architecture
- Better dependency injection

### Tested
- Full unit and integration test coverage