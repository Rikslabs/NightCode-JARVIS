"""Optimization engine for learning suggestions."""

from typing import Any, Dict, List

from .models import (
    OptimizationSuggestion,
    FailurePattern,
    SuccessPattern,
)


class OptimizationEngine:
    """Generates optimization suggestions from learning data."""

    def __init__(self):
        self._suggestions: List[OptimizationSuggestion] = []
        self._failure_patterns: List[FailurePattern] = []
        self._success_patterns: List[SuccessPattern] = []

    def suggest_improvement(
        self,
        tool_name: str,
        current_confidence: float,
    ) -> OptimizationSuggestion:
        """Generate an improvement suggestion for a tool."""
        suggested = min(1.0, current_confidence + 0.1)
        suggestion = OptimizationSuggestion(
            tool_name=tool_name,
            current_confidence=current_confidence,
            suggested_confidence=suggested,
            reason="Performance analysis suggests confidence boost",
            impact="positive",
        )
        self._suggestions.append(suggestion)
        return suggestion

    def identify_failure_patterns(
        self,
        failures: List[Dict[str, Any]],
    ) -> List[FailurePattern]:
        """Identify patterns in failure data."""
        patterns = []
        error_counts: Dict[str, int] = {}

        for f in failures:
            error_type = f.get("error_type", "unknown")
            error_counts[error_type] = error_counts.get(error_type, 0) + 1

        for error_type, count in error_counts.items():
            if count >= 2:
                pattern = FailurePattern(
                    pattern_id=f"fail_{error_type}",
                    tool_name="multiple",
                    error_type=error_type,
                    occurrence_count=count,
                )
                patterns.append(pattern)
                self._failure_patterns.append(pattern)

        return patterns

    def identify_success_patterns(
        self,
        successes: List[Dict[str, Any]],
    ) -> List[SuccessPattern]:
        """Identify patterns in success data."""
        patterns = []
        tool_confidences: Dict[str, List[float]] = {}

        for s in successes:
            tool = s.get("tool_name", "unknown")
            conf = s.get("confidence", 0.0)
            if tool not in tool_confidences:
                tool_confidences[tool] = []
            tool_confidences[tool].append(conf)

        for tool, confs in tool_confidences.items():
            avg_conf = sum(confs) / len(confs) if confs else 0.0
            pattern = SuccessPattern(
                pattern_id=f"success_{tool}",
                tool_name=tool,
                confidence_level=avg_conf,
                occurrence_count=len(confs),
            )
            patterns.append(pattern)
            self._success_patterns.append(pattern)

        return patterns

    def get_all_suggestions(self) -> List[OptimizationSuggestion]:
        """Get all generated suggestions."""
        return list(self._suggestions)

    def clear(self) -> None:
        """Clear all patterns and suggestions."""
        self._suggestions.clear()
        self._failure_patterns.clear()
        self._success_patterns.clear()