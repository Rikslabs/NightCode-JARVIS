"""Focused tests for the V2.3.1 release foundation."""

from pathlib import Path
from unittest.mock import Mock

from app.cli import start_cli
from app.cli.commands import CLICommands
from app.jarvis import JarvisService, MissionService
from app.version import __version__


def test_version_constant() -> None:
    assert __version__ == "2.3.1"


def test_cli_banner_uses_version_constant() -> None:
    output = []
    commands = iter(("exit",))

    start_cli(
        service_factory=lambda: Mock(spec=JarvisService),
        mission_factory=lambda: Mock(spec=MissionService),
        input_func=lambda prompt: next(commands),
        output_func=output.append,
    )

    assert output[0] == f"NightCode-JARVIS v{__version__}"


def test_version_command_output() -> None:
    output = []

    CLICommands(service=object(), output=output.append).execute("version")

    assert output == [f"NightCode-JARVIS\nVersion: {__version__}"]


def test_active_cli_has_no_stale_v1_1_banner() -> None:
    cli_root = Path(__file__).parents[1] / "app" / "cli"
    sources = "\n".join(
        path.read_text(encoding="utf-8") for path in cli_root.glob("*.py")
    )

    assert "NightCode-JARVIS v1.1" not in sources
