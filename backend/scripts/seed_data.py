from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_returns.json"


def seed() -> None:
    sample = json.loads(DATA_PATH.read_text())
    print(f"Seeded {len(sample)} sample return requests.")


if __name__ == "__main__":
    seed()
