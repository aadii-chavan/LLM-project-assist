"""Tests for schema validation rules."""

import pytest
from pydantic import ValidationError

from app.schemas import CorrectionResult, DetectionResult


def make_detection(confidence: float) -> DetectionResult:
    """Build a DetectionResult with the given confidence."""
    return DetectionResult(
        ambiguous=True,
        types=["vagueness"],
        spans=["fast"],
        explanation="'fast' is not measurable.",
        confidence=confidence,
    )


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_confidence_outside_range_is_rejected(confidence: float) -> None:
    """Confidence must be between 0 and 1."""
    with pytest.raises(ValidationError):
        make_detection(confidence)


@pytest.mark.parametrize("count", [0, 4])
def test_clarifying_questions_count_is_validated(count: int) -> None:
    """clarifying_questions must have 1 to 3 items."""
    with pytest.raises(ValidationError):
        CorrectionResult(
            rewritten_text="The system shall respond within 2 seconds.",
            clarifying_questions=["Question?"] * count,
            assumptions=[],
        )
