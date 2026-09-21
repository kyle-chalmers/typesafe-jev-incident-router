"""Durable local persistence for human-review decisions."""

from __future__ import annotations

import json
import os
from pathlib import Path

from tools.models import RoutingDecision


class JsonlReviewQueue:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def enqueue(self, decision: RoutingDecision) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        existing = self.path.read_text().splitlines() if self.path.exists() else []
        for line in existing:
            if json.loads(line).get("incident_reference") == decision.incident_reference:
                return False

        payload = json.dumps(decision.to_dict(), sort_keys=True)
        temp_path = self.path.with_name(f".{self.path.name}.tmp")
        with temp_path.open("w") as handle:
            if existing:
                handle.write("\n".join(existing) + "\n")
            handle.write(payload + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, self.path)
        return True
