"""Backtesting utilities for evaluating strategies."""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Dict, Iterable, List

from .strategies import Strategy

LOGGER = logging.getLogger(__name__)


@dataclass
class BacktestResult:
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float


class Backtester:
    """Run a simple backtest on OHLC closes."""

    risk_free_rate: float = 0.0

    def run(self, strategy: Strategy, closes: List[float]) -> BacktestResult:
        LOGGER.info("Running backtest for %s", strategy)
        signals = strategy.generate_signals(closes)
        if len(signals) != len(closes):
            raise ValueError("Signals length mismatch")
        returns = self._compute_returns(closes)
        strategy_returns = [signal * r for signal, r in zip(signals, returns)]
        cumulative = self._cumulative_return(strategy_returns)
        annual = self._annualized_return(cumulative, len(returns))
        sharpe = self._sharpe_ratio(strategy_returns)
        drawdown = self._max_drawdown(strategy_returns)
        LOGGER.info(
            "Result total=%.2f%% annual=%.2f%% sharpe=%.2f drawdown=%.2f%%",
            cumulative * 100,
            annual * 100,
            sharpe,
            drawdown * 100,
        )
        return BacktestResult(cumulative, annual, sharpe, drawdown)

    @staticmethod
    def _compute_returns(closes: List[float]) -> List[float]:
        returns: List[float] = [0.0]
        for prev, curr in zip(closes, closes[1:]):
            if prev == 0:
                returns.append(0.0)
            else:
                returns.append((curr - prev) / prev)
        return returns

    @staticmethod
    def _cumulative_return(returns: Iterable[float]) -> float:
        total = 1.0
        for r in returns:
            total *= 1 + r
        return total - 1

    @staticmethod
    def _annualized_return(total_return: float, periods: int) -> float:
        if periods == 0:
            return 0.0
        years = periods / 365
        if years == 0:
            return 0.0
        return (1 + total_return) ** (1 / years) - 1

    def _sharpe_ratio(self, returns: List[float]) -> float:
        if len(returns) < 2:
            return 0.0
        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
        std = math.sqrt(variance)
        if std == 0:
            return 0.0
        excess = mean - self.risk_free_rate / 365
        return (excess / std) * math.sqrt(365)

    @staticmethod
    def _max_drawdown(returns: List[float]) -> float:
        equity = [1.0]
        for r in returns:
            equity.append(equity[-1] * (1 + r))
        peak = equity[0]
        max_dd = 0.0
        for value in equity:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_dd = max(max_dd, drawdown)
        return max_dd
