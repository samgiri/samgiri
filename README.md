# Crypto Trading Bot

A Python trading bot that buys and sells the **same token every day** on supported exchanges (Binance, Kraken, Coinbase, Bybit).

## Features

- **3 built-in strategies**: Simple DCA, RSI, Moving Average Crossover
- **Risk management**: Stop-loss and take-profit on every position
- **Backtesting**: Test any strategy on historical data before going live
- **Testnet support**: Run safely on exchange sandboxes first
- **Configurable**: Everything driven by a `.env` file

---

## Quickstart

### 1. Clone & install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure your environment

```bash
cp .env.example .env
# Edit .env with your API keys and desired settings
```

### 3. Run the bot

```bash
python bot.py
```

---

## Strategies

| Strategy | Description | Best for |
|---|---|---|
| `simple_dca` | Buy at fixed time, sell at fixed time daily | Passive accumulation |
| `rsi` | Buy when RSI < 30, sell when RSI > 70 | Volatile markets |
| `ma_crossover` | Buy on golden cross, sell on death cross | Trending markets |

---

## Configuration (`.env`)

| Variable | Default | Description |
|---|---|---|
| `API_KEY` | — | Exchange API key |
| `API_SECRET` | — | Exchange API secret |
| `SYMBOL` | `BTC/USDT` | Token pair to trade |
| `BUY_AMOUNT_USDT` | `10` | USDT to spend per buy |
| `STRATEGY` | `simple_dca` | `simple_dca` / `rsi` / `ma_crossover` |
| `DCA_BUY_TIME` | `09:00` | UTC time to buy (DCA only) |
| `DCA_SELL_TIME` | `17:00` | UTC time to sell (DCA only) |
| `STOP_LOSS_PCT` | `5.0` | Stop-loss trigger % |
| `TAKE_PROFIT_PCT` | `10.0` | Take-profit trigger % |
| `EXCHANGE` | `binance` | Exchange name |
| `TESTNET` | `true` | Use testnet (`true`/`false`) |

---

## Backtesting

Test a strategy on the last 30 days of BTC/USDT history:

```bash
python backtest.py --symbol BTC/USDT --strategy rsi --days 30

# Other examples
python backtest.py --symbol ETH/USDT --strategy ma_crossover --days 60
python backtest.py --symbol BNB/USDT --strategy rsi --days 14 --sl 3.0 --tp 8.0
```

---

## File Structure

```
.
├── bot.py          # Main bot entry point & scheduler
├── strategies.py   # Trading strategy logic (RSI, MA, DCA)
├── exchange.py     # Exchange connection & order helpers
├── backtest.py     # Historical backtester (no real orders)
├── config.py       # Loads config from .env
├── .env.example    # Template for your .env file
└── requirements.txt
```

---

## Disclaimer

**This bot is for educational purposes only.** Crypto trading involves significant financial risk. Always test on testnet first, start with small amounts, and never trade money you cannot afford to lose.
