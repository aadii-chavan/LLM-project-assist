"""Step 4: re-check the rewrite and retry correction if still ambiguous."""

from app.schemas import CorrectionResult, DetectionResult


def verify_and_correct(
    requirement: str, detection: DetectionResult, max_retries: int = 2
) -> tuple[CorrectionResult, int]:
    """Return the final correction and the number of attempts used."""
    raise NotImplementedError
