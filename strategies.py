import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def compute_rsi(prices: pd.Series, period: int = 14) -> float:
    """Compute the latest RSI value from a price series."""
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1])


def rsi_strategy(df: pd.DataFrame, oversold: int = 30, overbought: int = 70) -> str:
    """
    RSI Strategy:
    - BUY  when RSI < oversold threshold
    - SELL when RSI > overbought threshold
    - HOLD otherwise
    """
    rsi = compute_rsi(df["close"])
    logger.info(f"RSI value: {rsi:.2f}")

    if rsi < oversold:
        return "buy"
    elif rsi > overbought:
        return "sell"
    return "hold"


def ma_crossover_strategy(df: pd.DataFrame, short: int = 7, long: int = 21) -> str:
    """
    Moving Average Crossover Strategy:
    - BUY  when short MA crosses above long MA (golden cross)
    - SELL when short MA crosses below long MA (death cross)
    - HOLD otherwise
    """
    if len(df) < long + 1:
        logger.warning("Not enough candles for MA crossover.")
        return "hold"

    ma_short = df["close"].rolling(short).mean()
    ma_long = df["close"].rolling(long).mean()

    prev_short = ma_short.iloc[-2]
    prev_long = ma_long.iloc[-2]
    curr_short = ma_short.iloc[-1]
    curr_long = ma_long.iloc[-1]

    logger.info(
        f"MA{short}={curr_short:.4f}  MA{long}={curr_long:.4f} | "
        f"prev MA{short}={prev_short:.4f}  prev MA{long}={prev_long:.4f}"
    )

    if prev_short <= prev_long and curr_short > curr_long:
        return "buy"   # Golden cross
    elif prev_short >= prev_long and curr_short < curr_long:
        return "sell"  # Death cross
    return "hold"


def simple_dca_strategy(current_time_str: str, buy_time: str, sell_time: str) -> str:
    """
    Simple DCA (Dollar Cost Averaging) Strategy:
    - BUY  at configured buy time every day
    - SELL at configured sell time every day

    current_time_str: "HH:MM" in UTC
    """
    if current_time_str == buy_time:
        return "buy"
    elif current_time_str == sell_time:
        return "sell"
    return "hold"


def get_signal(strategy: str, df: pd.DataFrame, config) -> str:
    """
    Route to the correct strategy and return: 'buy' | 'sell' | 'hold'
    """
    if strategy == "rsi":
        return rsi_strategy(df, config.RSI_OVERSOLD, config.RSI_OVERBOUGHT)
    elif strategy == "ma_crossover":
        return ma_crossover_strategy(df, config.MA_SHORT, config.MA_LONG)
    elif strategy == "simple_dca":
        from datetime import datetime, timezone
        now_utc = datetime.now(timezone.utc).strftime("%H:%M")
        return simple_dca_strategy(now_utc, config.DCA_BUY_TIME, config.DCA_SELL_TIME)
    else:
        logger.warning(f"Unknown strategy '{strategy}', defaulting to hold.")
        return "hold"
