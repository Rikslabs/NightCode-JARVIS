"""Constants for JARVIS core domain."""

# Default values
DEFAULT_CONFIDENCE: float = 1.0
DEFAULT_TIMEOUT: float = 30.0
DEFAULT_MAX_RETRIES: int = 3

# Risk thresholds
RISK_FACTORS = [
    ("low_threshold", 0.7),
    ("medium_threshold", 0.3),
    ("high_threshold", 0.5),
]

# Tool categories
TOOL_CATEGORIES = [
    "planning",
    "review",
    "knowledge",
    "editing",
    "coding",
    "memory",
    "system",
]