"""Interactive CLI entry point."""

from pathlib import Path
from typing import Callable, Optional

from app.coding import (
    CodeExplainer,
    CodingService,
    FileReader,
    PatchGenerator,
    ProjectAnalyzer,
    PythonSymbolIndex,
    RepositoryExplorer,
    SafeApplyService,
)
from app.git import GitAssistant
from app.jarvis import JarvisService, MissionReviewer, MissionService
from app.jarvis.exporter import MissionExporter
from app.providers import GenerationService, ProviderManager, create_default_provider_manager
from app.terminal import TerminalAssistant
from app.version import __version__

from .commands import CLICommands


def start_cli(
    service_factory: Optional[Callable[[], JarvisService]] = None,
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], None] = print,
    mission_factory: Optional[Callable[[], MissionService]] = None,
    provider_factory: Optional[Callable[[], ProviderManager]] = None,
) -> None:
    """Start the interactive CLI and continue until exit or end-of-input."""
    factory = service_factory or _create_jarvis_service
    try:
        service = factory()
    except Exception as exc:
        output_func(f"Error: Unable to start JarvisService: {exc}")
        return
    try:
        mission = (mission_factory or _create_mission_service)()
    except Exception as exc:
        output_func(f"Error: Unable to start MissionService: {exc}")
        return
    reviewer = MissionReviewer(mission, service.git_status, Path.cwd())
    providers = (provider_factory or create_default_provider_manager)()
    generation = GenerationService(providers)
    commands = CLICommands(
        service,
        output_func,
        mission,
        MissionExporter(mission),
        reviewer,
        providers,
        generation,
    )
    output_func(f"NightCode-JARVIS v{__version__}")

    while True:
        try:
            command = input_func("jarvis > ")
        except (EOFError, KeyboardInterrupt, StopIteration):
            output_func("Goodbye.")
            return
        except Exception as exc:
            output_func(f"Error: Unable to read input: {exc}")
            continue
        if not commands.execute(command):
            return


def _create_jarvis_service() -> JarvisService:
    project_root = Path.cwd()
    explorer = RepositoryExplorer(project_root)
    reader = FileReader(project_root)
    symbols = PythonSymbolIndex(project_root, explorer=explorer)
    explainer = CodeExplainer(project_root, reader=reader, symbol_index=symbols)
    coding = CodingService(
        analyzer=ProjectAnalyzer(project_root),
        explorer=explorer,
        symbol_index=symbols,
        reader=reader,
        explainer=explainer,
        patch_generator=PatchGenerator(project_root, reader=reader),
    )
    return JarvisService(
        coding=coding,
        terminal=TerminalAssistant(working_directory=project_root),
        git=GitAssistant(project_root),
        safe_apply=SafeApplyService(project_root),
    )


def _create_mission_service() -> MissionService:
    return MissionService(Path.cwd() / "jarvis")


if __name__ == "__main__":
    start_cli()
