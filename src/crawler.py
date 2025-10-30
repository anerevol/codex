"""Utilities for discovering recent open-source crypto AI trading models."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

import requests

from .config import CONFIG

LOGGER = logging.getLogger(__name__)


class GitHubModelCrawler:
    """Fetch model repositories from GitHub search."""

    SEARCH_URL = "https://api.github.com/search/repositories"

    def __init__(self, session: requests.Session | None = None) -> None:
        self._session = session or requests.Session()

    def fetch_recent_models(self) -> List[Dict[str, Any]]:
        """Return metadata for the latest repositories that match the query."""
        cfg = CONFIG.github
        params = {
            "q": cfg.query,
            "sort": cfg.sort,
            "order": cfg.order,
            "per_page": cfg.per_page,
        }
        LOGGER.debug("Querying GitHub: %s", params)
        response = self._session.get(self.SEARCH_URL, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        items = payload.get("items", [])
        LOGGER.info("Fetched %d repositories from GitHub", len(items))
        return [self._normalize(item) for item in items]

    @staticmethod
    def _normalize(item: Dict[str, Any]) -> Dict[str, Any]:
        pushed_at = item.get("pushed_at")
        pushed = datetime.fromisoformat(pushed_at.replace("Z", "+00:00")) if pushed_at else None
        return {
            "id": item.get("id"),
            "name": item.get("name"),
            "full_name": item.get("full_name"),
            "description": item.get("description"),
            "html_url": item.get("html_url"),
            "pushed_at": pushed.isoformat() if pushed else None,
            "stargazers_count": item.get("stargazers_count", 0),
            "language": item.get("language"),
            "topics": item.get("topics", []),
        }
