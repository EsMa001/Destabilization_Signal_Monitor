from __future__ import annotations

import argparse
from pathlib import Path

STRUCTURE = [
    "docs/project",
    "docs/requirements",
    "docs/method",
    "docs/architecture",
    "docs/traceability",
    "docs/testing",
    "docs/data",
    "docs/planning",
    "scripts",
    "config/countries",
    "data/bridge",
    "data/context",
    "proto/sources",
    "proto/features",
    "proto/scoring",
    "proto/reporting",
    "proto/runs",
    "proto/pipeline",
    "tests",
    "outputs/runs",
    "outputs/reference",
]

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=".", help="Target directory")
    args = parser.parse_args()

    root = Path(args.target).resolve()
    for rel in STRUCTURE:
        (root / rel).mkdir(parents=True, exist_ok=True)

    print(f"Scaffold directories created in {root}")

if __name__ == "__main__":
    main()
