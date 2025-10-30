"""Persistence helpers for the discovered models."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List

LOGGER = logging.getLogger(__name__)


@dataclass
class ModelRepository:
    """Persist model metadata in a JSON file."""

    path: Path
    _models: Dict[int, Dict] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.path.exists():
            self._models = self._load()
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text("{}", encoding="utf-8")

    def update(self, models: Iterable[Dict]) -> List[Dict]:
        """Store unseen models and return the new ones."""
        new_models: List[Dict] = []
        for model in models:
            model_id = model.get("id")
            if model_id is None:
                continue
            if model_id not in self._models:
                LOGGER.info("Discovered new model: %s", model.get("full_name"))
                self._models[model_id] = model
                new_models.append(model)
        if new_models:
            self._persist()
        return new_models

    def _persist(self) -> None:
        self.path.write_text(json.dumps(self._models, indent=2, sort_keys=True), encoding="utf-8")

    def _load(self) -> Dict[int, Dict]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            LOGGER.warning("Model store corrupted, resetting: %s", self.path)
            return {}
