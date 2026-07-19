from ..memory.base import Command
from ..memory.registry import register_command
from ..version import __version__

@register_command("system_status")
class SystemStatusCommand(Command):
    """
    A command to retrieve the current status of the JARVIS system.
    """

    def execute(self, params: dict) -> str:
        """
        Executes the system status command, returning information about
        JARVIS status, version, and available modules.

        Args:
            params: A dictionary of parameters (not used for this command).

        Returns:
            A string detailing the system status.
        """
        jarvis_status = "Operational"
        available_modules = ["system_status", "memory_manager"] # Placeholder

        status_report = (
            f"JARVIS Status: {jarvis_status}\n"
            f"Version: {__version__}\n"
            f"Available Modules: {', '.join(available_modules)}"
        )
        return status_report
