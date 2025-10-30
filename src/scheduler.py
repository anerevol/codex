"""Simple scheduler that runs the pipeline once per day."""
from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta

from .config import CONFIG
from .pipeline import DailyPipeline

LOGGER = logging.getLogger(__name__)


def _seconds_until(target_hour: int, target_minute: int) -> float:
    now = datetime.utcnow()
    target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


def run_forever() -> None:
    """Run the pipeline once per day at the configured time."""
    pipeline = DailyPipeline()
    run_time = CONFIG.scheduler.run_time
    while True:
        wait_seconds = _seconds_until(run_time.hour, run_time.minute)
        LOGGER.info("Next execution in %.2f hours", wait_seconds / 3600)
        time.sleep(wait_seconds)
        try:
            pipeline.run()
        except Exception as exc:  # pragma: no cover - defensive logging
            LOGGER.exception("Pipeline execution failed: %s", exc)
        time.sleep(60)  # avoid duplicate runs if the loop is fast
