"""Step 2: detect whether a requirement is ambiguous (LLM call #1)."""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import anthropic
from pydantic import ValidationError

from app.config import get_settings
from app.schemas import DetectionResult

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "detect_prompt.txt"
LOG_PATH = Path(__file__).resolve().parents[2] / "logs" / "llm_calls.jsonl"

TOOL_NAME = "report_detection"
MAX_ATTEMPTS = 2  # first try + one retry
MAX_TOKENS = 1024


class DetectionError(Exception):
    """Raised when detection cannot be completed (bad config or bad LLM output)."""


def build_prompt(requirement: str) -> str:
    """Load the prompt template and insert the requirement."""
    template = PROMPT_PATH.read_text(encoding="utf-8")
    return template.replace("{requirement}", requirement)


def log_call(record: dict[str, Any]) -> None:
    """Append one JSON line describing an LLM call to the log file."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")


def extract_tool_input(response: Any) -> dict[str, Any]:
    """Return the input of the tool call in the response."""
    for block in response.content:
        if block.type == "tool_use":
            return block.input
    raise ValueError("response contains no tool call")


def check_spans(detection: DetectionResult, requirement: str) -> None:
    """Raise ValueError if any span is not a substring of the requirement."""
    text = requirement.lower()
    for span in detection.spans:
        if span.lower() not in text:
            raise ValueError(f"span {span!r} is not in the requirement")


def detect_ambiguity(requirement: str) -> DetectionResult:
    """Return the ambiguity detection result for one requirement."""
    settings = get_settings()
    if not settings.ANTHROPIC_API_KEY or not settings.MODEL_NAME:
        raise DetectionError(
            "ANTHROPIC_API_KEY and MODEL_NAME must be set in backend/.env"
        )

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    prompt = build_prompt(requirement)
    tool = {
        "name": TOOL_NAME,
        "description": "Report whether the requirement is ambiguous.",
        "input_schema": DetectionResult.model_json_schema(),
    }

    last_error = ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        start = time.perf_counter()
        response = client.messages.create(
            model=settings.MODEL_NAME,
            max_tokens=MAX_TOKENS,
            temperature=0,
            tools=[tool],
            tool_choice={"type": "tool", "name": TOOL_NAME},
            messages=[{"role": "user", "content": prompt}],
        )
        latency = time.perf_counter() - start

        parsed, last_error = None, ""
        try:
            parsed = DetectionResult.model_validate(extract_tool_input(response))
            check_spans(parsed, requirement)
        except (ValidationError, ValueError) as error:
            last_error = str(error)

        log_call(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "stage": "detect",
                "model": settings.MODEL_NAME,
                "prompt": prompt,
                "raw_response": response.model_dump(mode="json"),
                "parsed_result": None if last_error else parsed.model_dump(mode="json"),
                "error": last_error or None,
                "latency_seconds": round(latency, 3),
                "attempt": attempt,
            }
        )
        if not last_error:
            return parsed

    raise DetectionError(
        f"Detection failed after {MAX_ATTEMPTS} attempts. Last error: {last_error}"
    )
