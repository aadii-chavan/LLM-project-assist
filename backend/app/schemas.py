"""Pydantic models shared by the pipeline and the API."""

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class AmbiguityType(str, Enum):
    """The five kinds of ambiguity we detect."""

    lexical = "lexical"
    syntactic = "syntactic"
    semantic = "semantic"
    vagueness = "vagueness"
    incompleteness = "incompleteness"


class Method(str, Enum):
    """Which approach produced a result (used to compare methods)."""

    rule_based = "rule_based"
    zero_shot = "zero_shot"
    few_shot = "few_shot"
    few_shot_verifier = "few_shot_verifier"


class DetectionResult(BaseModel):
    """Output of the detection step."""

    ambiguous: bool
    types: list[AmbiguityType]
    spans: list[str]
    explanation: str
    confidence: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def check_consistency(self) -> "DetectionResult":
        """Ambiguous results need types; clear results must have no types or spans."""
        if self.ambiguous and not self.types:
            raise ValueError("types must not be empty when ambiguous is true")
        if not self.ambiguous and (self.types or self.spans):
            raise ValueError("types and spans must be empty when ambiguous is false")
        return self


class CorrectionResult(BaseModel):
    """Output of the correction step."""

    rewritten_text: str
    clarifying_questions: list[str] = Field(min_length=1, max_length=3)
    assumptions: list[str]


class AnalysisResult(BaseModel):
    """Before/after result for one requirement."""

    requirement_id: str
    original_text: str
    detection: DetectionResult
    correction: CorrectionResult | None = None
    attempts: int = 0
    method: Method


class AnalyzeRequest(BaseModel):
    """Request body for POST /analyze."""

    text: str = Field(min_length=1)
    method: Method = Method.few_shot_verifier


class BatchAnalyzeRequest(BaseModel):
    """Request body for POST /analyze/batch."""

    text: str = Field(min_length=1)
    project_name: str | None = None
    method: Method = Method.few_shot_verifier


class BatchAnalyzeResponse(BaseModel):
    """Response body for POST /analyze/batch."""

    run_id: str
    results: list[AnalysisResult]
