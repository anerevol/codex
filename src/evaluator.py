"""Evaluate model candidates against historical data."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, List

from .backtester import Backtester, BacktestResult
from .config import CONFIG
from .data import HistoricalDataClient
from .model_factory import ModelCandidate

LOGGER = logging.getLogger(__name__)


@dataclass
class EvaluationOutcome:
    candidate: ModelCandidate
    result: BacktestResult
    eligible_for_live: bool


class ModelEvaluator:
    """Run backtests and apply selection criteria."""

    def __init__(self, data_client: HistoricalDataClient | None = None, backtester: Backtester | None = None) -> None:
        self._data_client = data_client or HistoricalDataClient()
        self._backtester = backtester or Backtester()

    def evaluate(self, candidates: Iterable[ModelCandidate]) -> List[EvaluationOutcome]:
        closes = self._data_client.fetch_daily_close()
        outcomes: List[EvaluationOutcome] = []
        for candidate in candidates:
            result = self._backtester.run(candidate.strategy, closes)
            eligible = self._passes_thresholds(result)
            outcomes.append(EvaluationOutcome(candidate, result, eligible))
        return outcomes

    @staticmethod
    def _passes_thresholds(result: BacktestResult) -> bool:
        cfg = CONFIG.evaluation
        if result.annualized_return < cfg.min_annual_return:
            LOGGER.info("Annualized return %.2f below threshold %.2f", result.annualized_return, cfg.min_annual_return)
            return False
        if result.sharpe_ratio < cfg.min_sharpe_ratio:
            LOGGER.info("Sharpe %.2f below threshold %.2f", result.sharpe_ratio, cfg.min_sharpe_ratio)
            return False
        if result.max_drawdown > cfg.max_drawdown:
            LOGGER.info("Drawdown %.2f above threshold %.2f", result.max_drawdown, cfg.max_drawdown)
            return False
        return True
