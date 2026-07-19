"""Core interactive CLI commands."""

from typing import Callable, List, Optional

from app.jarvis import JarvisService, MissionService, MissionStage


class CLICommands:
    """Dispatch interactive commands to JarvisService."""

    def __init__(
        self,
        service: JarvisService,
        output: Callable[[str], None],
        mission: Optional[MissionService] = None,
    ) -> None:
        self._service = service
        self._output = output
        self._mission = mission
        self._history: List[str] = []

    def execute(self, command: str) -> bool:
        """Execute a command and return whether the CLI should continue."""
        raw_command = command.strip()
        normalized = raw_command.casefold()
        if raw_command:
            self._history.append(raw_command)
        try:
            if normalized == "help":
                self._output(
                    "Available commands: help, clear, exit, analyze, files, read <path>, "
                    "explain <path|symbol>, patch <path>, run <allowed-command>, "
                    "git status, git diff, git log, history, history clear, "
                    "mission, mission status, mission next, mission preview, "
                    "mission roadmap, mission blueprint, mission rules, mission execute, "
                    "mission approve, mission reject, mission complete, mission reset"
                )
                return True
            if normalized == "clear":
                self._output("\033[2J\033[H")
                return True
            if normalized == "exit":
                self._output("Goodbye.")
                return False
            if normalized == "analyze":
                self._analyze()
                return True
            if normalized == "files":
                self._files()
                return True
            if normalized == "git status":
                self._git_status()
                return True
            if normalized == "git diff":
                self._run("git diff")
                return True
            if normalized == "git log":
                self._git_log()
                return True
            if normalized == "history":
                self._show_history()
                return True
            if normalized == "history clear":
                self._history.clear()
                self._output("History cleared.")
                return True
            if normalized in {"mission", "mission status"}:
                self._mission_status()
                return True
            if normalized == "mission next":
                self._mission_stage(self._require_mission().determine_next_stage())
                return True
            if normalized == "mission preview":
                self._mission_stage(self._require_mission().preview_stage())
                return True
            if normalized == "mission roadmap":
                self._mission_roadmap()
                return True
            if normalized == "mission blueprint":
                self._mission_blueprint()
                return True
            if normalized == "mission rules":
                self._mission_rules()
                return True
            if normalized == "mission execute":
                self._mission_execute()
                return True
            if normalized == "mission approve":
                self._require_mission().approve_mission()
                self._output("Mission Approved.\nImplementation may begin.")
                return True
            if normalized == "mission reject":
                self._require_mission().reject_mission()
                self._output("Mission rejected and cancelled.")
                return True
            if normalized == "mission complete":
                state = self._require_mission().complete_mission()
                self._output(
                    f"Mission completed: {state.last_completed_stage}\n"
                    f"Current Version: {state.current_version}"
                )
                return True
            if normalized == "mission reset":
                self._require_mission().reset_mission()
                self._output("Mission reset to IDLE.")
                return True
            if normalized == "read" or normalized.startswith("read "):
                self._read(self._argument(raw_command))
                return True
            if normalized == "explain" or normalized.startswith("explain "):
                self._explain(self._argument(raw_command))
                return True
            if normalized == "patch" or normalized.startswith("patch "):
                self._patch(self._argument(raw_command))
                return True
            if normalized == "run" or normalized.startswith("run "):
                self._run(self._argument(raw_command))
                return True
            self._output("Unknown command.")
            self._output("Type 'help' to see available commands.")
            return True
        except Exception as exc:
            self._output(f"Error: {exc}")
            return True

    def _analyze(self) -> None:
        result = self._service.analyze_project()
        project = result.project
        languages = ", ".join(project.detected_languages) or "none detected"
        self._output(
            f"Project: {project.name}\n"
            f"Languages: {languages}\n"
            f"Files: {project.file_count}\n"
            f"Directories: {project.directory_count}"
        )

    def _files(self) -> None:
        files = self._service.list_files()
        if not files:
            self._output("No files found.")
            return
        self._output("Files:\n" + "\n".join(
            f"- {entry.relative_path} ({entry.size} bytes)" for entry in files
        ))

    def _git_status(self) -> None:
        statuses = self._service.git_status()
        if not statuses:
            self._output("Git status: clean")
            return
        self._output("Git status:\n" + "\n".join(
            f"- {entry.index_status}{entry.worktree_status} {entry.path}"
            for entry in statuses
        ))

    def _read(self, path: str) -> None:
        if not path:
            self._output("Usage: read <path>")
            return
        content = self._service._coding.read_file(path)
        self._output(f"File: {path}\n{content}")

    def _explain(self, target: str) -> None:
        if not target:
            self._output("Usage: explain <path|symbol>")
            return
        try:
            explanation = self._service.explain_file(target)
        except FileNotFoundError:
            explanation = self._service.explain_symbol(target)

        if hasattr(explanation, "module_name"):
            classes = ", ".join(explanation.classes) or "none"
            functions = ", ".join(
                explanation.functions + explanation.async_functions
            ) or "none"
            self._output(
                f"Module: {explanation.module_name}\n"
                f"Language: {explanation.detected_language}\n"
                f"Classes: {classes}\n"
                f"Functions: {functions}"
            )
            return
        self._output(
            f"Symbol: {explanation.name}\n"
            f"Type: {explanation.symbol_type}\n"
            f"Location: {explanation.location}\n"
            f"Parent: {explanation.parent or 'none'}\n"
            f"Signature: {explanation.signature or 'not available'}"
        )

    def _patch(self, path: str) -> None:
        if not path:
            self._output("Usage: patch <path>")
            return
        explanation = self._service.explain_file(path)
        proposal = self._service.generate_patch(
            path,
            explanation,
            f"Prepare a patch proposal for {path}",
        )
        changes = "\n".join(f"- {change}" for change in proposal.proposed_changes)
        details = f"\nChanges:\n{changes}" if changes else ""
        diff = f"\nDiff:\n{proposal.unified_diff}" if proposal.unified_diff else ""
        self._output(
            f"Patch proposal: {proposal.summary}\n"
            f"Reasoning: {proposal.reasoning}{details}{diff}"
        )

    def _run(self, command: str) -> None:
        if not command:
            self._output("Usage: run <allowed-command>")
            return
        result = self._service.run_command(command)
        output = result.stdout.strip()
        error = result.stderr.strip()
        parts = [f"Command: {result.command}", f"Exit code: {result.exit_code}"]
        if output:
            parts.append(f"Output:\n{output}")
        if error:
            parts.append(f"Error:\n{error}")
        self._output("\n".join(parts))

    def _git_log(self) -> None:
        commits = self._service.repository_summary().recent_commits
        if not commits:
            self._output("Git log: no commits")
            return
        self._output("Git log:\n" + "\n".join(
            f"- {commit.commit_hash} {commit.message}" for commit in commits
        ))

    def _show_history(self) -> None:
        if not self._history:
            self._output("History is empty.")
            return
        self._output("History:\n" + "\n".join(
            f"{index}. {entry}" for index, entry in enumerate(self._history, start=1)
        ))

    def _mission_status(self) -> None:
        summary = self._require_mission().mission_summary()
        lifecycle = self._require_mission().mission_status()
        next_name = summary.next_stage.name if summary.next_stage else "none"
        self._output(
            f"Mission Status\n"
            f"Lifecycle: {lifecycle}\n"
            f"Current Version: {summary.current_version}\n"
            f"Target Version: {summary.target_version}\n"
            f"Completed Stages: {summary.completed_stages}/{summary.total_stages}\n"
            f"Active Mission: {summary.active_mission or 'none'}\n"
            f"Next Stage: {next_name}"
        )

    def _mission_stage(self, stage: Optional[MissionStage]) -> None:
        if stage is None:
            self._output("No eligible mission stage.")
            return
        summary = self._require_mission().mission_summary()
        dependencies = ", ".join(stage.dependencies) or "none"
        files = ", ".join(stage.estimated_files) or "none"
        self._output(
            f"Current Version: {summary.current_version}\n"
            f"Target Version: {summary.target_version}\n"
            f"Next Stage: {stage.name} ({stage.id})\n"
            f"Description: {stage.description}\n"
            f"Dependencies: {dependencies}\n"
            f"Estimated Files: {files}\n"
            f"Approval Required: {'yes' if stage.approval_required else 'no'}"
        )

    def _mission_roadmap(self) -> None:
        roadmap = self._require_mission().load_roadmap()
        self._output(f"Roadmap to {roadmap.version}:\n" + "\n".join(
            f"- [{stage.status}] {stage.id}: {stage.name}"
            for stage in roadmap.stages
        ))

    def _mission_blueprint(self) -> None:
        blueprint = self._require_mission().load_blueprint()
        self._output(
            f"Blueprint: {blueprint.project_name}\n"
            f"Current Version: {blueprint.current_version}\n"
            f"Architecture Layers: {', '.join(blueprint.architecture_layers)}\n"
            f"Coding Standards: {', '.join(blueprint.coding_standards)}"
        )

    def _mission_rules(self) -> None:
        rules = self._require_mission().load_rules().rules
        self._output("Mission Rules:\n" + "\n".join(
            f"- {rule}" for rule in rules
        ))

    def _mission_execute(self) -> None:
        stage = self._require_mission().execute_mission()
        self._output(
            f"Mission Name: {stage.name}\n"
            f"Description: {stage.description}\n"
            f"Dependencies: {', '.join(stage.dependencies) or 'none'}\n"
            f"Estimated Files: {', '.join(stage.estimated_files) or 'none'}\n"
            f"Approval Required: {'yes' if stage.approval_required else 'no'}"
        )

    def _require_mission(self) -> MissionService:
        if self._mission is None:
            raise RuntimeError("MissionService is unavailable")
        return self._mission

    @staticmethod
    def _argument(command: str) -> str:
        _, separator, argument = command.partition(" ")
        return argument.strip() if separator else ""
