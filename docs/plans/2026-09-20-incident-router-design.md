# Confidence-Gated Incident Router Design

## Goal

Build a small Python application that routes synthetic data incidents using deterministic registry data first, Jev for bounded semantic judgments, and a durable human-review queue whenever policy does not permit automatic routing.

## Chosen approach

Use a production-shaped command-line application with separate modules for questions, registry lookups, TypeSafe transport, routing policy, and review-queue persistence. This structure makes the central boundary inspectable: Jev returns typed judgments, while ordinary Python determines what may happen next.

A single-file example would be shorter, but it would hide the transport and policy boundary. A live-generated skeleton would add output variance without teaching anything essential about the router.

## Technology

- Python 3.11 or newer
- `uv` for environment and command execution
- `typesafe-sdk==0.7.0`
- `pytest` for offline policy and integration tests
- Standard-library JSON and JSONL persistence

## Components

- `tools/questions.py`: the three atomic questions and every illustrative threshold in one audit surface.
- `tools/models.py`: application-owned dataclasses for incidents, model judgments, and routing decisions.
- `tools/registry.py`: exact asset-to-response-team lookup.
- `tools/clients.py`: the live TypeSafe adapter, fixture client, and explicit service-error boundary.
- `tools/policy.py`: a pure function that maps registry facts and typed judgments to an automatic assignment or review decision.
- `tools/review_queue.py`: idempotent JSONL persistence keyed by incident reference.
- `scripts/route_incident.py`: command-line entry point for fixture and live execution.
- `scripts/evaluate_calibration.py`: a small worksheet command that reports routing and review metrics from labeled synthetic cases.

## Data flow

1. Validate one synthetic incident at the boundary.
2. Check the response-team registry for an exact asset match.
3. If the response team is unknown, ask Jev a Choice with an `other_or_unknown` option. Score and Noul are evaluated against the same state.
4. Preserve the complete answer distributions and concrete model version.
5. Apply named Python thresholds.
6. Write uncertain, high-risk, or failed evaluations to the review queue with the evidence needed by a person.
7. Emit one stable decision object as JSON.

## Illustrative policy

- An exact registry responder overrides semantic ownership inference.
- `other_or_unknown` always enters review.
- Choice confidence below `0.75` enters review.
- Score confidence below `0.70` enters review because the priority is insufficiently supported.
- A critical-work Noul probability of `0.70` or higher forces high-priority review.
- A service failure after two SDK retries enters high-priority review.
- These constants are examples, not production defaults. The calibration command reports evidence for choosing replacements.

## Failure handling

The live adapter uses `RetryPolicy(max_retries=2)` and a bounded timeout. It converts SDK or transport failures into an application error without discarding the incident. The caller creates a review decision and persists it to the local queue. Fixture mode can inject the same error path without contacting TypeSafe.

## Testing

Offline tests cover exact-registry routing, confident semantic routing, low Choice confidence, `other_or_unknown`, weak Score confidence, the critical-work risk gate, queue idempotency, and API failure. One opt-in live smoke test verifies the current SDK and records the returned model version without asserting unstable probabilities.

## Public-data boundary

All tracked incidents are synthetic. `.env`, `.internal/`, and runtime queue files remain untracked. The public documentation tells teams to evaluate vendor approval, retention, residency, and redaction requirements before sending operational or sensitive incident text.

## Diagram

A branded Excalidraw diagram presents the selection heuristic as four lanes and then zooms into the Jev lane: typed answers feed a Python confidence gate, which branches to automatic routing or a durable review queue. The diagram includes a concrete Choice distribution as evidence rather than generic component labels.

