from types import SimpleNamespace

from scripts.assess_use_case_boundaries import (
    DEFAULT_SOURCE,
    QUESTION_ID,
    assess_use_cases,
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
    assert result["results"][0]["yes_probability"] == 0.92
    assert result["results"][0]["matches_published"] is True
    assert "External controls:" in build_state(use_case)
