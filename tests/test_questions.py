from typesafe_sdk import Choice, Noul, Score

from tools.models import Incident
from tools.questions import (
    CRITICAL_WORK_REVIEW,
    IMPACT_CONFIDENCE_FLOOR,
    OWNER_CONFIDENCE_FLOOR,
    build_questions,
)


def test_incident_requires_a_reference_and_affected_asset():
    incident = Incident.from_mapping(
        {
            "id": "inc_001",
            "title": "Warehouse load failed",
            "description": "The finance load stopped after a permissions error.",
            "affected_asset": "finance_daily",
            "business_context": "The morning close report is delayed.",
        }
    )

    assert incident.reference == "inc_001"
    assert incident.affected_asset == "finance_daily"


def test_owner_question_has_an_explicit_escape_route():
    questions = build_questions(include_owner=True)

    owner = questions["response_team"]
    assert isinstance(owner, Choice)
    assert "other_or_unknown" in owner.criteria
    assert len(owner.criteria) == 5


def test_known_owner_request_omits_semantic_ownership_question():
    questions = build_questions(include_owner=False)

    assert "response_team" not in questions
    assert set(questions) == {
        "business_impact",
        "report_states_critical_work_blocked",
    }


def test_score_and_noul_are_atomic_and_typed():
    questions = build_questions(include_owner=True)

    impact = questions["business_impact"]
    blocked = questions["report_states_critical_work_blocked"]
    assert isinstance(impact, Score)
    assert len(impact.criteria) == 4
    assert "and" not in str(impact.instructions).lower()
    assert isinstance(blocked, Noul)
    assert "report" in str(blocked.instructions).lower()


def test_policy_thresholds_are_named_illustrative_constants():
    assert OWNER_CONFIDENCE_FLOOR == 0.75
    assert IMPACT_CONFIDENCE_FLOOR == 0.70
    assert CRITICAL_WORK_REVIEW == 0.70
