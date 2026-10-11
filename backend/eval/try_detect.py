"""Runs the detector on the sample requirements and prints a comparison table.

Run from the backend/ folder:  python eval/try_detect.py
"""

import json
import sys
from pathlib import Path

# Make "app" importable when running this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.pipeline.detect import detect_ambiguity  # noqa: E402

SAMPLE_PATH = Path(__file__).resolve().parent / "sample_requirements.json"


def main() -> None:
    """Detect each sample requirement and print the results."""
    samples = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    matches = 0

    for i, sample in enumerate(samples, start=1):
        result = detect_ambiguity(sample["text"])
        matched = result.ambiguous == sample["expected_ambiguous"]
        matches += matched
        print(f"[{i:02d}] {'OK ' if matched else 'MISS'} {sample['text']}")
        print(f"      expected: ambiguous={sample['expected_ambiguous']} {sample['expected_types']}")
        print(f"      got:      ambiguous={result.ambiguous} {[t.value for t in result.types]}")
        print(f"      spans:    {result.spans}")

    print(f"\nAmbiguous flag matched on {matches}/{len(samples)} requirements.")


if __name__ == "__main__":
    main()
