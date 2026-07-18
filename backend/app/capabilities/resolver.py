"""Capability Resolver - resolves goals to tools through capabilities."""

from typing import Any, Dict, List, Optional

from .graph import CapabilityGraph
from .matcher import CapabilityMatcher
from .models import CapabilityMatch, CapabilityResult
from .registry import CapabilityRegistry


class CapabilityResolver:
    """
    Resolves goals through capabilities to tools.

    Uses CapabilityMatcher to find capabilities, then resolves
    to actual tool names and execution paths.
    """

    def __init__(
        self,
        graph: Optional[CapabilityGraph] = None,
        matcher: Optional[CapabilityMatcher] = None,
    ):
        """Initialize with optional graph and matcher."""
        self._graph = graph or CapabilityGraph()
        self._matcher = matcher

    def resolve(self, goal: str) -> CapabilityResult:
        """
        Resolve a goal to a capability and tool.

        Args:
            goal: Natural language goal to resolve.

        Returns:
            CapabilityResult with the matched capability and tool.
        """
        matches = self._matcher.match(goal) if self._matcher else []

        if not matches:
            return CapabilityResult(
                capability_match=CapabilityMatch(
                    capability=None,
                    confidence=0.0,
                    match_reason="No matching capability found",
                ),
                tool_name="",
                success=False,
                message="No capability matches the goal",
            )

        best_match = matches[0]
        capability = best_match.capability

        if not capability:
            return CapabilityResult(
                capability_match=best_match,
                tool_name="",
                success=False,
                message="Capability not found in registry",
            )

        tool_name = capability.metadata.provider
        execution_path = self._graph.get_execution_path(capability.id)

        return CapabilityResult(
            capability_match=best_match,
            tool_name=tool_name,
            execution_path=execution_path,
        )

    def resolve_with_alternatives(self, goal: str, top_n: int = 3) -> List[CapabilityResult]:
        """
        Resolve a goal returning multiple alternatives.

        Args:
            goal: Natural language goal to resolve.
            top_n: Maximum number of alternatives to return.

        Returns:
            List of CapabilityResult objects.
        """
        matches = self._matcher.match(goal, top_n=top_n) if self._matcher else []

        results = []
        for match in matches:
            if match.capability:
                tool_name = match.capability.metadata.provider
                execution_path = self._graph.get_execution_path(match.capability.id)
                results.append(
                    CapabilityResult(
                        capability_match=match,
                        tool_name=tool_name,
                        execution_path=execution_path,
                    )
                )

        return results