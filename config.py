import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Exchange credentials
    API_KEY = os.getenv("API_KEY", "")
    API_SECRET = os.getenv("API_SECRET", "")

    # Trading pair
    SYMBOL = os.getenv("SYMBOL", "BTC/USDT")
    BUY_AMOUNT_USDT = float(os.getenv("BUY_AMOUNT_USDT", "10"))

    # Strategy
    STRATEGY = os.getenv("STRATEGY", "simple_dca")  # ma_crossover | rsi | simple_dca
    RSI_OVERSOLD = int(os.getenv("RSI_OVERSOLD", "30"))
    RSI_OVERBOUGHT = int(os.getenv("RSI_OVERBOUGHT", "70"))
    MA_SHORT = int(os.getenv("MA_SHORT", "7"))
    MA_LONG = int(os.getenv("MA_LONG", "21"))

    # Daily schedule times (UTC)
    DCA_BUY_TIME = os.getenv("DCA_BUY_TIME", "09:00")
    DCA_SELL_TIME = os.getenv("DCA_SELL_TIME", "17:00")

    # Risk management
    STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", "5.0"))
    TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", "10.0"))

    # Exchange
    EXCHANGE = os.getenv("EXCHANGE", "binance")
    TESTNET = os.getenv("TESTNET", "true").lower() == "true"

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # OHLCV candle timeframe for analysis
    TIMEFRAME = "1h"
    CANDLE_LIMIT = 50  # How many candles to fetch for analysis
