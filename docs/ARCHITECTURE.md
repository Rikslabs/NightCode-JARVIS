# Architecture

**Purpose:** Documents the system architecture, component relationships, and design decisions.

**Status:** Draft  
**Version:** 1.0  
**Last Updated:** YYYY-MM-DD

---

## 1. Architecture Overview

NightCode-JARVIS follows a layered Clean Architecture approach. Each layer has a single responsibility and depends only on layers below it. Dependencies point inward: outer layers depend on inner layers, never the reverse.

```
User
  ↓
API Layer (FastAPI)
  ↓
JarvisBrain (Orchestration)
  ↓
CommandDispatcher (Routing)
  ↓
Commands (Orchestration)
  ↓
Tools (Business Logic)
  ↓
Managers (Storage / Infrastructure)
  ↓
Providers (AI / External)
  ↓
Storage (JSON / Filesystem)
```

- **API Layer**: HTTP entry point. Thin. Delegates to JarvisBrain.
- **Brain**: Orchestrates the processing pipeline. No feature-specific logic.
- **Dispatcher**: Routes messages to commands via the matcher.
- **Commands**: Validate input, call tools, format responses. No business logic.
- **Tools**: Execute business operations. Return structured results. No formatting.
- **Managers**: Wrap infrastructure (file I/O, storage).
- **Providers**: Abstract external services (AI models).
- **Storage**: Persistent data on disk.

---

## 2. Core Components

### 2.1 JarvisBrain

- **File**: `backend/app/brain/jarvis.py`
- **Responsibility**: Main orchestration layer. Receives a user message, delegates to the CommandDispatcher, and falls back to the AI provider if no command matches.
- **Constraints**: Contains no feature-specific logic. Does not know about individual commands or tools.

### 2.2 CommandDispatcher

- **File**: `backend/app/brain/dispatcher.py`
- **Responsibility**: Routes user messages to registered commands. Retrieves command metadata from the registry, passes it to the CommandMatcher, and executes the matched command.
- **Flow**: `get_command_details()` → `matcher.match()` → `get_command()` → `command.execute()`

### 2.3 Command System

- **Files**: `backend/app/commands/`, `backend/app/memory/base.py`, `backend/app/memory/registry.py`
- **Commands are orchestration components**. They:
  - Validate input parameters.
  - Resolve and call the appropriate Tool.
  - Format the Tool's structured result into a user-facing string.
  - Handle edge cases (missing data, errors).
- **Commands do not contain business logic**. Business logic lives in Tools.
- **Registration**: Declarative via `@register_command("intent_name")` decorator. Commands are instantiated once at import time and stored in the Command Registry.

### 2.4 Tool System

- **Files**: `backend/app/tools/`, `backend/app/tools/base.py`, `backend/app/tools/registry.py`
- **Tools contain business logic**. They:
  - Execute a single, focused operation.
  - Accept typed keyword arguments.
  - Return a `ToolResult` dataclass with `success`, `data`, and `error` fields.
  - Have zero knowledge of commands, formatting, or AI.
- **Tools are reusable** across multiple commands and future interfaces (voice, CLI, API).
- **Registration**: Declarative via `@register_tool("name")` decorator. Tools are stateless singletons.

### 2.5 Memory System

- **Files**: `backend/app/memory/manager.py`
- **Responsibility**: Persistent key-value storage for user information. Reads and writes a JSON file on disk.
- **Atomic writes**: Uses a temporary file + rename pattern to prevent data corruption.
- **Accessed by**: `MemoryTool` (the tool layer), which wraps `MemoryManager` and exposes structured get/set/has operations.

### 2.6 AI Provider Layer

- **Files**: `backend/app/ai/provider.py`, `backend/app/ai/ollama.py`
- **Responsibility**: Abstract the AI model backend behind a common interface (`AIProvider` with a `generate(prompt) -> str` method).
- **Current implementation**: `OllamaProvider` uses the `ollama` Python library to call a local model (`qwen2.5-coder:7b`).
- **Extensibility**: New providers implement `AIProvider` and can be swapped in without changing any other layer.

---

## 3. Dependency Rules

Dependencies flow in one direction only:

```
API Layer
  ↓
Brain
  ↓
Commands
  ↓
Tools
  ↓
Managers
  ↓
Providers
```

**Enforced rules:**

- **Tools must not import Commands.** Tools have no knowledge of the command layer.
- **Providers must not know application logic.** Providers receive a prompt string and return a response string. They do not import brain, commands, or tools.
- **Commands must not directly access storage.** Commands call Tools, which wrap Managers. Direct storage access in a command is a violation.
- **No circular dependencies.** The import graph is a DAG. Every layer imports only from layers below it.

---

## 4. Current Folder Architecture

```
backend/app/
├── main.py                 # FastAPI app, routes, imports commands
├── brain/
│   ├── jarvis.py           # JarvisBrain — main orchestrator
│   ├── dispatcher.py       # CommandDispatcher — routes messages to commands
│   └── matcher.py          # CommandMatcher — keyword + LLM intent matching
├── commands/
│   ├── __init__.py
│   ├── system_status.py    # SystemStatusCommand
│   └── memory_commands.py  # RememberNameCommand, GetNameCommand
├── tools/
│   ├── __init__.py
│   ├── base.py             # Tool ABC, ToolResult dataclass
│   ├── registry.py         # ToolRegistry — register, get, list, metadata
│   ├── memory.py           # MemoryTool — wraps MemoryManager
│   └── system.py           # SystemTool — system information
├── memory/
│   ├── __init__.py
│   ├── base.py             # Command ABC
│   ├── registry.py         # CommandRegistry — register, get, details
│   ├── manager.py          # MemoryManager — JSON file storage
│   └── memory.json         # Persistent user data
└── ai/
    ├── __init__.py
    ├── provider.py         # AIProvider ABC
    ├── ollama.py           # OllamaProvider — local LLM via Ollama
    └── prompts.py          # (reserved for prompt templates)
```

---

## 5. Data Flow

### Standard message flow:

```
1. User sends message to POST /chat
2. FastAPI route calls brain.process(message)
3. JarvisBrain.process():
   a. Calls dispatcher.dispatch(message)
   b. Dispatcher retrieves command_details from registry
   c. Dispatcher calls matcher.match(message, command_details)
      i.   Keyword matching (fast path, no LLM call)
      ii.  LLM intent matching (slow path, if keyword fails)
      iii. Returns {"intent": "...", "params": {...}} or None
   d. If matched:
      i.   Dispatcher retrieves command from registry
      ii.  Command.execute(params)
      iii. Command calls Tool via get_tool()
      iv.  Tool returns ToolResult
      v.   Command formats result into response string
      vi.  Returns string
   e. If not matched:
      i.   Returns None
4. If dispatcher returned None:
   a. JarvisBrain calls ai.generate(message) for conversational response
5. Response returned to user
```

### Command matching flow:

```
matcher.match(message, command_details)
  ├── _keyword_match()  — case-insensitive substring match on intent names
  │   → match: return {"intent": "system_status", "params": {}}
  │   → no match: continue
  └── _llm_match()      — LLM classifies intent from descriptions + params
      → match: return {"intent": "remember_name", "params": {"name": "Vikash"}}
      → no match: return None
```

---

## 6. Future Architecture Expansion

The following systems are **planned but not implemented**. They are listed here to guide future development without implying current capability.

- **Voice system**: Speech-to-text input and text-to-speech output. Would sit between the API layer and the Brain, converting audio to text before processing and text to audio after response generation.
- **Vision system**: Multimodal model integration for image analysis. Would be exposed as a Tool (e.g., `VisionTool`) callable by a Command.
- **Plugin system**: Dynamic loading of commands and tools from external directories at runtime, without modifying the core codebase.
- **Event system**: An internal event bus for components to publish and subscribe to events (e.g., "user remembered", "command executed").
- **Scheduler**: Time-based task execution (e.g., reminders, periodic health checks).
- **Provider manager**: Dynamic switching between AI providers at runtime, with fallback logic and model selection per task.
- **Desktop automation**: Tools for window management, keyboard/mouse control, and application launching.
- **Coding agent**: Tools for reading, writing, and refactoring code within a project directory.

All future systems will follow the existing architectural patterns: new capabilities are added as Tools, exposed through Commands, and registered via the existing decorator system.

---

## 7. Architecture Rules

These rules are non-negotiable and must be preserved across all stages of development:

1. **Preserve existing functionality.** No change should break a working endpoint, command, or tool.
2. **Avoid unnecessary rewrites.** Prefer extending existing components over replacing them.
3. **Prefer extension over modification.** New capabilities should add new files, not restructure existing ones.
4. **Single responsibility.** Every class and module has exactly one reason to change.
5. **Explicit dependencies.** Dependencies are declared in `__init__` or imported at the top of the file. No hidden or global state.
6. **Maintain backward compatibility.** Public interfaces (method signatures, return types, API contracts) must not change without a deprecation period.
7. **Tools are AI-agnostic.** Tools must never import or reference AI providers, prompts, or the brain.
8. **Commands are formatting-only.** Commands must never contain business logic that belongs in a Tool.
9. **No circular imports.** The dependency graph must remain a directed acyclic graph.
10. **Document before implementing.** Architecture decisions must be documented before code is written.