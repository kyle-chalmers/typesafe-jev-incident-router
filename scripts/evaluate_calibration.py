"""Summarize labeled routing outcomes with explicit denominators."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


def _rate(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 4) if denominator else None


def evaluate_cases(cases: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    rows = list(cases)
    for index, row in enumerate(rows, start=1):
        required = {
            "action",
            "suggested_responder",
            "correct_responder",
            "minutes_to_correct_responder",
        }
        missing = sorted(required.difference(row))
        if missing:
            raise ValueError(f"case {index} is missing: {', '.join(missing)}")
        if row["action"] not in {"assign", "review"}:
            raise ValueError(f"case {index} has an invalid action")
        if float(row["minutes_to_correct_responder"]) < 0:
            raise ValueError(f"case {index} has negative correction time")

    assignments = [row for row in rows if row["action"] == "assign"]
    reviews = [row for row in rows if row["action"] == "review"]
    misroutes = [
        row
        for row in assignments
        if row["suggested_responder"] != row["correct_responder"]
    ]
    total_minutes = sum(float(row["minutes_to_correct_responder"]) for row in rows)

    return {
        "total_cases": len(rows),
        "misroute_rate": {
            "value": _rate(len(misroutes), len(assignments)),
            "numerator": len(misroutes),
            "denominator": len(assignments),
        },
        "review_rate": {
            "value": _rate(len(reviews), len(rows)),
            "numerator": len(reviews),
            "denominator": len(rows),
        },
        "mean_minutes_to_correct_responder": {
            "value": round(total_minutes / len(rows), 2) if rows else None,
            "total_minutes": total_minutes,
            "denominator": len(rows),
        },
    }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate labeled incident-routing outcomes."
    )
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    print(json.dumps(evaluate_cases(load_jsonl(args.path)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
