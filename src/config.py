"""Configuration values for the crypto model pipeline."""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class GitHubConfig:
    """Parameters for GitHub model crawling."""

    query: str = "crypto AI trading"
    per_page: int = 10
    sort: str = "updated"
    order: str = "desc"


@dataclass(frozen=True)
class DataConfig:
    """Historical data collection parameters."""

    symbol: str = "BTCUSDT"
    interval: str = "1d"
    lookback_years: int = 3


@dataclass(frozen=True)
class EvaluationConfig:
    """Performance thresholds for enabling live trading."""

    min_annual_return: float = 0.15
    min_sharpe_ratio: float = 1.0
    max_drawdown: float = 0.35


@dataclass(frozen=True)
class SchedulerConfig:
    """Configuration for the daily scheduler."""

    run_time: time = time(hour=6, minute=0)  # 06:00 UTC


@dataclass(frozen=True)
class BinanceConfig:
    """API credentials and trading parameters."""

    base_url: str = "https://api.binance.com"
    api_key: str | None = os.getenv("BINANCE_API_KEY")
    api_secret: str | None = os.getenv("BINANCE_API_SECRET")
    trade_symbol: str = "BTCUSDT"
    trade_quantity: float = 0.001


@dataclass(frozen=True)
class PipelineConfig:
    """Top-level configuration container for the pipeline."""

    github: GitHubConfig = GitHubConfig()
    data: DataConfig = DataConfig()
    evaluation: EvaluationConfig = EvaluationConfig()
    scheduler: SchedulerConfig = SchedulerConfig()
    binance: BinanceConfig = BinanceConfig()


CONFIG = PipelineConfig()
