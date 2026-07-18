"""Capability taxonomy - hierarchical categories for capabilities."""

from typing import List


class CapabilityCategory:
    """Hierarchical capability categories."""

    # Top-level categories
    ENGINEERING = "engineering"
    PLANNING = "planning"
    EDITING = "editing"
    KNOWLEDGE = "knowledge"
    WORKFLOW = "workflow"
    MEMORY = "memory"
    SYSTEM = "system"
    FUTURE = "future"

    # Engineering subcategories
    CODE_REVIEW = "engineering/code_review"
    ARCHITECTURE_REVIEW = "engineering/architecture_review"
    SECURITY_REVIEW = "engineering/security_review"

    # Planning subcategories
    SPRINT_PLANNING = "planning/sprint_planning"
    ROADMAP = "planning/roadmap"
    MILESTONES = "planning/milestones"

    # Editing subcategories
    GENERATE_PATCH = "editing/generate_patch"
    VALIDATE_PATCH = "editing/validate_patch"

    # Knowledge subcategories
    STORE_KNOWLEDGE = "knowledge/store"
    RETRIEVE_KNOWLEDGE = "knowledge/retrieve"
    SEARCH_KNOWLEDGE = "knowledge/search"

    # Workflow subcategories
    EXECUTE_WORKFLOW = "workflow/execute"
    QUEUE_WORKFLOW = "workflow/queue"
    RESUME_WORKFLOW = "workflow/resume"

    # Memory subcategories
    STORE_MEMORY = "memory/store"
    RECALL_MEMORY = "memory/recall"
    UPDATE_MEMORY = "memory/update"

    # System subcategories
    DIAGNOSTICS = "system/diagnostics"
    STATUS = "system/status"

    # Future subcategories
    VOICE = "future/voice"
    VISION = "future/vision"
    DESKTOP = "future/desktop"
    BROWSER = "future/browser"

    @classmethod
    def get_all_categories(cls) -> List[str]:
        """Get all defined capability categories."""
        return [
            cls.ENGINEERING,
            cls.PLANNING,
            cls.EDITING,
            cls.KNOWLEDGE,
            cls.WORKFLOW,
            cls.MEMORY,
            cls.SYSTEM,
            cls.FUTURE,
        ]

    @classmethod
    def get_subcategories(cls, category: str) -> List[str]:
        """Get all subcategories for a given category."""
        mapping = {
            cls.ENGINEERING: [cls.CODE_REVIEW, cls.ARCHITECTURE_REVIEW, cls.SECURITY_REVIEW],
            cls.PLANNING: [cls.SPRINT_PLANNING, cls.ROADMAP, cls.MILESTONES],
            cls.EDITING: [cls.GENERATE_PATCH, cls.VALIDATE_PATCH],
            cls.KNOWLEDGE: [cls.STORE_KNOWLEDGE, cls.RETRIEVE_KNOWLEDGE, cls.SEARCH_KNOWLEDGE],
            cls.WORKFLOW: [cls.EXECUTE_WORKFLOW, cls.QUEUE_WORKFLOW, cls.RESUME_WORKFLOW],
            cls.MEMORY: [cls.STORE_MEMORY, cls.RECALL_MEMORY, cls.UPDATE_MEMORY],
            cls.SYSTEM: [cls.DIAGNOSTICS, cls.STATUS],
            cls.FUTURE: [cls.VOICE, cls.VISION, cls.DESKTOP, cls.BROWSER],
        }
        return mapping.get(category, [])

    @classmethod
    def is_valid_category(cls, category: str) -> bool:
        """Check if a category is valid (either top-level or subcategory)."""
        all_cats = cls.get_all_categories()
        for cat in all_cats:
            if cat == category:
                return True
            if category.startswith(cat + "/"):
                return True
        return False

    @classmethod
    def get_parent_category(cls, subcategory: str) -> str:
        """Get the parent category for a subcategory."""
        if "/" in subcategory:
            return subcategory.split("/")[0]
        return subcategory


class CapabilityTaxonomy:
    """Taxonomy manager for capabilities."""

    def __init__(self):
        self._categories: dict[str, List[str]] = {}
        self._initialize_default_taxonomy()

    def _initialize_default_taxonomy(self) -> None:
        """Initialize with default category structure."""
        self._categories = {
            CapabilityCategory.ENGINEERING: [
                CapabilityCategory.CODE_REVIEW,
                CapabilityCategory.ARCHITECTURE_REVIEW,
                CapabilityCategory.SECURITY_REVIEW,
            ],
            CapabilityCategory.PLANNING: [
                CapabilityCategory.SPRINT_PLANNING,
                CapabilityCategory.ROADMAP,
                CapabilityCategory.MILESTONES,
            ],
            CapabilityCategory.EDITING: [
                CapabilityCategory.GENERATE_PATCH,
                CapabilityCategory.VALIDATE_PATCH,
            ],
            CapabilityCategory.KNOWLEDGE: [
                CapabilityCategory.STORE_KNOWLEDGE,
                CapabilityCategory.RETRIEVE_KNOWLEDGE,
                CapabilityCategory.SEARCH_KNOWLEDGE,
            ],
            CapabilityCategory.WORKFLOW: [
                CapabilityCategory.EXECUTE_WORKFLOW,
                CapabilityCategory.QUEUE_WORKFLOW,
                CapabilityCategory.RESUME_WORKFLOW,
            ],
            CapabilityCategory.MEMORY: [
                CapabilityCategory.STORE_MEMORY,
                CapabilityCategory.RECALL_MEMORY,
                CapabilityCategory.UPDATE_MEMORY,
            ],
            CapabilityCategory.SYSTEM: [
                CapabilityCategory.DIAGNOSTICS,
                CapabilityCategory.STATUS,
            ],
            CapabilityCategory.FUTURE: [
                CapabilityCategory.VOICE,
                CapabilityCategory.VISION,
                CapabilityCategory.DESKTOP,
                CapabilityCategory.BROWSER,
            ],
        }

    def get_subcategories(self, category: str) -> List[str]:
        """Get subcategories for a given category."""
        return list(self._categories.get(category, []))

    def is_valid(self, category: str) -> bool:
        """Check if category is valid."""
        if category in self._categories:
            return True
        for subcats in self._categories.values():
            if category in subcats:
                return True
        return False

    def get_all_categories(self) -> List[str]:
        """Get all top-level categories."""
        return list(self._categories.keys())

    def get_all_subcategories(self) -> List[str]:
        """Get all subcategories across all categories."""
        result = []
        for subcats in self._categories.values():
            result.extend(subcats)
        return result

    def to_dict(self) -> dict:
        """Convert taxonomy to dictionary."""
        return {k: list(v) if isinstance(v, list) else v for k, v in self._categories.items()}