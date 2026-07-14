# Tools Used in Aether

This document explains the primary development tools used throughout the project and the reasoning behind each choice.

---

# uv

## Purpose

Modern Python package and environment management.

## Chosen Because

* Extremely fast
* Unified package management
* Virtual environment management
* Dependency synchronization
* Modern replacement for pip + venv

## Alternatives Considered

* pip
* Poetry
* Pipenv

---

# Ruff

## Purpose

Linting and formatting.

## Chosen Because

* Extremely fast
* Modern Python standard
* Replaces multiple older tools
* Built-in import sorting
* Consistent code style

## Alternatives Considered

* Black
* Flake8
* isort

---

# Pytest

## Purpose

Automated testing.

## Chosen Because

* Industry standard
* Excellent fixture system
* Rich plugin ecosystem
* Simple syntax
* Easy integration testing

## Alternatives Considered

* unittest
* nose2

---

# pytest-cov

## Purpose

Code coverage reporting.

## Chosen Because

* Seamless integration with Pytest
* Coverage measurement
* Helps identify untested code

## Alternatives Considered

* coverage.py (standalone)

---

# Pydantic

## Purpose

Data validation and typed models.

## Chosen Because

* Strong type safety
* Excellent developer experience
* Automatic validation
* JSON serialization
* Modern Python support

Current Usage

* Configuration models
* Message models
* Response models
* Memory models

## Alternatives Considered

* dataclasses
* attrs

---

# PyYAML

## Purpose

Configuration management.

## Chosen Because

* Human-readable configuration
* Widely adopted
* Easy environment customization

## Alternatives Considered

* JSON
* TOML

---

# Ollama

## Purpose

Run local Large Language Models.

## Chosen Because

* Local execution
* Privacy-first
* Open-source ecosystem
* Supports multiple models
* No mandatory API costs

## Alternatives Considered

* OpenAI API
* LM Studio
* llama.cpp

---

# Git

## Purpose

Version control.

## Chosen Because

* Industry standard
* Branching workflow
* Complete project history
* Collaboration support

---

# GitHub

## Purpose

Repository hosting and collaboration.

## Chosen Because

* Pull Requests
* Issues
* Releases
* GitHub Actions
* Community visibility

---

# GitHub Actions

## Purpose

Continuous Integration.

## Chosen Because

* Automatic test execution
* Automatic linting
* Native GitHub integration
* Free for public repositories

Current Workflows

* Ruff
* Pytest

---

# VS Code

## Purpose

Primary development environment.

## Chosen Because

* Excellent Python support
* Strong debugging tools
* Large extension ecosystem
* Integrated terminal

---

# Design Philosophy

Tool selection follows the same engineering principles as the rest of Aether.

Every tool should:

* Improve developer productivity.
* Improve maintainability.
* Support modern Python development.
* Reduce unnecessary complexity.
* Prefer open-source solutions whenever practical.
