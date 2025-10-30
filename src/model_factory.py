"""Translate repository metadata into strategy instances."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .strategies import Strategy, strategy_from_keywords


@dataclass
class ModelCandidate:
    metadata: Dict
    strategy: Strategy


def build_candidate(metadata: Dict) -> ModelCandidate:
    topics = metadata.get("topics") or []
    strategy = strategy_from_keywords(topics)
    return ModelCandidate(metadata=metadata, strategy=strategy)
