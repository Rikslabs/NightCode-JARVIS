"""Goal Graph - represents goal dependencies as a graph."""

from typing import Any, Dict, List, Optional, Set
from .models import Goal, GoalDependency, GoalStep, GoalStatus


class GoalGraph:
    """
    Graph representation of goal steps and dependencies.

    Supports cycle detection and parallel execution detection.
    """

    def __init__(self, goal: Optional[Goal] = None):
        """Initialize with optional goal."""
        self._goal = goal
        self._nodes: Set[str] = set()
        self._edges: Dict[str, List[str]] = {}

    def build(self, goal: Goal) -> None:
        """Build graph from goal."""
        self._goal = goal
        self._nodes = {step.id for step in goal.steps}
        self._edges = {}

        for dep in goal.dependencies:
            if dep.step_id not in self._edges:
                self._edges[dep.step_id] = []
            self._edges[dep.step_id].append(dep.depends_on_step_id)

    def get_dependencies(self, step_id: str) -> List[str]:
        """Get dependencies for a step."""
        return self._edges.get(step_id, [])

    def get_dependents(self, step_id: str) -> List[str]:
        """Get steps that depend on this step."""
        dependents = []
        for sid, deps in self._edges.items():
            if step_id in deps:
                dependents.append(sid)
        return dependents

    def has_cycles(self) -> bool:
        """Detect if the graph has cycles."""
        visited = set()
        rec_stack = set()

        def visit(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in self._edges.get(node, []):
                if neighbor not in visited:
                    if visit(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for node in self._nodes:
            if node not in visited:
                if visit(node):
                    return True

        return False

    def get_execution_order(self) -> List[str]:
        """Get topological order of steps."""
        if self.has_cycles():
            return []

        order = []

        # Build reverse adjacency: for each node, who depends on it
        dependents: Dict[str, List[str]] = {n: [] for n in self._nodes}
        # Calculate in-degree: how many dependencies each node has
        in_degree = {n: 0 for n in self._nodes}

        for step_id, deps in self._edges.items():
            in_degree[step_id] = len(deps)
            for dep in deps:
                if dep in dependents:
                    dependents[dep].append(step_id)

        # Kahn's algorithm - start with nodes that have no dependencies
        queue = [n for n in self._nodes if in_degree[n] == 0]
        while queue:
            node = queue.pop(0)
            order.append(node)
            for dependent in dependents[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        return order

    def get_parallel_groups(self) -> List[List[str]]:
        """Get groups of steps that can run in parallel."""
        if self.has_cycles():
            return []

        groups = []
        remaining = set(self._nodes)
        completed = set()

        while remaining:
            # Find all steps with no uncompleted dependencies
            parallel = []
            for step_id in remaining:
                deps = self._edges.get(step_id, [])
                if not (set(deps) - completed):
                    parallel.append(step_id)

            if parallel:
                groups.append(parallel)
                completed.update(parallel)
                remaining -= set(parallel)
            else:
                # Cycle or deadlock - just add remaining
                groups.append(list(remaining))
                break

        return groups

    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary."""
        return {
            "nodes": list(self._nodes),
            "edges": {k: v for k, v in self._edges.items()},
            "has_cycles": self.has_cycles(),
            "execution_order": self.get_execution_order(),
            "parallel_groups": self.get_parallel_groups(),
        }