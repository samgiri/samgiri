"""
Crypto Trading Bot — same token buy/sell every day.

Supports three strategies:
  - simple_dca    : Buy at DCA_BUY_TIME, sell at DCA_SELL_TIME (UTC)
  - rsi           : Buy when RSI < oversold, sell when RSI > overbought
  - ma_crossover  : Buy on golden cross, sell on death cross
"""

import logging
import time
from datetime import datetime, timezone

import schedule

from config import Config
from exchange import (
    fetch_ohlcv,
    get_balance,
    get_current_price,
    get_exchange,
    place_buy_order,
    place_sell_order,
)
from strategies import get_signal

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("trading_bot.log"),
    ],
)
logger = logging.getLogger(__name__)


class TradingBot:
    def __init__(self, config: Config):
        self.config = config
        self.exchange = get_exchange(config)
        self.symbol = config.SYMBOL
        self.base = config.SYMBOL.split("/")[0]
        self.quote = config.SYMBOL.split("/")[1]
        self.buy_price: float = 0.0   # Track last buy price for stop-loss / take-profit

    # ── Core cycle ────────────────────────────────────────────────────────────

    def run_cycle(self):
        """Execute one decision cycle: fetch data → signal → act."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        logger.info(f"{'='*60}")
        logger.info(f"Cycle start: {now}  |  Symbol: {self.symbol}  |  Strategy: {self.config.STRATEGY}")

        try:
            price = get_current_price(self.exchange, self.symbol)
            logger.info(f"Current price: {price:.6f} {self.quote}")

            # Check stop-loss / take-profit before generating signal
            override = self._check_risk_management(price)
            if override:
                signal = override
            else:
                df = fetch_ohlcv(
                    self.exchange,
                    self.symbol,
                    self.config.TIMEFRAME,
                    self.config.CANDLE_LIMIT,
                )
                signal = get_signal(self.config.STRATEGY, df, self.config)

            logger.info(f"Signal: {signal.upper()}")
            self._execute_signal(signal, price)

        except Exception as exc:
            logger.error(f"Error in cycle: {exc}", exc_info=True)

    # ── Risk management ───────────────────────────────────────────────────────

    def _check_risk_management(self, current_price: float):
        """Return 'sell' if stop-loss or take-profit is hit, else None."""
        if self.buy_price <= 0:
            return None

        change_pct = ((current_price - self.buy_price) / self.buy_price) * 100

        if change_pct <= -abs(self.config.STOP_LOSS_PCT):
            logger.warning(
                f"STOP-LOSS triggered! Price dropped {change_pct:.2f}% from buy price {self.buy_price:.6f}"
            )
            return "sell"

        if change_pct >= abs(self.config.TAKE_PROFIT_PCT):
            logger.info(
                f"TAKE-PROFIT triggered! Price rose {change_pct:.2f}% from buy price {self.buy_price:.6f}"
            )
            return "sell"

        return None

    # ── Order execution ───────────────────────────────────────────────────────

    def _execute_signal(self, signal: str, price: float):
        if signal == "buy":
            order = place_buy_order(self.exchange, self.symbol, self.config.BUY_AMOUNT_USDT)
            if order:
                self.buy_price = price
                self._log_balances()

        elif signal == "sell":
            order = place_sell_order(self.exchange, self.symbol, sell_pct=100.0)
            if order:
                self.buy_price = 0.0
                self._log_balances()

        else:
            logger.info("Signal is HOLD — no order placed.")

    def _log_balances(self):
        base_bal = get_balance(self.exchange, self.base)
        quote_bal = get_balance(self.exchange, self.quote)
        logger.info(f"Balances — {self.base}: {base_bal:.6f}  |  {self.quote}: {quote_bal:.4f}")

    # ── Scheduler ─────────────────────────────────────────────────────────────

    def start(self):
        """Start the bot with the configured schedule."""
        logger.info(
            f"Starting Trading Bot | Exchange: {self.config.EXCHANGE} "
            f"| Symbol: {self.symbol} | Strategy: {self.config.STRATEGY}"
        )

        strategy = self.config.STRATEGY

        if strategy == "simple_dca":
            # For DCA, check every minute so we don't miss the scheduled times
            logger.info(
                f"DCA schedule — BUY at {self.config.DCA_BUY_TIME} UTC, "
                f"SELL at {self.config.DCA_SELL_TIME} UTC (checked every minute)"
            )
            schedule.every(1).minutes.do(self.run_cycle)

        elif strategy in ("rsi", "ma_crossover"):
            # Run every hour for indicator-based strategies
            logger.info("Running indicator cycle every hour.")
            schedule.every(1).hours.do(self.run_cycle)

        else:
            # Default: every hour
            schedule.every(1).hours.do(self.run_cycle)

        # Run once immediately on start
        self.run_cycle()

        while True:
            schedule.run_pending()
            time.sleep(30)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cfg = Config()

    if not cfg.API_KEY or not cfg.API_SECRET:
        logger.error(
            "API_KEY and API_SECRET are not set. "
            "Copy .env.example to .env and fill in your credentials."
        )
        raise SystemExit(1)

    bot = TradingBot(cfg)
    bot.start()
