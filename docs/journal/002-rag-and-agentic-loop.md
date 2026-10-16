# Engineering Journal #002

**Date:** 2026-10-16  
**Project Phases:** Phase 5 (Retrieval-Augmented Generation) & Phase 6 (Agentic ReAct Loop)  
**Milestone:** v0.6.0  
**Test Suite:** 269 passed | 90% test coverage  

---

# Objective

1. Build a local-first, persistent Retrieval-Augmented Generation (RAG) system to ground LLM conversations in external documents with verifiable citations.
2. Build an autonomous ReAct (Reason -> Act -> Observe) agentic loop capable of multi-step problem solving and tool chaining.

---

# Work Completed

## Phase 5 — Retrieval-Augmented Generation (RAG)
- **Document Ingestion**: Created `DocumentLoaderFactory` with `TextLoader` and `MarkdownLoader`, supporting recursive directory traversal.
- **Sliding-Window Chunking**: Designed `TextChunker` with configurable window size, overlap, and natural boundary snapping (whitespace and newlines) to avoid slicing words or sentences.
- **Persistent Storage**: Implemented `JsonChunkStore` to store chunks on disk at `data/rag_chunks.json`.
- **Startup Re-indexing**: Wired `rag_pipeline.reindex()` into `ApplicationBuilder` so indexed documents are embedded into the in-memory vector store upon application startup.
- **Source Deduplication**: Ensured `DocumentIndexer` deduplicates chunks by source file path so re-indexing modifies chunks cleanly in-place.
- **Context Injection & Citations**: Formatted retrieved passages as bracketed references (`[1]`, `[2]`) injected into system context for grounded answers.
- **CLI Ingestion**: Implemented `aether index <path>` command.

## Phase 6 — Agentic ReAct Loop
- **Data Models**: Created `AgentStep`, `AgentTrace`, `AgentResult`, and `StepType` (`THOUGHT`, `ACTION`, `OBSERVATION`, `ANSWER`).
- **ReAct Orchestrator**: Implemented `AgentRunner` in `app/agent/runner.py`, decoupled from `ConversationEngine`.
- **Reasoning & Tool Execution**: Captured LLM reasoning text alongside tool requests, dispatched tool execution via `ToolExecutor` / `ToolPolicy`, and fed back results as observations.
- **Step Budgeting & Graceful Fallback**: Protected against infinite loops with `--max-steps`; synthesized a best-effort response if the budget is reached.
- **Error Feedback**: Converted missing tools and policy rejections into observation text, enabling the LLM to self-correct.
- **CLI Subcommand**: Added `aether run GOAL [--max-steps N] [--show-trace]`.

---

# Major Lessons Learned

1. **Decoupling Chat from Autonomous Agents**: Chat sessions require conversational continuity, turn management, and memory consolidation; agentic loops require goal focus, tight reasoning-action feedback, and step budgets. Keeping `ConversationEngine` and `AgentRunner` distinct avoids compromising either workflow.
2. **Persistence vs. In-Memory Search**: Storing chunks in JSON on disk while serving search via in-memory cosine vectors gives the speed of local vectors with the persistence of file storage, with re-indexing bridging the gap on startup.
3. **Boundary Snapping in Chunkers**: Blind character slicing breaks sentences and words. Snapping backwards to whitespace or newlines significantly improves embedding coherence.
4. **Resilient Feedback Loops**: Rather than crashing on tool errors or permission denials, feeding the failure description back into the LLM as an observation allows autonomous agents to recover or try alternative strategies.
