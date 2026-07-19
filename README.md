# NightCode-JARVIS

## V1.0.0

NightCode-JARVIS V1 is a developer-assistant foundation for safe, local repository workflows.

### Capabilities

- Read-only project analysis, repository exploration, Python symbol discovery, and code explanation.
- Structured patch proposals with explicit approval required before safe application and timestamped backup creation.
- Allowlisted terminal execution with captured output and timeouts.
- Read-only Git status, diff, log, branch, and repository summaries.
- A dependency-injected `JarvisService` facade composing coding, terminal, Git, and safe-apply services.

V1 does not add voice, desktop UI, networking, autonomous editing, or destructive Git/terminal operations.

### Usage

```python
from app.jarvis import JarvisService

jarvis = JarvisService(
    coding=coding_service,
    terminal=terminal_assistant,
    git=git_assistant,
    safe_apply=safe_apply_service,
)

project = jarvis.analyze_project()
files = jarvis.list_files(".py")
```

All dependencies are supplied explicitly so applications retain control over repository roots, command execution, and patch approval.

## Technology

- Python / FastAPI backend
- React / Tailwind CSS frontend
- MongoDB persistence
