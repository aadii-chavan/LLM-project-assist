"""Step 3: rewrite an ambiguous requirement (LLM call #2)."""

from app.schemas import CorrectionResult, DetectionResult


def correct_requirement(requirement: str, detection: DetectionResult) -> CorrectionResult:
    """Return a rewritten requirement plus clarifying questions."""
    raise NotImplementedError
