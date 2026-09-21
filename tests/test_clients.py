import json

import pytest
from typesafe_sdk import (
    ChoiceAnswer,
    NoulAnswer,
    ScoreAnswer,
    SystemOneResponse,
    Usage,
)

from tools.clients import FixtureClient, ServiceUnavailable, TypeSafeAdapter
from tools.models import Incident


def incident() -> Incident:
    return Incident(
        reference="inc_001",
        title="Warehouse permission failure",
        description="The ingestion job stopped after a permission error.",
        affected_asset="unknown_asset",
        business_context="The operations review is waiting for refreshed data.",
    )


def sdk_response() -> SystemOneResponse:
    return SystemOneResponse(
        model="jev-1.13.0",
        usage=Usage(input_tokens=30, output_tokens=12),
        answers={
            "response_team": ChoiceAnswer(
                choice="data_platform",
                confidence=0.39,
                probabilities={
                    "analytics_engineering": 0.18,
                    "data_platform": 0.34,
                    "business_intelligence": 0.14,
                    "source_application": 0.13,
                    "other_or_unknown": 0.21,
                },
            ),
            "business_impact": ScoreAnswer(
                score=2.2,
                confidence=0.74,
                legend={0: "None", 1: "Degraded", 2: "Blocked", 3: "Critical"},
                probabilities={0: 0.02, 1: 0.18, 2: 0.55, 3: 0.25},
            ),
            "report_states_critical_work_blocked": NoulAnswer(noul=0.82),
        },
    )


class FakeSdkClient:
    def __init__(self, response):
        self.response = response
        self.state = None
        self.questions = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def system_one(self, *, state, questions):
        self.state = state
        self.questions = questions
        return self.response


def test_live_adapter_converts_sdk_answers_and_sends_scoped_state():
    sdk_client = FakeSdkClient(sdk_response())
    captured = {}

    def factory(**kwargs):
        captured.update(kwargs)
        return sdk_client

    result = TypeSafeAdapter(client_factory=factory).evaluate(
        incident(), include_owner=True
    )

    assert result.model_version == "jev-1.13.0"
    assert result.owner.choice == "data_platform"
    assert result.owner.confidence == 0.39
    assert result.impact.score == 2.2
    assert result.critical_work.probability == 0.82
    assert sdk_client.state["incident"]["id"] == "inc_001"
    assert set(sdk_client.questions) == {
        "response_team",
        "business_impact",
        "report_states_critical_work_blocked",
    }
    assert captured["model"] == "jev-latest"
    assert captured["retry"].max_retries == 2


def test_live_adapter_omits_owner_question_when_registry_is_authoritative():
    response = sdk_response()
    response.answers.pop("response_team")
    sdk_client = FakeSdkClient(response)

    result = TypeSafeAdapter(client_factory=lambda **_kwargs: sdk_client).evaluate(
        incident(), include_owner=False
    )

    assert result.owner is None
    assert "response_team" not in sdk_client.questions


def test_live_adapter_converts_transport_failures_to_service_unavailable():
    def factory(**_kwargs):
        raise TimeoutError("network timeout")

    with pytest.raises(ServiceUnavailable, match="TypeSafe evaluation failed"):
        TypeSafeAdapter(client_factory=factory).evaluate(incident(), include_owner=True)


def test_fixture_client_loads_named_response(tmp_path):
    path = tmp_path / "fixtures.json"
    path.write_text(
        json.dumps(
            {
                "low_confidence": {
                    "model": "fixture-jev-1.13.0",
                    "owner": {
                        "choice": "data_platform",
                        "confidence": 0.39,
                        "probabilities": {"data_platform": 0.4, "other_or_unknown": 0.6},
                    },
                    "impact": {
                        "score": 1.4,
                        "confidence": 0.8,
                        "probabilities": {"0": 0.1, "1": 0.5, "2": 0.3, "3": 0.1},
                    },
                    "critical_work": 0.2,
                }
            }
        )
    )

    result = FixtureClient(path, "low_confidence").evaluate(
        incident(), include_owner=True
    )

    assert result.model_version == "fixture-jev-1.13.0"
    assert result.owner.confidence == 0.39
    assert result.impact.probabilities[2] == 0.3


def test_fixture_client_can_inject_service_failure(tmp_path):
    path = tmp_path / "fixtures.json"
    path.write_text(json.dumps({"api_error": {"error": "timeout"}}))

    with pytest.raises(ServiceUnavailable, match="fixture service failure"):
        FixtureClient(path, "api_error").evaluate(incident(), include_owner=True)
