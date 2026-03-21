"""
Simple backtester — run a strategy against historical OHLCV data
without placing any real orders.

Usage:
    python backtest.py --symbol BTC/USDT --strategy rsi --days 30
"""

import argparse
import logging
from datetime import datetime, timezone

import ccxt
import pandas as pd

from config import Config
from strategies import get_signal

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def fetch_history(symbol: str, timeframe: str, days: int) -> pd.DataFrame:
    """Fetch historical OHLCV data from Binance (public, no auth needed)."""
    exchange = ccxt.binance({"enableRateLimit": True})
    since_ms = exchange.parse8601(
        (pd.Timestamp.utcnow() - pd.Timedelta(days=days)).isoformat() + "Z"
    )
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since_ms, limit=1000)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df


def run_backtest(symbol: str, strategy: str, days: int, buy_amount: float,
                 stop_loss_pct: float, take_profit_pct: float):
    config = Config()
    config.SYMBOL = symbol
    config.STRATEGY = strategy
    config.BUY_AMOUNT_USDT = buy_amount
    config.STOP_LOSS_PCT = stop_loss_pct
    config.TAKE_PROFIT_PCT = take_profit_pct

    logger.info(f"Fetching {days} days of {symbol} ({strategy}) history...")
    df = fetch_history(symbol, "1h", days)
    logger.info(f"Fetched {len(df)} candles.")

    usdt = 1000.0   # Starting capital
    holdings = 0.0
    buy_price = 0.0
    trades = []

    for i in range(50, len(df)):
        window = df.iloc[: i + 1]
        price = float(window["close"].iloc[-1])
        ts = window.index[-1]

        # Risk management check
        signal = "hold"
        if holdings > 0 and buy_price > 0:
            change_pct = ((price - buy_price) / buy_price) * 100
            if change_pct <= -abs(stop_loss_pct):
                signal = "sell"
                logger.debug(f"{ts} STOP-LOSS at {price:.2f}  change={change_pct:.2f}%")
            elif change_pct >= abs(take_profit_pct):
                signal = "sell"
                logger.debug(f"{ts} TAKE-PROFIT at {price:.2f}  change={change_pct:.2f}%")

        if signal == "hold":
            signal = get_signal(strategy, window, config)

        if signal == "buy" and usdt >= buy_amount:
            qty = buy_amount / price
            holdings += qty
            usdt -= buy_amount
            buy_price = price
            trades.append({"time": ts, "action": "BUY", "price": price, "qty": qty, "usdt": usdt})

        elif signal == "sell" and holdings > 0:
            proceeds = holdings * price
            usdt += proceeds
            trades.append({"time": ts, "action": "SELL", "price": price, "qty": holdings, "usdt": usdt})
            holdings = 0.0
            buy_price = 0.0

    # Final liquidation
    final_price = float(df["close"].iloc[-1])
    total_value = usdt + holdings * final_price

    print("\n" + "=" * 60)
    print(f"  Backtest Results — {symbol} | {strategy} | {days} days")
    print("=" * 60)
    print(f"  Starting capital : $1,000.00")
    print(f"  Final value      : ${total_value:,.2f}")
    print(f"  P&L              : ${total_value - 1000:,.2f}  ({((total_value/1000)-1)*100:.2f}%)")
    print(f"  Total trades     : {len(trades)}")
    buys  = [t for t in trades if t["action"] == "BUY"]
    sells = [t for t in trades if t["action"] == "SELL"]
    print(f"  Buys / Sells     : {len(buys)} / {len(sells)}")
    print("=" * 60)

    if trades:
        trades_df = pd.DataFrame(trades)
        print("\nTrade log (last 10):")
        print(trades_df.tail(10).to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crypto Trading Bot Backtester")
    parser.add_argument("--symbol",   default="BTC/USDT",      help="Trading pair")
    parser.add_argument("--strategy", default="rsi",
                        choices=["rsi", "ma_crossover", "simple_dca"])
    parser.add_argument("--days",     type=int, default=30,    help="Number of days to backtest")
    parser.add_argument("--amount",   type=float, default=100, help="Buy amount per trade (USDT)")
    parser.add_argument("--sl",       type=float, default=5.0, help="Stop-loss %")
    parser.add_argument("--tp",       type=float, default=10.0,help="Take-profit %")
    args = parser.parse_args()

    run_backtest(args.symbol, args.strategy, args.days, args.amount, args.sl, args.tp)
