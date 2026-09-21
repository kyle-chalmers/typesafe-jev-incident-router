# Confidence-Gated Incident Router Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a runnable TypeSafe Jev incident router with deterministic lookup, typed judgments, confidence-gated policy, a durable review queue, and offline fixtures.

**Architecture:** Keep the TypeSafe transport behind a small client protocol and convert its responses into application-owned dataclasses. Keep routing policy pure and persist only the resulting review decisions. The CLI selects either a live adapter or a named fixture without changing policy code.

**Tech Stack:** Python 3.11+, uv, typesafe-sdk 0.7.0, pytest, Excalidraw

---

### Task 1: Create the public project contract

**Files:**
- Create: `pyproject.toml`
- Create: `.python-version`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `CLAUDE.md`
- Create: `README.md`
- Create: `tools/__init__.py`
- Create: `scripts/__init__.py`
- Create: `tests/__init__.py`

**Step 1:** Write `pyproject.toml` with Python `>=3.11`, `typesafe-sdk==0.7.0`, and a pytest development dependency.

**Step 2:** Add the public-facing repository notice, engineering workflow, and data-handling rules to `CLAUDE.md`. Do not include process choreography.

**Step 3:** Add `.env.example` with only `TYPESAFE_API_KEY=` and ignore `.env`, `.internal/`, `.local/`, caches, and virtual environments.

**Step 4:** Run `uv sync` and `uv run python -c "from typesafe_sdk import Choice, Noul, Score, TypeSafeClient"`.

**Expected:** Dependency sync succeeds and all SDK symbols import.

**Step 5:** Commit with `chore: initialize incident router project`.

### Task 2: Define domain models and atomic questions

**Files:**
- Create: `tools/models.py`
- Create: `tools/questions.py`
- Test: `tests/test_questions.py`

**Step 1:** Write failing tests that assert the Choice includes `other_or_unknown`, Score levels are ordered descriptions, Noul asks only what the incident states, and all thresholds are named constants.

**Step 2:** Run `uv run pytest tests/test_questions.py -q` and confirm it fails because the modules do not exist.

**Step 3:** Implement `Incident`, `JudgmentBundle`, and `RoutingDecision` dataclasses. Implement `build_questions(include_owner: bool)` and the illustrative constants `OWNER_CONFIDENCE_FLOOR = 0.75`, `IMPACT_CONFIDENCE_FLOOR = 0.70`, and `CRITICAL_WORK_REVIEW = 0.70`.

**Step 4:** Run `uv run pytest tests/test_questions.py -q` and confirm it passes.

**Step 5:** Commit with `feat: define incident judgments and policy constants`.

### Task 3: Implement deterministic registry and routing policy

**Files:**
- Create: `tools/registry.py`
- Create: `tools/policy.py`
- Create: `data/response_teams.json`
- Test: `tests/test_policy.py`

**Step 1:** Write failing tests for exact registry ownership, confident semantic assignment, low Choice confidence, `other_or_unknown`, weak Score confidence, and the critical-work risk gate.

**Step 2:** Run `uv run pytest tests/test_policy.py -q` and confirm the policy imports fail.

**Step 3:** Implement `lookup_responder(asset, registry)` and `decide(incident, registry_responder, judgments)`. The decision object must retain the incident reference, suggested responder, full Choice distribution, risk flags, model version, action, queue, priority, and reasons.

**Step 4:** Run `uv run pytest tests/test_policy.py -q` and confirm all policy branches pass.

**Step 5:** Commit with `feat: add confidence-gated routing policy`.

### Task 4: Add live and fixture clients plus durable review persistence

**Files:**
- Create: `tools/clients.py`
- Create: `tools/review_queue.py`
- Create: `data/fixtures/jev_responses.json`
- Test: `tests/test_clients.py`
- Test: `tests/test_review_queue.py`

**Step 1:** Write failing tests for fixture selection, SDK response conversion, injected timeout behavior, and idempotent JSONL persistence by incident reference.

**Step 2:** Run `uv run pytest tests/test_clients.py tests/test_review_queue.py -q` and confirm the modules are missing.

**Step 3:** Implement `TypeSafeAdapter` with `RetryPolicy(max_retries=2)` and a bounded timeout. Convert SDK answers to `JudgmentBundle` while preserving `response.model`. Implement `FixtureClient` and `ServiceUnavailable`.

**Step 4:** Implement `JsonlReviewQueue.enqueue(decision)` using atomic replacement and duplicate suppression.

**Step 5:** Run the two test files and confirm they pass.

**Step 6:** Commit with `feat: add TypeSafe and review queue adapters`.

### Task 5: Build the command line and synthetic scenarios

**Files:**
- Create: `scripts/route_incident.py`
- Create: `data/incidents/known_asset.json`
- Create: `data/incidents/semantic_route.json`
- Create: `data/incidents/ambiguous_owner.json`
- Test: `tests/test_cli.py`

**Step 1:** Write subprocess tests for fixture commands covering automatic, review, unknown-owner, critical-risk, and service-error routes.

**Step 2:** Run `uv run pytest tests/test_cli.py -q` and confirm the entry point is missing.

**Step 3:** Implement CLI flags `--incident`, `--fixture`, `--live`, `--registry`, and `--queue`. Require exactly one of `--fixture` or `--live`. Print stable formatted JSON and label the execution source.

**Step 4:** Run `uv run pytest tests/test_cli.py -q`, then run one automatic fixture and one service-error fixture manually.

**Expected:** The automatic fixture prints `action: assign`; the error fixture prints `action: review` and appends one queue entry.

**Step 5:** Commit with `feat: add incident routing commands and fixtures`.

### Task 6: Add calibration evidence

**Files:**
- Create: `data/calibration_cases.jsonl`
- Create: `scripts/evaluate_calibration.py`
- Test: `tests/test_calibration.py`

**Step 1:** Write a failing test for misroute rate, review rate, and mean time to correct responder from labeled synthetic outcomes.

**Step 2:** Implement the smallest evaluator that reads JSONL and emits the metrics with explicit denominators.

**Step 3:** Run `uv run pytest tests/test_calibration.py -q` and the command against the sample file.

**Step 4:** Commit with `feat: add calibration worksheet metrics`.

### Task 7: Create the technical diagram and finish documentation

**Files:**
- Create: `images/decision-flow.excalidraw`
- Create: `images/decision-flow.png`
- Modify: `README.md`

**Step 1:** Build the diagram in sections using the KC AI Labs palette: selection heuristic, Jev evidence artifact, Python gate, and automatic or review outcomes.

**Step 2:** Render, inspect, revise, brand, and re-render until text, arrows, and hierarchy are clean.

**Step 3:** Finish README setup, fixture commands, live command, policy explanation, privacy boundary, calibration guidance, and project structure. Embed the PNG where it explains the decision flow.

**Step 4:** Validate every external README URL and fix any broken link.

**Step 5:** Commit with `docs: explain the incident routing workflow`.

### Task 8: Verify, audit, and prepare the clean project state

**Files:**
- Create, ignored: `.internal/OWNER_CONFIG.md`
- Create, ignored: `.internal/REHEARSAL_REPORT.md`
- Create, ignored: `.internal/RECORDING_NOTES.md`
- Create, ignored: `.internal/recording-assets.json`

**Step 1:** Run `uv run pytest -q`, the full fixture matrix, calibration command, and one live smoke test. Do not assert exact live probabilities.

**Step 2:** Compare the planned approach with one simpler alternative and record why the chosen flow remains preferable.

**Step 3:** Scan every tracked file for secrets, personal values, operational identifiers, and self-referential project language. Fix every blocker.

**Step 4:** Write the internal run report and machine-readable asset manifest, then run the content workspace pre-record checker against project 44.

**Step 5:** Reset runtime artifacts, confirm `git status --short` is clean, and commit any final public fixes with `chore: finalize incident router setup`.

**Step 6:** Merge the implementation branch into local `main`. Create the public GitHub repository only after the explicit remote-write confirmation.

