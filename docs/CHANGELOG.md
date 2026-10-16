# Changelog

All notable changes to Aether will be documented in this file.

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