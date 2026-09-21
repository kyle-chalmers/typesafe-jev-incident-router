"""Exact response-team registry lookups."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping


def load_registry(path: str | Path) -> dict[str, str]:
    value = json.loads(Path(path).read_text())
    if not isinstance(value, dict):
        raise ValueError("response-team registry must be a JSON object")
    registry = {str(asset): str(team) for asset, team in value.items()}
    if any(not asset.strip() or not team.strip() for asset, team in registry.items()):
        raise ValueError("response-team registry keys and values must be non-empty")
    return registry


def lookup_responder(asset: str, registry: Mapping[str, str]) -> str | None:
    return registry.get(asset)

