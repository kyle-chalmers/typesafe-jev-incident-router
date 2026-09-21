"""Live and fixture clients for TypeSafe judgments."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from typesafe_sdk import RetryPolicy, TypeSafeClient

from tools.models import (
    ChoiceJudgment,
    Incident,
    JudgmentBundle,
    NoulJudgment,
    ScoreJudgment,
)
from tools.questions import build_questions


class ServiceUnavailable(RuntimeError):
    """The semantic evaluation did not return a usable answer."""


class TypeSafeAdapter:
    def __init__(
        self,
        *,
        client_factory: Callable[..., Any] = TypeSafeClient,
        model: str = "jev-latest",
        timeout_seconds: float = 10.0,
    ) -> None:
        self.client_factory = client_factory
        self.model = model
        self.timeout_seconds = timeout_seconds

    def evaluate(self, incident: Incident, *, include_owner: bool) -> JudgmentBundle:
        try:
            with self.client_factory(
                model=self.model,
                retry=RetryPolicy(max_retries=2),
                timeout=self.timeout_seconds,
            ) as client:
                response = client.system_one(
                    state=incident.to_state(),
                    questions=build_questions(include_owner=include_owner),
                )
        except Exception as exc:
            raise ServiceUnavailable(f"TypeSafe evaluation failed: {exc}") from exc

        owner = None
        if include_owner:
            answer = response.choices["response_team"]
            owner = ChoiceJudgment(
                choice=answer.choice,
                confidence=answer.confidence,
                probabilities=dict(answer.probabilities),
            )
        impact_answer = response.scores["business_impact"]
        critical_answer = response.nouls["report_states_critical_work_blocked"]
        return JudgmentBundle(
            model_version=response.model,
            owner=owner,
            impact=ScoreJudgment(
                score=impact_answer.score,
                confidence=impact_answer.confidence,
                probabilities=dict(impact_answer.probabilities),
            ),
            critical_work=NoulJudgment(probability=critical_answer.noul),
        )


class FixtureClient:
    def __init__(self, path: str | Path, fixture_name: str) -> None:
        self.path = Path(path)
        self.fixture_name = fixture_name

    def evaluate(self, _incident: Incident, *, include_owner: bool) -> JudgmentBundle:
        fixtures = json.loads(self.path.read_text())
        if self.fixture_name not in fixtures:
            raise ValueError(f"unknown fixture: {self.fixture_name}")
        value = fixtures[self.fixture_name]
        if value.get("error"):
            raise ServiceUnavailable(
                f"fixture service failure: {value['error']}"
            )

        owner = None
        if include_owner:
            owner_value = value["owner"]
            owner = ChoiceJudgment(
                choice=str(owner_value["choice"]),
                confidence=float(owner_value["confidence"]),
                probabilities={
                    str(key): float(probability)
                    for key, probability in owner_value["probabilities"].items()
                },
            )
        impact_value = value["impact"]
        return JudgmentBundle(
            model_version=str(value["model"]),
            owner=owner,
            impact=ScoreJudgment(
                score=float(impact_value["score"]),
                confidence=float(impact_value["confidence"]),
                probabilities={
                    int(key): float(probability)
                    for key, probability in impact_value["probabilities"].items()
                },
            ),
            critical_work=NoulJudgment(probability=float(value["critical_work"])),
        )
