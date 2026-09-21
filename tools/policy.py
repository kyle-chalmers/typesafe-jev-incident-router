"""Deterministic policy over registry facts and typed model judgments."""

from __future__ import annotations

from tools.models import Incident, JudgmentBundle, RoutingDecision
from tools.questions import (
    CRITICAL_WORK_REVIEW,
    HIGH_IMPACT_SCORE,
    IMPACT_CONFIDENCE_FLOOR,
    OWNER_CONFIDENCE_FLOOR,
)

REVIEW_QUEUE = "data_incident_review"


def decide(
    incident: Incident,
    *,
    registry_responder: str | None,
    judgments: JudgmentBundle,
) -> RoutingDecision:
    reasons: list[str] = []
    risk_flags: list[str] = []
    owner = judgments.owner
    suggested = registry_responder or (owner.choice if owner else None)
    priority = "high" if judgments.impact.score >= HIGH_IMPACT_SCORE else "normal"

    if judgments.impact.confidence < IMPACT_CONFIDENCE_FLOOR:
        reasons.append("impact_confidence_below_floor")

    if judgments.critical_work.probability >= CRITICAL_WORK_REVIEW:
        reasons.append("critical_work_requires_review")
        risk_flags.append("critical_work_reported")
        priority = "high"

    if registry_responder is None:
        if owner is None:
            reasons.append("owner_judgment_missing")
        else:
            if owner.choice == "other_or_unknown":
                reasons.append("owner_outside_known_teams")
            if owner.confidence < OWNER_CONFIDENCE_FLOOR:
                reasons.append("owner_confidence_below_floor")

    if reasons:
        action = "review"
        queue = REVIEW_QUEUE
    else:
        action = "assign"
        queue = suggested or REVIEW_QUEUE
        reasons.append("registry_match" if registry_responder else "semantic_route_approved")

    return RoutingDecision(
        incident_reference=incident.reference,
        action=action,
        queue=queue,
        priority=priority,
        suggested_responder=suggested,
        reasons=tuple(reasons),
        model_version=judgments.model_version,
        choice_probabilities=dict(owner.probabilities) if owner else {},
        risk_flags=tuple(risk_flags),
        source="registry" if registry_responder else "jev",
    )

