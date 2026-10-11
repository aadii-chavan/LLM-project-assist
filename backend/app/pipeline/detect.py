"""Step 2: detect whether a requirement is ambiguous (LLM call #1)."""

from app.schemas import DetectionResult


def detect_ambiguity(requirement: str) -> DetectionResult:
    """Return the ambiguity detection result for one requirement."""
    raise NotImplementedError
