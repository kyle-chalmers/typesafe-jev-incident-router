"""Reproduce the live Jev boundary check for the data-team use-case guide."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from dotenv import load_dotenv
from typesafe_sdk import Noul, RetryPolicy, TypeSafeClient


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "docs" / "data-team-use-cases.md"
QUESTION_ID = "bounded_jev_role"
QUESTION = (
    "Is Jev limited to a bounded semantic judgment in this proposed use case, "
    "with exact computation and consequential actions kept outside Jev?"
)
CRITERIA = {
    "true": (
        "Jev evaluates messy or unstructured evidence using bounded typed answers, "
        "while code or people own exact facts, calculations, policy, and "
        "consequential actions."
    ),
    "false": (
        "Jev is asked to perform exact computation, create open-ended output, or "
        "directly authorize a consequential action."
    ),
}
DISCIPLINES = (
    "Data engineering",
    "Analytics engineering",
    "Data analytics",
    "Data science",
)


@dataclass(frozen=True)
class UseCase:
    discipline: str
    title: str
    ask_jev: str
    keep_outside_jev: str
    published_decision: str


def parse_use_cases(markdown: str) -> list[UseCase]:
    cases: list[UseCase] = []
    for discipline in DISCIPLINES:
        match = re.search(
            rf"^## {re.escape(discipline)}\n(.*?)(?=^## |\Z)",
            markdown,
            re.MULTILINE | re.DOTALL,
        )
        if match is None:
            raise ValueError(f"missing guide section: {discipline}")
        for line in match.group(1).splitlines():
            if not line.startswith("| **"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) != 4:
                raise ValueError(f"expected four table columns: {line}")
            published_decision = cells[3].lower()
            if published_decision not in {"yes", "no"}:
                raise ValueError(f"expected Yes or No Jev decision: {line}")
            cases.append(
                UseCase(
                    discipline=discipline,
                    title=cells[0].replace("**", ""),
                    ask_jev=cells[1],
                    keep_outside_jev=cells[2],
                    published_decision=published_decision,
                )
            )
    return cases


def build_state(use_case: UseCase) -> str:
    return "\n".join(
        (
            f"Discipline: {use_case.discipline}",
            f"Use case: {use_case.title}",
            f"Proposed Jev judgment: {use_case.ask_jev}",
            f"External controls: {use_case.keep_outside_jev}",
        )
    )


def assess_use_cases(
    use_cases: list[UseCase],
    *,
    model: str,
    client_factory: Callable[..., Any] = TypeSafeClient,
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    resolved_models: set[str] = set()
    with client_factory(
        model=model,
        retry=RetryPolicy(max_retries=2),
        timeout=30.0,
    ) as client:
        for use_case in use_cases:
            try:
                response = client.system_one(
                    state=build_state(use_case),
                    questions={
                        QUESTION_ID: Noul(
                            instructions=QUESTION,
                            criteria=CRITERIA,
                        )
                    },
                )
            except Exception as exc:
                results.append(
                    {
                        **asdict(use_case),
                        "error": type(exc).__name__,
                    }
                )
                continue
            resolved_models.add(response.model)
            probability = response.nouls[QUESTION_ID].noul
            decision = "yes" if probability >= 0.5 else "no"
            results.append(
                {
                    **asdict(use_case),
                    "model": response.model,
                    "decision": decision,
                    "yes_probability": probability,
                    "matches_published": decision == use_case.published_decision,
                }
            )
    return {
        "requested_model": model,
        "resolved_models": sorted(resolved_models),
        "question_id": QUESTION_ID,
        "question": QUESTION,
        "criteria": CRITERIA,
        "results": results,
    }


def assessment_matches_published(assessment: dict[str, Any]) -> bool:
    return all(
        result.get("matches_published") is True
        for result in assessment["results"]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Jev's boundary check for every data-team use case."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Markdown guide to assess.",
    )
    parser.add_argument("--model", default="jev-latest")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_dotenv(dotenv_path=ROOT / ".env")
    use_cases = parse_use_cases(args.source.read_text())
    assessment = assess_use_cases(use_cases, model=args.model)
    print(json.dumps(assessment, indent=2))
    if not assessment_matches_published(assessment):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
