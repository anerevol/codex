"""Simple trading strategies used as stand-ins for downloaded models."""
from __future__ import annotations

import abc
import math
from dataclasses import dataclass
from typing import Iterable, List


class Strategy(abc.ABC):
    """Base class for trading strategies."""

    @abc.abstractmethod
    def generate_signals(self, prices: List[float]) -> List[int]:
        """Return 1 for long, -1 for short, and 0 for neutral positions."""


@dataclass
class SmaCrossStrategy(Strategy):
    """Trade on a simple moving average cross-over."""

    fast_window: int = 10
    slow_window: int = 30

    def generate_signals(self, prices: List[float]) -> List[int]:
        if len(prices) < self.slow_window:
            return [0] * len(prices)
        signals: List[int] = [0] * len(prices)
        for idx in range(self.slow_window, len(prices)):
            fast = sum(prices[idx - self.fast_window : idx]) / self.fast_window
            slow = sum(prices[idx - self.slow_window : idx]) / self.slow_window
            if fast > slow:
                signals[idx] = 1
            elif fast < slow:
                signals[idx] = -1
            else:
                signals[idx] = 0
        return signals


@dataclass
class MomentumStrategy(Strategy):
    """Trade on simple momentum; go long when return exceeds threshold."""

    lookback: int = 14
    threshold: float = 0.02

    def generate_signals(self, prices: List[float]) -> List[int]:
        signals: List[int] = [0] * len(prices)
        for idx in range(self.lookback, len(prices)):
            start = prices[idx - self.lookback]
            if start == 0:
                continue
            change = (prices[idx] - start) / start
            if change > self.threshold:
                signals[idx] = 1
            elif change < -self.threshold:
                signals[idx] = -1
        return signals


@dataclass
class HoldStrategy(Strategy):
    """A do-nothing benchmark strategy."""

    def generate_signals(self, prices: List[float]) -> List[int]:
        return [0] * len(prices)


def strategy_from_keywords(keywords: Iterable[str]) -> Strategy:
    """Return a strategy heuristic based on repository keywords."""
    keywords_lower = {kw.lower() for kw in keywords}
    if {"sma", "moving-average"} & keywords_lower:
        return SmaCrossStrategy()
    if {"momentum", "trend"} & keywords_lower:
        return MomentumStrategy()
    return SmaCrossStrategy()
