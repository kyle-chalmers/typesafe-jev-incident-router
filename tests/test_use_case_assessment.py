from types import SimpleNamespace

import pytest

import scripts.assess_use_case_boundaries as assessment_module
from scripts.assess_use_case_boundaries import (
    DEFAULT_SOURCE,
    QUESTION_ID,
    assess_use_cases,
    assessment_matches_published,
    build_state,
    parse_use_cases,
)


class FakeClient:
    def __init__(self, **_kwargs):
        self.states = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def system_one(self, *, state, questions):
        self.states.append(state)
        assert set(questions) == {QUESTION_ID}
        return SimpleNamespace(
            model="jev-test",
            nouls={QUESTION_ID: SimpleNamespace(noul=0.92)},
        )


class FailingClient(FakeClient):
    def system_one(self, *, state, questions):
        raise RuntimeError("synthetic failure")


def test_guide_contains_26_four_column_use_cases():
    use_cases = parse_use_cases(DEFAULT_SOURCE.read_text())

    assert len(use_cases) == 26
    assert {case.discipline for case in use_cases} == {
        "Data engineering",
        "Analytics engineering",
        "Data analytics",
        "Data science",
    }


def test_assessment_preserves_per_row_probability():
    use_case = parse_use_cases(DEFAULT_SOURCE.read_text())[0]

    result = assess_use_cases(
        [use_case],
        model="jev-test",
        client_factory=FakeClient,
    )

    assert result["resolved_models"] == ["jev-test"]
    assert result["results"][0]["decision"] == "yes"
    assert result["results"][0]["model"] == "jev-test"
    assert result["results"][0]["yes_probability"] == 0.92
    assert result["results"][0]["matches_published"] is True
    assert "External controls:" in build_state(use_case)


def test_assessment_gate_accepts_matching_results():
    assessment = {"results": [{"matches_published": True}]}

    assert assessment_matches_published(assessment) is True


def test_assessment_gate_rejects_mismatch():
    assessment = {"results": [{"matches_published": False}]}

    assert assessment_matches_published(assessment) is False


def test_assessment_gate_rejects_api_error():
    assessment = {"results": [{"error": "ServiceUnavailable"}]}

    assert assessment_matches_published(assessment) is False


def test_assessment_records_api_error_without_discarding_result():
    use_case = parse_use_cases(DEFAULT_SOURCE.read_text())[0]

    result = assess_use_cases(
        [use_case],
        model="jev-test",
        client_factory=FailingClient,
    )

    assert result["results"][0]["error"] == "RuntimeError"
    assert assessment_matches_published(result) is False


def test_main_exits_nonzero_on_failed_assessment(monkeypatch, capsys):
    monkeypatch.setattr(
        assessment_module,
        "parse_args",
        lambda: SimpleNamespace(source=DEFAULT_SOURCE, model="jev-test"),
    )
    monkeypatch.setattr(
        assessment_module,
        "assess_use_cases",
        lambda *_args, **_kwargs: {"results": [{"error": "RuntimeError"}]},
    )

    with pytest.raises(SystemExit) as error:
        assessment_module.main()

    assert error.value.code == 1
    assert '"error": "RuntimeError"' in capsys.readouterr().out
