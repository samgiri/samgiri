import ccxt
import logging
import pandas as pd
from config import Config

logger = logging.getLogger(__name__)


def get_exchange(config: Config) -> ccxt.Exchange:
    """Initialize and return the ccxt exchange instance."""
    exchange_class = getattr(ccxt, config.EXCHANGE)
    exchange = exchange_class(
        {
            "apiKey": config.API_KEY,
            "secret": config.API_SECRET,
            "enableRateLimit": True,
            "options": {"defaultType": "spot"},
        }
    )

    if config.TESTNET:
        if hasattr(exchange, "set_sandbox_mode"):
            exchange.set_sandbox_mode(True)
            logger.info(f"[TESTNET] Connected to {config.EXCHANGE} sandbox.")
        else:
            logger.warning(f"{config.EXCHANGE} does not support sandbox mode. Running in live mode.")
    else:
        logger.info(f"Connected to {config.EXCHANGE} (LIVE).")

    return exchange


def fetch_ohlcv(exchange: ccxt.Exchange, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
    """Fetch OHLCV candles and return as a DataFrame."""
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df


def get_balance(exchange: ccxt.Exchange, currency: str) -> float:
    """Return the free balance for a given currency."""
    balance = exchange.fetch_balance()
    return float(balance.get("free", {}).get(currency, 0.0))


def get_current_price(exchange: ccxt.Exchange, symbol: str) -> float:
    """Fetch the latest ticker price for a symbol."""
    ticker = exchange.fetch_ticker(symbol)
    return float(ticker["last"])


def place_buy_order(exchange: ccxt.Exchange, symbol: str, amount_usdt: float) -> dict:
    """
    Place a market buy order using a fixed USDT amount.
    Returns the order dict.
    """
    price = get_current_price(exchange, symbol)
    base_currency = symbol.split("/")[0]
    quote_currency = symbol.split("/")[1]

    quote_balance = get_balance(exchange, quote_currency)
    if quote_balance < amount_usdt:
        logger.warning(
            f"Insufficient {quote_currency} balance: {quote_balance:.4f} < {amount_usdt:.4f}"
        )
        return {}

    # Calculate quantity to buy
    quantity = amount_usdt / price
    market = exchange.market(symbol)
    quantity = exchange.amount_to_precision(symbol, quantity)

    logger.info(
        f"BUY  {quantity} {base_currency} @ ~{price:.4f} {quote_currency}  "
        f"(cost ~{amount_usdt:.2f} {quote_currency})"
    )
    order = exchange.create_market_buy_order(symbol, float(quantity))
    logger.info(f"Buy order placed: {order.get('id')}  status={order.get('status')}")
    return order


def place_sell_order(exchange: ccxt.Exchange, symbol: str, sell_pct: float = 100.0) -> dict:
    """
    Sell a percentage of the held base-currency balance.
    sell_pct=100 sells everything; sell_pct=50 sells half.
    """
    base_currency = symbol.split("/")[0]
    balance = get_balance(exchange, base_currency)

    if balance <= 0:
        logger.warning(f"No {base_currency} balance to sell.")
        return {}

    quantity = balance * (sell_pct / 100.0)
    quantity = exchange.amount_to_precision(symbol, quantity)
    price = get_current_price(exchange, symbol)

    logger.info(
        f"SELL {quantity} {base_currency} @ ~{price:.4f}  "
        f"(est. value ~{float(quantity) * price:.2f})"
    )
    order = exchange.create_market_sell_order(symbol, float(quantity))
    logger.info(f"Sell order placed: {order.get('id')}  status={order.get('status')}")
    return order
