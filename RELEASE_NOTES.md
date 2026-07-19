# NightCode-JARVIS v2.3.1

## Overview

NightCode-JARVIS v2.3.1 establishes a reliable release foundation for the
read-only AI generation capability completed in V2.3. It centralizes the
application version and documents the supported architecture and safety model.

## Major capabilities

- Repository exploration, file reading, and code explanation.
- Patch proposal generation with explicit safe-apply controls.
- Read-only Git and allowlisted terminal assistants.
- Approval-gated mission planning, export, lifecycle, and review workflows.
- Multi-provider registration and active-provider selection.
- Local Ollama discovery, health status, and model selection.
- Provider-agnostic, typed, non-streaming AI generation.

## Available commands

- Core: `help`, `version`, `analyze`, `files`, `read <path>`, `history`, `exit`.
- Code assistance: `explain <path|symbol>`, `patch <path>`.
- Repository tools: `git status`, `git diff`, `git log`, `run <allowed-command>`.
- Missions: `mission`, `mission status`, `mission next`, `mission preview`,
  `mission roadmap`, `mission blueprint`, `mission rules`, `mission execute`,
  `mission approve`, `mission reject`, `mission complete`, `mission reset`,
  `mission export`, `mission export codex`, `mission review`, `mission verify`,
  `mission report`.
- Providers: `provider`, `provider list`, `provider current`, `provider models`,
  `provider switch <provider>`.
- AI: `ai ask "<prompt>"`.

## Architecture summary

The CLI receives user requests and delegates them to injected services. The
ProviderManager owns provider registration and active selection. GenerationService
uses only the active provider contract, while provider implementations own their
transport details. Mission planning and review remain independent from generation.

## Safety boundaries

AI generation is read-only. It can answer questions and display responses, but it
cannot modify files, generate or apply patches, execute commands, alter missions,
commit changes, push branches, or create Git tags autonomously.

## Known limitations

- Ollama must be installed and running locally for Ollama-backed generation.
- Generation is non-streaming and maintains no conversation memory.
- External hosted providers remain unavailable placeholders.
- Specialized Engineering Skills are not part of the V2.3 stable capability.

## Next planned milestone

V2.4 Engineering Skills will introduce reusable, read-only engineering commands
on top of GenerationService.
