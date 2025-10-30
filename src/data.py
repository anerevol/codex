"""Historical data utilities."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import List

import requests

from .config import CONFIG

LOGGER = logging.getLogger(__name__)


class HistoricalDataClient:
    """Download historical OHLC data from Binance."""

    BASE_URL = "https://api.binance.com/api/v3/klines"

    def __init__(self, session: requests.Session | None = None) -> None:
        self._session = session or requests.Session()

    def fetch_daily_close(self) -> List[float]:
        cfg = CONFIG.data
        end = datetime.now(tz=timezone.utc)
        start = end - timedelta(days=cfg.lookback_years * 365)
        params = {
            "symbol": cfg.symbol,
            "interval": cfg.interval,
            "startTime": int(start.timestamp() * 1000),
            "endTime": int(end.timestamp() * 1000),
            "limit": 1000,
        }
        LOGGER.info("Requesting historical data: %s", params)
        response = self._session.get(self.BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        closes = [float(entry[4]) for entry in data]
        LOGGER.info("Fetched %d daily candles", len(closes))
        return closes
