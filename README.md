# Crypto AI Trading Pipeline

This project automates the discovery, evaluation and deployment of open-source
crypto AI trading strategies.

## Features

1. **Daily crawler** – queries GitHub for repositories related to AI-driven
   crypto trading and stores the metadata locally.
2. **Backtesting** – converts discovered repositories into built-in trading
   strategy implementations and evaluates them on the last three years of
   historical BTC/USDT daily candles from Binance.
3. **Automated trading** – when a strategy beats configurable thresholds, the
   system can route a market order to Binance using API keys from environment
   variables.
4. **Daily scheduler** – a lightweight scheduler (`src/scheduler.py`) runs the
   pipeline once per day at the configured time (default 06:00 UTC).

## Quick start

1. Create a virtual environment and install dependencies::

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Provide Binance credentials via environment variables:

   ```bash
   export BINANCE_API_KEY="your-key"
   export BINANCE_API_SECRET="your-secret"
   ```

3. Run the pipeline once:

   ```bash
   python -m src.main
   ```

4. Run the daily scheduler (blocks forever and executes at the configured
   time):

   ```bash
   python -m src.scheduler
   ```

## Configuration

Configuration lives in `src/config.py` and covers GitHub search parameters,
backtest thresholds, Binance trading preferences and the scheduler run time.

## Safety

Live trading only happens when:

- The Binance API key and secret are present.
- A newly discovered strategy exceeds the annual return, Sharpe ratio and
  maximum drawdown thresholds defined in `EvaluationConfig`.

Without credentials, the pipeline logs the decisions but does not place any
orders.
