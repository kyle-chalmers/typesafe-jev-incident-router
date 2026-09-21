"""TypeSafe questions and illustrative application policy constants."""

from typesafe_sdk import Choice, Noul, Score

OWNER_CONFIDENCE_FLOOR = 0.75
IMPACT_CONFIDENCE_FLOOR = 0.70
CRITICAL_WORK_REVIEW = 0.70
HIGH_IMPACT_SCORE = 2.0

OWNER_CRITERIA = {
    "analytics_engineering": (
        "Transformation logic, data models, orchestration, or warehouse jobs"
    ),
    "data_platform": (
        "Shared ingestion, storage, compute, permissions, or platform reliability"
    ),
    "business_intelligence": (
        "Dashboard logic, semantic models, reporting, or visualization behavior"
    ),
    "source_application": "The upstream operational system or source data it produces",
    "other_or_unknown": (
        "The evidence does not identify one listed team or spans several teams"
    ),
}

IMPACT_CRITERIA = [
    "Informational issue with no current user or business impact",
    "Degraded or delayed work with a practical workaround",
    "A named business workflow or reporting deadline is blocked",
    "Critical customer, financial, regulatory, or executive reporting impact",
]


def build_questions(*, include_owner: bool) -> dict[str, Choice | Score | Noul]:
    questions: dict[str, Choice | Score | Noul] = {
        "business_impact": Score(
            instructions="How severe is the operational impact stated in the incident?",
            criteria=IMPACT_CRITERIA,
        ),
        "report_states_critical_work_blocked": Noul(
            instructions=(
                "Does the incident report state that a named critical business process "
                "or reporting deadline is blocked?"
            ),
            criteria={
                "true": "A specific process, decision, or deadline cannot proceed",
                "false": (
                    "Work continues, impact is unspecified, or only inconvenience is described"
                ),
            },
        ),
    }
    if include_owner:
        questions["response_team"] = Choice(
            instructions="Which response team best matches the failure described?",
            criteria=OWNER_CRITERIA,
        )
    return questions
