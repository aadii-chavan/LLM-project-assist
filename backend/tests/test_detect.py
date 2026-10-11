"""Tests for the detector, using a mocked Anthropic client (no real API calls)."""

import json
from types import SimpleNamespace
from typing import Any

import pytest

from app.config import Settings
from app.pipeline import detect
from app.pipeline.detect import DetectionError, detect_ambiguity

REQUIREMENT = "The system shall be fast."

VALID = {
    "ambiguous": True,
    "types": ["vagueness"],
    "spans": ["fast"],
    "explanation": "'fast' is not measurable.",
    "confidence": 0.9,
}


def fake_response(tool_input: dict[str, Any]) -> SimpleNamespace:
    """Build an object that looks like an Anthropic response with one tool call."""
    block = SimpleNamespace(type="tool_use", input=tool_input)
    return SimpleNamespace(
        content=[block],
        model_dump=lambda mode="json": {"content": [{"type": "tool_use", "input": tool_input}]},
    )


class FakeClient:
    """Stands in for anthropic.Anthropic and returns queued responses."""

    def __init__(self, responses: list[SimpleNamespace]) -> None:
        self.responses = responses
        self.calls = 0
        self.messages = SimpleNamespace(create=self.create)

    def create(self, **kwargs: Any) -> SimpleNamespace:
        """Return the next queued response."""
        self.calls += 1
        return self.responses.pop(0)


@pytest.fixture
def log_path(tmp_path, monkeypatch):
    """Send log output to a temp file and provide fake settings."""
    path = tmp_path / "logs" / "llm_calls.jsonl"
    monkeypatch.setattr(detect, "LOG_PATH", path)
    settings = Settings(ANTHROPIC_API_KEY="test-key", MODEL_NAME="test-model", _env_file=None)
    monkeypatch.setattr(detect, "get_settings", lambda: settings)
    return path


def use_client(monkeypatch, responses: list[SimpleNamespace]) -> FakeClient:
    """Make detect.anthropic.Anthropic return a FakeClient."""
    client = FakeClient(responses)
    monkeypatch.setattr(detect.anthropic, "Anthropic", lambda api_key: client)
    return client


def test_valid_response(log_path, monkeypatch) -> None:
    """A valid response is parsed and logged once."""
    client = use_client(monkeypatch, [fake_response(VALID)])
    result = detect_ambiguity(REQUIREMENT)

    assert result.ambiguous is True
    assert result.spans == ["fast"]
    assert client.calls == 1

    lines = log_path.read_text().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["stage"] == "detect"
    assert record["model"] == "test-model"
    assert record["attempt"] == 1
    assert REQUIREMENT in record["prompt"]


def test_invalid_response_is_retried_once(log_path, monkeypatch) -> None:
    """An invalid first response triggers one retry, which can succeed."""
    bad = {**VALID, "confidence": 5}
    client = use_client(monkeypatch, [fake_response(bad), fake_response(VALID)])

    result = detect_ambiguity(REQUIREMENT)

    assert result.confidence == 0.9
    assert client.calls == 2
    assert len(log_path.read_text().splitlines()) == 2


def test_span_not_in_text_is_retried(log_path, monkeypatch) -> None:
    """A span that is not in the requirement triggers a retry."""
    bad = {**VALID, "spans": ["quick"]}
    client = use_client(monkeypatch, [fake_response(bad), fake_response(VALID)])

    result = detect_ambiguity(REQUIREMENT)

    assert result.spans == ["fast"]
    assert client.calls == 2


def test_span_check_is_case_insensitive(log_path, monkeypatch) -> None:
    """Span matching ignores case."""
    upper = {**VALID, "spans": ["FAST"]}
    client = use_client(monkeypatch, [fake_response(upper)])

    assert detect_ambiguity(REQUIREMENT).spans == ["FAST"]
    assert client.calls == 1


def test_fails_after_one_retry(log_path, monkeypatch) -> None:
    """Two bad responses in a row raise a clear error."""
    bad = {**VALID, "spans": ["quick"]}
    client = use_client(monkeypatch, [fake_response(bad), fake_response(bad)])

    with pytest.raises(DetectionError, match="failed after 2 attempts"):
        detect_ambiguity(REQUIREMENT)
    assert client.calls == 2


def test_missing_api_key_gives_clear_error(monkeypatch) -> None:
    """Missing settings raise a readable error before any API call."""
    settings = Settings(ANTHROPIC_API_KEY=None, MODEL_NAME=None, _env_file=None)
    monkeypatch.setattr(detect, "get_settings", lambda: settings)

    with pytest.raises(DetectionError, match="ANTHROPIC_API_KEY and MODEL_NAME"):
        detect_ambiguity(REQUIREMENT)
