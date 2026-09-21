import json

from tools.models import (
    ChoiceJudgment,
    Incident,
    JudgmentBundle,
    NoulJudgment,
    ScoreJudgment,
)
from tools.policy import decide
from tools.registry import load_registry, lookup_responder


def incident(asset: str = "unknown_asset") -> Incident:
    return Incident(
        reference="inc_001",
        title="Warehouse load failed",
        description="The finance load stopped after a permissions error.",
        affected_asset=asset,
        business_context="The morning close report is delayed.",
    )


def judgments(
    *,
    owner: str = "data_platform",
    owner_confidence: float = 0.91,
    impact_score: float = 1.2,
    impact_confidence: float = 0.82,
    critical_work: float = 0.2,
) -> JudgmentBundle:
    return JudgmentBundle(
        model_version="jev-1.13.0",
        owner=ChoiceJudgment(
            choice=owner,
            confidence=owner_confidence,
            probabilities={
                "analytics_engineering": 0.03,
                "data_platform": 0.91,
                "business_intelligence": 0.02,
                "source_application": 0.02,
                "other_or_unknown": 0.02,
            },
        ),
        impact=ScoreJudgment(
            score=impact_score,
            confidence=impact_confidence,
            probabilities={0: 0.05, 1: 0.70, 2: 0.20, 3: 0.05},
        ),
        critical_work=NoulJudgment(probability=critical_work),
    )


def test_registry_loads_exact_response_team(tmp_path):
    path = tmp_path / "registry.json"
    path.write_text(json.dumps({"finance_daily": "analytics_engineering"}))

    registry = load_registry(path)

    assert lookup_responder("finance_daily", registry) == "analytics_engineering"
    assert lookup_responder("missing", registry) is None


def test_exact_registry_responder_overrides_semantic_owner():
    decision = decide(
        incident("finance_daily"),
        registry_responder="analytics_engineering",
        judgments=judgments(owner="data_platform"),
    )

    assert decision.action == "assign"
    assert decision.queue == "analytics_engineering"
    assert decision.suggested_responder == "analytics_engineering"
    assert decision.source == "registry"


def test_confident_semantic_route_assigns_selected_team():
    decision = decide(incident(), registry_responder=None, judgments=judgments())

    assert decision.action == "assign"
    assert decision.queue == "data_platform"
    assert decision.choice_probabilities["data_platform"] == 0.91
    assert decision.model_version == "jev-1.13.0"


def test_low_owner_confidence_preserves_suggestion_for_review():
    decision = decide(
        incident(),
        registry_responder=None,
        judgments=judgments(owner_confidence=0.39),
    )

    assert decision.action == "review"
    assert decision.queue == "data_incident_review"
    assert decision.suggested_responder == "data_platform"
    assert "owner_confidence_below_floor" in decision.reasons


def test_unknown_owner_always_enters_review():
    decision = decide(
        incident(),
        registry_responder=None,
        judgments=judgments(owner="other_or_unknown"),
    )

    assert decision.action == "review"
    assert "owner_outside_known_teams" in decision.reasons


def test_weak_impact_confidence_enters_review():
    decision = decide(
        incident(),
        registry_responder=None,
        judgments=judgments(impact_confidence=0.55),
    )

    assert decision.action == "review"
    assert "impact_confidence_below_floor" in decision.reasons


def test_critical_work_probability_forces_high_priority_review():
    decision = decide(
        incident(),
        registry_responder=None,
        judgments=judgments(critical_work=0.94),
    )

    assert decision.action == "review"
    assert decision.priority == "high"
    assert "critical_work_reported" in decision.risk_flags


def test_score_sets_priority_when_route_is_automatic():
    decision = decide(
        incident(),
        registry_responder=None,
        judgments=judgments(impact_score=2.44),
    )

    assert decision.action == "assign"
    assert decision.priority == "high"


def test_decision_serializes_tuples_as_json_arrays():
    decision = decide(incident(), registry_responder=None, judgments=judgments())

    value = decision.to_dict()

    assert value["reasons"] == ["semantic_route_approved"]
    assert value["risk_flags"] == []
