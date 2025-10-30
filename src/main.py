"""Entry point to run the pipeline once."""
from __future__ import annotations

import logging

from .pipeline import DailyPipeline


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    pipeline = DailyPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()
