"""Intent reasoning engine for the Intelligence Orchestrator."""

import re
from typing import Any, Dict, List, Optional

from .models import (
    IntentAnalysis,
    IntentType,
    ComplexityLevel,
    RiskLevel,
    ReasoningContext,
)


class IntentReasoner:
    """
    Analyzes natural language requests to determine intent.

    Pure reasoning logic - does not call AI. Uses pattern matching
    and keyword analysis to classify intents.
    """

    # Intent patterns for classification
    INTENT_PATTERNS: Dict[IntentType, List[str]] = {
        IntentType.REVIEW_PROJECT: [
            r"review.*project",
            r"analyze.*code",
            r"check.*quality",
            r"code.*review",
            r"audit.*project",
        ],
        IntentType.PLAN_FEATURE: [
            r"plan.*feature",
            r"implement.*feature",
            r"add.*feature",
            r"create.*feature",
        ],
        IntentType.PLAN_BUGFIX: [
            r"fix.*bug",
            r"solve.*issue",
            r"debug.*",
            r"bugfix",
            r"resolve.*bug",
        ],
        IntentType.PLAN_REFACTOR: [
            r"refactor",
            r"improve.*structure",
            r"restructure",
            r"cleanup.*code",
        ],
        IntentType.ANALYZE_CODE: [
            r"analyze.*file",
            r"understand.*code",
            r"explain.*code",
            r"what does.*do",
        ],
        IntentType.QUERY_KNOWLEDGE: [
            r"what is.*",
            r"how to.*",
            r"explain.*",
            r"tell me.*",
            r"describe.*",
        ],
        IntentType.EDIT_CODE: [
            r"edit.*code",
            r"modify.*file",
            r"change.*code",
            r"update.*source",
        ],
        IntentType.EXECUTE_WORKFLOW: [
            r"run.*workflow",
            r"execute.*workflow",
            r"workflow.*",
        ],
    }

    # Entity extraction patterns
    ENTITY_PATTERNS: Dict[str, str] = {
        "feature_name": r"(?:feature|implement)\s+['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?",
        "file_path": r"['\"]?([A-Za-z0-9_/.-]+\.py)['\"]?",
        "directory_path": r"(?:in|at)\s+['\"]?([A-Za-z0-9_/.-]+)['\"]?",
        "project_path": r"(?:project|codebase)\s+['\"]?([A-Za-z0-9_/.-]+)['\"]?",
    }

    def analyze(self, context: ReasoningContext) -> IntentAnalysis:
        """
        Analyze a request to determine intent.

        Args:
            context: The reasoning context containing the request.

        Returns:
            IntentAnalysis with the determined intent and metadata.
        """
        request_lower = context.request.lower()

        # Find matching intent
        intent, confidence = self._classify_intent(request_lower)

        # Extract entities
        entities = self._extract_entities(context.request)

        # Determine complexity
        complexity = self._assess_complexity(intent, entities)

        # Determine risk level
        risk = self._assess_risk(intent, complexity)

        # Generate reasoning trace
        reasoning = self._generate_reasoning(context.request, intent, confidence, entities)

        return IntentAnalysis(
            intent=intent,
            confidence=confidence,
            entities=entities,
            complexity=complexity,
            risk=risk,
            reasoning=reasoning,
        )

    def _classify_intent(self, request: str) -> tuple[IntentType, float]:
        """
        Classify the intent based on pattern matching.

        Returns intent type and confidence score.
        """
        best_intent = IntentType.UNKNOWN
        best_confidence = 0.0

        for intent_type, patterns in self.INTENT_PATTERNS.items():
            matches = sum(1 for pattern in patterns if re.search(pattern, request))
            if matches > 0:
                confidence = min(1.0, matches * 0.3 + 0.4)
                if confidence > best_confidence:
                    best_intent = intent_type
                    best_confidence = confidence

        # Default confidence for unknown
        if best_intent == IntentType.UNKNOWN:
            best_confidence = 0.5

        return best_intent, best_confidence

    def _extract_entities(self, request: str) -> List[str]:
        """
        Extract entities from the request.

        Returns list of extracted entity strings.
        """
        entities = []

        for entity_type, pattern in self.ENTITY_PATTERNS.items():
            matches = re.findall(pattern, request, re.IGNORECASE)
            entities.extend(matches)

        return entities

    def _assess_complexity(self, intent: IntentType, entities: List[str]) -> ComplexityLevel:
        """
        Assess the complexity of the intent.

        Simple: Single file operations, basic queries
        Moderate: Multi-file operations, feature planning
        Complex: Full project analysis, architecture changes
        """
        if intent in (IntentType.QUERY_KNOWLEDGE, IntentType.ANALYZE_CODE):
            if len(entities) <= 1:
                return ComplexityLevel.SIMPLE
            return ComplexityLevel.MODERATE

        if intent in (IntentType.REVIEW_PROJECT, IntentType.EXECUTE_WORKFLOW):
            return ComplexityLevel.COMPLEX

        if intent in (IntentType.PLAN_FEATURE, IntentType.PLAN_REFACTOR):
            return ComplexityLevel.COMPLEX

        return ComplexityLevel.MODERATE

    def _assess_risk(self, intent: IntentType, complexity: ComplexityLevel) -> RiskLevel:
        """
        Assess the risk level of the intent.

        Based on the type of operation and its complexity.
        """
        if intent == IntentType.EDIT_CODE:
            return RiskLevel.MEDIUM

        if intent in (IntentType.PLAN_FEATURE, IntentType.PLAN_BUGFIX):
            if complexity == ComplexityLevel.COMPLEX:
                return RiskLevel.HIGH
            return RiskLevel.MEDIUM

        if intent == IntentType.EXECUTE_WORKFLOW:
            return RiskLevel.MEDIUM

        return RiskLevel.LOW

    def _generate_reasoning(self, request: str, intent: IntentType, confidence: float, entities: List[str]) -> str:
        """
        Generate a human-readable reasoning trace.
        """
        return (
            f"Analyzed request '{request[:50]}...' -> identified as '{intent.value}' "
            f"with {confidence:.2f} confidence. Found {len(entities)} entities."
        )