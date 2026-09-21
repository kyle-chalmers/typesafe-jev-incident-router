from scripts.evaluate_calibration import evaluate_cases


def test_calibration_metrics_include_explicit_denominators():
    cases = [
        {
            "action": "assign",
            "suggested_responder": "data_platform",
            "correct_responder": "data_platform",
            "minutes_to_correct_responder": 0,
        },
        {
            "action": "assign",
            "suggested_responder": "business_intelligence",
            "correct_responder": "analytics_engineering",
            "minutes_to_correct_responder": 45,
        },
        {
            "action": "review",
            "suggested_responder": "data_platform",
            "correct_responder": "business_intelligence",
            "minutes_to_correct_responder": 12,
        },
        {
            "action": "review",
            "suggested_responder": "other_or_unknown",
            "correct_responder": "source_application",
            "minutes_to_correct_responder": 18,
        },
    ]

    result = evaluate_cases(cases)

    assert result["misroute_rate"] == {
        "value": 0.5,
        "numerator": 1,
        "denominator": 2,
    }
    assert result["review_rate"] == {
        "value": 0.5,
        "numerator": 2,
        "denominator": 4,
    }
    assert result["mean_minutes_to_correct_responder"] == {
        "value": 18.75,
        "total_minutes": 75.0,
        "denominator": 4,
    }
