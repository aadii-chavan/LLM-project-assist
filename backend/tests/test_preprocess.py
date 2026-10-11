"""Tests for the preprocessor."""

import pytest

from app.pipeline.preprocess import assign_ids, split_requirements


@pytest.mark.parametrize(
    "line",
    [
        "- The system shall log errors.",
        "* The system shall log errors.",
        "• The system shall log errors.",
        "1. The system shall log errors.",
        "2) The system shall log errors.",
        "REQ-001: The system shall log errors.",
        "FR-3 - The system shall log errors.",
        "  The system shall log errors.  ",
    ],
)
def test_prefixes_are_stripped(line: str) -> None:
    """Bullets, numbering, labels and extra whitespace are removed."""
    assert split_requirements(line) == ["The system shall log errors."]


def test_blank_lines_are_dropped() -> None:
    """Empty and whitespace-only lines produce no requirements."""
    assert split_requirements("A one.\n\n   \nB two.\n") == ["A one.", "B two."]


def test_line_is_not_split_into_sentences() -> None:
    """A requirement containing periods stays as one requirement."""
    text = "The system shall show v1.2 of the page. It shall be cached."
    assert split_requirements(text) == [text]


def test_assign_ids() -> None:
    """Ids start at R001 and increase by one."""
    assert assign_ids(["a", "b"]) == [("R001", "a"), ("R002", "b")]
    assert assign_ids([]) == []
