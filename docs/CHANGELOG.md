# Changelog

All notable changes to Aether will be documented in this file.

## [0.10.0] - Phase 10: Multi-Agent System

### Added

- **Multi-Agent Architecture (`app/multi_agent/`)**:
  - `models.py`: Typed Pydantic models for `AgentRole`, `TaskStatus`, `SubTask`, `TaskPlan`, `AgentMessage`, `SpecialistResult`, and `TeamResult`.
  - `blackboard.py`: `Blackboard` shared context bus tracking artifacts, subtask outputs, inter-agent messages, and dependency summaries.
  - `base.py`: `BaseSpecialistAgent` abstract base class with ReAct runner integration and direct LLM generation.
  - `agents/`:
    - `PlannerAgent`: Decomposes high-level goals into structured `TaskPlan`s with dependencies and assigned roles.
    - `ResearchAgent`: Specialist for fact gathering, web exploration, and document analysis.
    - `CoderAgent`: Specialist for software engineering, file operations, Python execution, and testing.
    - `ReviewerAgent`: Specialist for code review, verification, safety validation, and QA critique.
    - `CoordinatorAgent`: High-level supervisor directing the team and synthesizing polished user deliverables.
  - `team.py`:
    - `AgentTeam`: High-level orchestrator executing the full collaborative workflow (`solve()`) and direct specialist delegation (`delegate()`).
  - `tools/delegate_tool.py`:
    - `DelegateTaskTool` (`delegate_task`): Tool allowing agents to dynamically delegate subtasks to specialists during execution.
- **Application Integration**:
  - `app.team`: Direct access to `AgentTeam` on the `Application` facade.
  - `ApplicationBuilder`: Instantiates and wires `AgentTeam` into the composition root.
- **CLI Subcommand**:
  - `aether team "GOAL" [--no-plan]`: Command to launch collaborative multi-agent problem solving.

### Tested

- 14 new unit tests across multi-agent models, blackboard, specialists, team orchestrator, and delegate tool.

---

## [0.9.0] - Phase 9: Voice

### Added

- **Voice Subsystem (`app/voice/`)**:
  - `models.py`: Typed Pydantic models for `AudioData`, `TranscriptionResult`, `SpeechResult`, and `VoiceConfig`.
  - `stt/`:
    - `BaseSTT`: Abstract interface for Speech-to-Text transcription.
    - `WhisperSTT`: Local Whisper integration supporting `faster-whisper` and `openai-whisper`.
    - `MockSTT`: Deterministic STT provider for fast, repeatable testing.
  - `tts/`:
    - `BaseTTS`: Abstract interface for Text-to-Speech synthesis and playback.
    - `Pyttsx3TTS`: 100% offline local speech synthesis using native system drivers (`pyttsx3`).
    - `MockTTS`: Mock TTS engine recording spoken text for test verification.
  - `wakeword/`:
    - `BaseWakeWordDetector`: Abstract wake word detection interface.
    - `KeywordWakeWordDetector`: Regex-normalized wake word triggering ("Aether", "Hey Aether").
  - `pipeline.py`:
    - `VoicePipeline`: High-level coordinator linking STT, wake word detection, `ConversationEngine`, and TTS.
  - `tools/speak_tool.py`:
    - `SpeakTool` (`speak`): Tool allowing both conversational agents and ReAct runners to speak aloud to the user.
- **Application Bootstrap Integration**:
  - `app.voice`: Direct access to `VoicePipeline(engine=engine)` on the `Application` facade.
  - Default tool registry expanded to 11 built-in tools (including `speak`).

### Tested

- 346 total unit tests passing with 89% code coverage (20 new tests across STT, TTS, wake word, voice pipeline, and SpeakTool).

---

## [0.8.0] - Phase 8: Web Intelligence

### Added

- **Web Intelligence Subsystem (`app/web/`)**:
  - `models.py`: Typed Pydantic data models for `WebSearchResult`, `WebPageContent`, and `WebResearchReport`.
  - `search.py`: `BaseWebSearch` and `DuckDuckGoSearch` implementing zero-API-key internet search with redirect URL unquoting and network error resilience.
  - `extractor.py`: `ContentExtractor` leveraging BeautifulSoup to strip boilerplate (scripts, styles, headers, footers, navs, iframes), extract titles, meta descriptions, and clean article body text.
  - `scraper.py`: `WebScraper` fetching web pages over HTTP/HTTPS with realistic browser headers, redirect handling, and size caps.
  - `pipeline.py`: `WebPipeline` coordinating search, page scraping, and LLM-grounded multi-source research synthesis.
  - `tools/search_tool.py`: `WebSearchTool` (`web_search`) enabling conversational and autonomous agents to query the internet.
  - `tools/scrape_tool.py`: `WebScrapeTool` (`web_scrape`) enabling agents to read and digest webpage text content.
- **Application Bootstrap Integration**:
  - `app.web`: Direct access to `WebPipeline(llm=llm)` on the `Application` instance.
  - `create_default_registry()` now provides 10 built-in tools (including `web_search` and `web_scrape`).
- **Multi-Page PDF Ingestion**:
  - `PDFLoader`: Page-by-page text extraction for PDFs in RAG using `pypdf`.

### Tested

- 326 total unit tests passing with 89% code coverage.
- Full unit test suites for HTML extraction, DuckDuckGo search parsing, scraping timeouts, web tools, and pipeline research synthesis.

---

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