# Project instructions

> IMPORTANT: Everything in this repo is public-facing, so do not place any sensitive info here and make sure to distinguish between what should be internal-facing info (e.g. secrets, PII, private operating notes), and public-facing info (instructions, how-to guides, actual code utilized). If there is information the assistant needs across sessions but should not be published, put it in the `.internal/` folder which is ignored by git per the `.gitignore`.

## Project overview

This project routes synthetic data incidents. It checks an exact response-team registry first, uses TypeSafe Jev for bounded semantic judgments when exact data is unavailable, and sends uncertain or consequential cases to a durable review queue.

Intended users are data professionals and Python developers evaluating probabilistic routing inside operational workflows.

## Available tools

- `uv sync`: install the pinned environment.
- `uv run pytest -q`: run the offline test suite.
- `uv run python scripts/route_incident.py --help`: inspect routing commands.
- `uv run python scripts/evaluate_calibration.py --help`: inspect calibration metrics.

## Environment

- Python 3.11 or newer.
- `TYPESAFE_API_KEY` is required only for live requests.
- Copy `.env.example` to `.env` for local configuration. Never commit `.env`.
- Concrete private values belong in `.internal/OWNER_CONFIG.md`.

## Code conventions

- Keep questions and policy constants in `tools/questions.py`.
- Keep TypeSafe transport behind the client interface in `tools/clients.py`.
- Keep routing policy pure and independently testable.
- Preserve complete probability distributions in decision evidence.
- Treat thresholds as illustrative until they are calibrated on representative labeled cases.
- Use synthetic tracked data only.

## Workflow

1. Validate the incident input.
2. Check the exact response-team registry.
3. Evaluate bounded judgments when exact ownership is unavailable.
4. Apply policy in Python.
5. Persist review decisions when automatic routing is unsafe.
6. Verify every behavior with offline fixtures before making a live request.

## Working principles

Explain non-obvious design choices briefly. Fail safely when the service is unavailable. Keep sensitive data out of logs and fixtures. Verify results with commands and tests before reporting success.

