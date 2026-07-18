"""Capability Matcher - deterministic matching of goals to capabilities."""

import re
from typing import List, Optional

from .models import Capability, CapabilityMatch
from .registry import CapabilityRegistry
from .taxonomy import CapabilityTaxonomy


class CapabilityMatcher:
    """
    Matches goals to capabilities using deterministic scoring.

    No AI - pure keyword matching and category scoring.
    """

    # Goal keywords mapped to categories
    CATEGORY_KEYWORDS = {
        "review": "engineering/code_review",
        "analyze": "engineering/architecture_review",
        "security": "engineering/security_review",
        "plan": "planning",
        "feature": "planning",
        "bugfix": "planning",
        "refactor": "planning",
        "edit": "editing",
        "patch": "editing",
        "knowledge": "knowledge",
        "store": "knowledge",
        "remember": "memory",
        "recall": "memory",
        "workflow": "workflow",
        "execute": "workflow",
        "status": "system",
        "diagnostic": "system",
    }

    def __init__(self, registry: Optional[CapabilityRegistry] = None):
        """Initialize with optional capability registry."""
        self._registry = registry or CapabilityRegistry()

    def match(self, goal: str, top_n: int = 5) -> List[CapabilityMatch]:
        """
        Match a goal to capabilities.

        Args:
            goal: Natural language goal to match.
            top_n: Maximum number of matches to return.

        Returns:
            List of CapabilityMatch objects sorted by confidence.
        """
        goal_lower = goal.lower()
        matches = []

        for capability in self._registry.get_all_capabilities().values():
            score = self._calculate_match_score(goal_lower, capability)
            if score > 0:
                matches.append(
                    CapabilityMatch(
                        capability=capability,
                        confidence=score,
                        match_reason=self._get_match_reason(goal_lower, capability),
                    )
                )

        # Sort by confidence descending
        matches.sort(key=lambda m: m.confidence, reverse=True)
        return matches[:top_n]

    def _calculate_match_score(self, goal: str, capability: Capability) -> float:
        """Calculate match score between goal and capability."""
        score = 0.0

        # Check name match
        if capability.metadata.name.lower() in goal:
            score += 0.5

        # Check category match
        category_score = self._match_category(goal, capability.metadata.category)
        score += category_score * 0.3

        # Check tag match
        for tag in capability.tags:
            if tag.lower() in goal:
                score += 0.2

        # Check description match
        if capability.metadata.description:
            desc_words = set(capability.metadata.description.lower().split())
            goal_words = set(goal.split())
            overlap = len(desc_words & goal_words)
            if overlap > 0:
                score += min(0.3, overlap * 0.1)

        return min(1.0, score)

    def _match_category(self, goal: str, category: str) -> float:
        """Match goal to category based on keywords."""
        for keyword, cat in self.CATEGORY_KEYWORDS.items():
            if keyword in goal:
                # Check if category matches or is subcategory of match
                if category == cat or category.startswith(cat + "/"):
                    return 1.0
                # Check parent category match
                if category.startswith(cat.split("/")[0] + "/"):
                    return 0.5
        return 0.0

    def _get_match_reason(self, goal: str, capability: Capability) -> str:
        """Get human-readable match reason."""
        reasons = []

        if capability.metadata.name.lower() in goal:
            reasons.append(f"name match: {capability.metadata.name}")

        if capability.metadata.category in goal or any(
            cat in goal for cat in self.CATEGORY_KEYWORDS.keys()
        ):
            reasons.append(f"category: {capability.metadata.category}")

        for tag in capability.tags:
            if tag.lower() in goal:
                reasons.append(f"tag: {tag}")

        return "; ".join(reasons) if reasons else "keyword overlap"