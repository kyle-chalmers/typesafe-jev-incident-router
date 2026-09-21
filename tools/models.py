"""Application-owned data structures for incident routing."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class Incident:
    reference: str
    title: str
    description: str
    affected_asset: str
    business_context: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "Incident":
        required = ("id", "title", "description", "affected_asset", "business_context")
        missing = [name for name in required if not str(value.get(name, "")).strip()]
        if missing:
            raise ValueError(f"incident is missing required fields: {', '.join(missing)}")
        return cls(
            reference=str(value["id"]),
            title=str(value["title"]),
            description=str(value["description"]),
            affected_asset=str(value["affected_asset"]),
            business_context=str(value["business_context"]),
        )

@dataclass(frozen=True, slots=True)
class ChoiceJudgment:
    choice: str
    confidence: float
    probabilities: dict[str, float]


@dataclass(frozen=True, slots=True)
class ScoreJudgment:
    score: float
    confidence: float
    probabilities: dict[int, float]


@dataclass(frozen=True, slots=True)
class NoulJudgment:
    probability: float


@dataclass(frozen=True, slots=True)
class JudgmentBundle:
    model_version: str
    impact: ScoreJudgment
    critical_work: NoulJudgment
    owner: ChoiceJudgment | None = None


@dataclass(frozen=True, slots=True)
class RoutingDecision:
    incident_reference: str
    action: str
    queue: str
    priority: str
    suggested_responder: str | None
    reasons: tuple[str, ...]
    model_version: str | None
    choice_probabilities: dict[str, float] = field(default_factory=dict)
    risk_flags: tuple[str, ...] = ()
    source: str = "policy"

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["reasons"] = list(self.reasons)
        value["risk_flags"] = list(self.risk_flags)
        return value
