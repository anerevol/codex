"""Binance trading adapter."""
from __future__ import annotations

import hmac
import logging
from dataclasses import dataclass
from hashlib import sha256
from time import time
from typing import Dict

import requests

from .config import CONFIG

LOGGER = logging.getLogger(__name__)


@dataclass
class TradeDecision:
    """A recommendation produced after evaluation."""

    symbol: str
    side: str
    quantity: float


class Trader:
    """Place market orders against Binance's REST API."""

    ORDER_ENDPOINT = "/api/v3/order"

    def __init__(self, session: requests.Session | None = None) -> None:
        self._session = session or requests.Session()
        self._cfg = CONFIG.binance

    def execute(self, decision: TradeDecision) -> Dict:
        if not self._cfg.api_key or not self._cfg.api_secret:
            LOGGER.warning("No Binance credentials provided; skipping live trade")
            return {"status": "skipped", "reason": "missing credentials"}
        LOGGER.info("Submitting order to Binance: %s", decision)
        payload = {
            "symbol": decision.symbol,
            "side": decision.side.upper(),
            "type": "MARKET",
            "quantity": f"{decision.quantity:.6f}",
            "timestamp": int(time() * 1000),
        }
        payload["signature"] = self._sign(payload)
        headers = {"X-MBX-APIKEY": self._cfg.api_key}
        response = self._session.post(
            f"{self._cfg.base_url}{self.ORDER_ENDPOINT}",
            headers=headers,
            params=payload,
            timeout=30,
        )
        response.raise_for_status()
        LOGGER.info("Order successful: %s", response.json())
        return response.json()

    def _sign(self, payload: Dict[str, str]) -> str:
        query = "&".join(f"{key}={value}" for key, value in payload.items() if key != "signature")
        signature = hmac.new(self._cfg.api_secret.encode(), query.encode(), sha256).hexdigest()
        return signature
