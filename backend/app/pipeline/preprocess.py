"""Step 1: split input text into individual, cleaned requirements."""

import re

# Leading bullet marker: "- ", "* ", "• "
BULLET_PATTERN = re.compile(r"^[-*•]\s+")
# Leading numbering: "1. ", "1) "
NUMBER_PATTERN = re.compile(r"^\d+[.)]\s+")
# Leading requirement label: "REQ-001:", "FR-3 -"
LABEL_PATTERN = re.compile(r"^[A-Za-z]+-\d+\s*[:\-–]\s*")


def clean_line(line: str) -> str:
    """Remove bullet, numbering or label prefix and trim whitespace."""
    line = line.strip()
    for pattern in (BULLET_PATTERN, NUMBER_PATTERN, LABEL_PATTERN):
        line = pattern.sub("", line, count=1)
    return line.strip()


def split_requirements(text: str) -> list[str]:
    """Split raw input into one cleaned requirement per non-empty line."""
    lines = (clean_line(line) for line in text.splitlines())
    return [line for line in lines if line]


def assign_ids(requirements: list[str]) -> list[tuple[str, str]]:
    """Return (id, text) pairs with ids R001, R002, and so on."""
    return [(f"R{i:03d}", text) for i, text in enumerate(requirements, start=1)]
