import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cli(tmp_path: Path, fixture: str, incident: str) -> tuple[dict, Path]:
    queue = tmp_path / "review_queue.jsonl"
    command = [
        sys.executable,
        "-m",
        "scripts.route_incident",
        "--incident",
        str(ROOT / "data" / "incidents" / incident),
        "--fixture",
        fixture,
        "--queue",
        str(queue),
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout), queue


def test_automatic_fixture_assigns_the_suggested_team(tmp_path):
    result, queue = run_cli(tmp_path, "automatic", "semantic_route.json")

    assert result["action"] == "assign"
    assert result["queue"] == "data_platform"
    assert result["execution_source"] == "fixture:automatic"
    assert queue.exists() is False


def test_low_confidence_fixture_enters_review_and_persists_once(tmp_path):
    first, queue = run_cli(tmp_path, "low_confidence", "ambiguous_owner.json")
    second, _queue = run_cli(tmp_path, "low_confidence", "ambiguous_owner.json")

    assert first["action"] == "review"
    assert first["suggested_responder"] == "data_platform"
    assert first["choice_probabilities"]["data_platform"] == 0.34
    assert first["queue_written"] is True
    assert second["queue_written"] is False
    assert len(queue.read_text().splitlines()) == 1


def test_unknown_owner_fixture_enters_review(tmp_path):
    result, _queue = run_cli(tmp_path, "unknown_owner", "ambiguous_owner.json")

    assert result["action"] == "review"
    assert "owner_outside_known_teams" in result["reasons"]


def test_critical_risk_fixture_forces_high_priority_review(tmp_path):
    result, _queue = run_cli(tmp_path, "critical_risk", "semantic_route.json")

    assert result["action"] == "review"
    assert result["priority"] == "high"
    assert "critical_work_reported" in result["risk_flags"]


def test_service_error_fixture_fails_safe_to_review(tmp_path):
    result, queue = run_cli(tmp_path, "api_error", "semantic_route.json")

    assert result["action"] == "review"
    assert result["model_version"] is None
    assert result["reasons"] == ["semantic_service_unavailable"]
    assert result["queue_written"] is True
    assert queue.exists()
