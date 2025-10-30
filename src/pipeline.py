"""Daily pipeline tying together crawling, evaluation and trading."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, List

from .config import CONFIG
from .crawler import GitHubModelCrawler
from .evaluator import ModelEvaluator
from .model_factory import ModelCandidate, build_candidate
from .model_repository import ModelRepository
from .trader import TradeDecision, Trader

LOGGER = logging.getLogger(__name__)


class DailyPipeline:
    """End-to-end pipeline executed each day."""

    def __init__(
        self,
        repository_path: Path = Path("data/models.json"),
        crawler: GitHubModelCrawler | None = None,
        evaluator: ModelEvaluator | None = None,
        trader: Trader | None = None,
    ) -> None:
        self._model_store = ModelRepository(repository_path)
        self._crawler = crawler or GitHubModelCrawler()
        self._evaluator = evaluator or ModelEvaluator()
        self._trader = trader or Trader()

    def run(self) -> List[TradeDecision]:
        LOGGER.info("Starting daily pipeline")
        repositories = self._crawler.fetch_recent_models()
        new_repositories = self._model_store.update(repositories)
        if not new_repositories:
            LOGGER.info("No new repositories discovered")
            return []
        candidates = self._build_candidates(new_repositories)
        outcomes = self._evaluator.evaluate(candidates)
        decisions: List[TradeDecision] = []
        for outcome in outcomes:
            metadata = outcome.candidate.metadata
            if outcome.eligible_for_live:
                decision = TradeDecision(
                    symbol=CONFIG.binance.trade_symbol,
                    side="BUY",
                    quantity=CONFIG.binance.trade_quantity,
                )
                LOGGER.info("Strategy %s eligible, preparing live trade", metadata.get("full_name"))
                self._trader.execute(decision)
                decisions.append(decision)
            else:
                LOGGER.info("Strategy %s not eligible for live trading", metadata.get("full_name"))
        return decisions

    def _build_candidates(self, repositories: Iterable[dict]) -> List[ModelCandidate]:
        return [build_candidate(repo) for repo in repositories]
