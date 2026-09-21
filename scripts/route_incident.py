"""Route one synthetic incident through deterministic and semantic policy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.clients import FixtureClient, ServiceUnavailable, TypeSafeAdapter
from tools.models import Incident, RoutingDecision
from tools.policy import REVIEW_QUEUE, decide
from tools.registry import load_registry, lookup_responder
from tools.review_queue import JsonlReviewQueue


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURES = ROOT / "data" / "fixtures" / "jev_responses.json"
DEFAULT_REGISTRY = ROOT / "data" / "response_teams.json"
DEFAULT_QUEUE = ROOT / ".local" / "review_queue.jsonl"


def service_failure_decision(incident: Incident) -> RoutingDecision:
    return RoutingDecision(
        incident_reference=incident.reference,
        action="review",
        queue=REVIEW_QUEUE,
        priority="high",
        suggested_responder=None,
        reasons=("semantic_service_unavailable",),
        model_version=None,
        source="service_error",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Route a synthetic data incident with TypeSafe Jev or a fixture."
    )
    parser.add_argument("--incident", type=Path, required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--fixture", help="Named fixture from jev_responses.json")
    source.add_argument("--live", action="store_true", help="Call the TypeSafe API")
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    incident = Incident.from_mapping(json.loads(args.incident.read_text()))
    registry = load_registry(args.registry)
    registry_responder = lookup_responder(incident.affected_asset, registry)
    include_owner = registry_responder is None

    if args.live:
        client = TypeSafeAdapter()
        execution_source = "live"
    else:
        client = FixtureClient(args.fixtures, args.fixture)
        execution_source = f"fixture:{args.fixture}"

    try:
        judgments = client.evaluate(incident, include_owner=include_owner)
        decision = decide(
            incident,
            registry_responder=registry_responder,
            judgments=judgments,
        )
    except ServiceUnavailable:
        decision = service_failure_decision(incident)

    queue_written = False
    if decision.action == "review":
        queue_written = JsonlReviewQueue(args.queue).enqueue(decision)

    payload = decision.to_dict()
    payload["execution_source"] = execution_source
    payload["queue_written"] = queue_written
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
