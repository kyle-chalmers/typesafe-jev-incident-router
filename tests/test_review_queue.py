import json

from tools.models import RoutingDecision
from tools.review_queue import JsonlReviewQueue


def review_decision(reference: str = "inc_001") -> RoutingDecision:
    return RoutingDecision(
        incident_reference=reference,
        action="review",
        queue="data_incident_review",
        priority="high",
        suggested_responder="data_platform",
        reasons=("owner_confidence_below_floor",),
        model_version="jev-1.13.0",
        choice_probabilities={"data_platform": 0.34, "other_or_unknown": 0.21},
        risk_flags=(),
        source="jev",
    )


def test_review_queue_persists_decision_as_jsonl(tmp_path):
    path = tmp_path / "review.jsonl"

    added = JsonlReviewQueue(path).enqueue(review_decision())

    assert added is True
    value = json.loads(path.read_text().strip())
    assert value["incident_reference"] == "inc_001"
    assert value["reasons"] == ["owner_confidence_below_floor"]


def test_review_queue_is_idempotent_by_incident_reference(tmp_path):
    path = tmp_path / "review.jsonl"
    queue = JsonlReviewQueue(path)

    first = queue.enqueue(review_decision())
    second = queue.enqueue(review_decision())

    assert first is True
    assert second is False
    assert len(path.read_text().splitlines()) == 1
