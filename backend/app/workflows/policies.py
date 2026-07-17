"""Workflow policy engine - controls action permissions."""
from dataclasses import dataclass, field
from typing import Any, Optional

from .actions import WorkflowAction


# Safe actions that don't require approval
SAFE_ACTIONS = {
    WorkflowAction.ANALYZE_PROJECT.value,
    WorkflowAction.RUN_REVIEW.value,
    WorkflowAction.CREATE_PLAN.value,
    WorkflowAction.VALIDATE_PATCH.value,
    WorkflowAction.STORE_KNOWLEDGE.value,
}

# Risky actions that require approval
RISKY_ACTIONS = {
    WorkflowAction.GENERATE_PATCH.value,
    WorkflowAction.APPLY_PATCH.value,
}


@dataclass
class PolicyDecision:
    """Result of policy evaluation."""
    allowed: bool
    requires_approval: bool
    reason: str = ''

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'allowed': self.allowed,
            'requires_approval': self.requires_approval,
            'reason': self.reason,
        }


class WorkflowPolicyEngine:
    """Controls which actions are allowed in workflows."""

    def evaluate_action(self, action_name: str) -> PolicyDecision:
        """
        Evaluate if an action is allowed.

        Args:
            action_name: The action to evaluate.

        Returns:
            PolicyDecision with allowed status and approval requirements.
        """
        if action_name in SAFE_ACTIONS:
            return PolicyDecision(
                allowed=True,
                requires_approval=False,
                reason=f'Action {action_name} is safe and allowed',
            )

        if action_name in RISKY_ACTIONS:
            return PolicyDecision(
                allowed=True,
                requires_approval=True,
                reason=f'Action {action_name} requires approval',
            )

        return PolicyDecision(
            allowed=False,
            requires_approval=False,
            reason=f'Unknown action: {action_name}',
        )

    def requires_approval(self, action_name: str) -> bool:
        """
        Check if action requires approval.

        Args:
            action_name: The action to check.

        Returns:
            True if approval required, False otherwise.
        """
        return action_name in RISKY_ACTIONS


def get_policy_engine() -> WorkflowPolicyEngine:
    """Get singleton policy engine instance."""
    return WorkflowPolicyEngine()