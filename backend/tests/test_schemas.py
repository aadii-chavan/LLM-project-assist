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


def test_ambiguous_requires_types() -> None:
    """ambiguous=true with empty types is rejected."""
    with pytest.raises(ValidationError):
        DetectionResult(
            ambiguous=True, types=[], spans=["fast"], explanation="x", confidence=0.5
        )


@pytest.mark.parametrize(
    "types, spans", [(["vagueness"], []), ([], ["fast"])]
)
def test_clear_requires_empty_types_and_spans(types: list[str], spans: list[str]) -> None:
    """ambiguous=false with any types or spans is rejected."""
    with pytest.raises(ValidationError):
        DetectionResult(
            ambiguous=False, types=types, spans=spans, explanation="x", confidence=0.5
        )


def test_clear_result_with_empty_lists_is_valid() -> None:
    """ambiguous=false with empty types and spans is accepted."""
    result = DetectionResult(
        ambiguous=False, types=[], spans=[], explanation="Clear.", confidence=0.9
    )
    assert result.ambiguous is False


@pytest.mark.parametrize("count", [0, 4])
def test_clarifying_questions_count_is_validated(count: int) -> None:
    """clarifying_questions must have 1 to 3 items."""
    with pytest.raises(ValidationError):
        CorrectionResult(
            rewritten_text="The system shall respond within 2 seconds.",
            clarifying_questions=["Question?"] * count,
            assumptions=[],
        )
