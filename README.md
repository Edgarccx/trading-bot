# Exness Trading Bot

## Overview
This is an automated trading bot that uses MetaTrader 5 (MT5), pandas, and APScheduler. It is designed to trade currency pairs on the Exness platform (or any MT5 compatible broker) based on Bullish and Bearish Engulfing candlestick patterns.

## Features
*   **Pattern Detection:** Identifies Bearish and Bullish Engulfing candlestick patterns.
*   **Automated Order Placement:** Automatically places market orders (buy/sell) with MetaTrader 5.
*   **Configurable Risk Management:** Allows setting Stop Loss (SL) and Take Profit (TP) levels based on a configurable ratio to the pattern candle's range.
*   **Scheduled Trading:** Uses APScheduler to run trading logic at configurable intervals (e.g., every 15 minutes).
*   **Global MT5 Connection:** Efficiently manages a single MetaTrader 5 connection.
*   **Detailed Logging:** Logs all major actions, trades, errors, and system messages to both a file (`trading_bot.log`) and the console.
*   **External Configuration:** Key parameters are managed via a `config.py` file for easy customization.

## Prerequisites
*   Python 3.7 or newer.
*   MetaTrader 5 Terminal installed and running on your system.
*   An Exness (or any other MetaTrader 5 compatible) trading account.
*   The trading account must be logged into the MetaTrader 5 terminal when the bot is running.
*   The trading symbol you intend to trade must be enabled in your MT5 Market Watch.

## Setup Instructions
1.  **Clone the Repository / Download Files:**
    *   If using Git: `git clone <repository_url>`
    *   Alternatively, download `exness_trading_bot.py` and `config.py` into the same directory.

2.  **Install Dependencies:**
    Open your terminal or command prompt and install the required Python libraries. It's recommended to use a virtual environment.
    ```bash
    pip install pandas MetaTrader5 apscheduler
    ```
    Ensure these packages are installed in the Python environment where you intend to run the bot.

## Configuration
The bot's behavior is controlled by parameters set in the `config.py` file. Open this file with a text editor to make changes.

**Key Parameters to Configure:**

*   **`TRADING_SYMBOL`**:
    *   The symbol the bot will trade (e.g., `"EURUSD"`, `"GBPUSD"`, `"XAUUSD"`).
    *   **Important:** Ensure this symbol exactly matches the symbol name provided by your broker in the MetaTrader 5 terminal (check Market Watch).
*   **`SCHEDULER_TIMEZONE`**:
    *   The timezone for the scheduler (e.g., `"America/New_York"`, `"Europe/London"`, `"UTC"`).
    *   **Crucial:** Set this to your local timezone or the timezone of your trading server to ensure jobs run at the intended times. A list of valid timezones can be found [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).
*   **`TRADE_VOLUME`**:
    *   The volume in lots for each trade (e.g., `0.01` for a micro lot).
    *   **Warning:** Trading with real money involves risk. Understand lot sizes and risk management before trading with significant volume. Start with the minimum volume allowed by your broker if unsure.

**Other Important Parameters in `config.py`:**

*   **`TIMEFRAME`**: The candlestick timeframe the bot will analyze (e.g., `mt5.TIMEFRAME_M15` for 15-minute candles).
*   **`SL_TP_RATIO`**: The ratio of Take Profit distance to Stop Loss distance.
*   **`NUM_CANDLES_FOR_SIGNAL`**: Number of candles fetched for pattern detection.
*   **`SCHEDULER_DAY_OF_WEEK`, `SCHEDULER_HOUR`, `SCHEDULER_MINUTE`**: Define the cron-like schedule for the trading job.
*   **`LOG_FILE`**: Name of the file where logs will be stored.
*   **`LOG_LEVEL_STR`**: Logging verbosity (e.g., `"INFO"`, `"DEBUG"`).

## Running the Bot
1.  Ensure your MetaTrader 5 terminal is running and you are logged into your trading account.
2.  Open your terminal or command prompt, navigate to the directory where you saved the bot files.
3.  Run the bot using:
    ```bash
    python exness_trading_bot.py
    ```
4.  The bot will initialize, connect to MetaTrader 5, and start the scheduler. Trading actions and logs will appear in the console and be saved to the log file.
5.  To stop the bot, press `Ctrl+C` in the terminal.

## Logging
*   The bot logs its activities to `trading_bot.log` (or the filename specified in `config.LOG_FILE`).
*   Logs are also printed to the console.
*   The log level (verbosity) can be configured in `config.py` via the `LOG_LEVEL_STR` parameter. For detailed troubleshooting, set it to `"DEBUG"`.

## Disclaimer
Trading financial markets, including Forex and CFDs, involves substantial risk of loss and is not suitable for every investor. Use this bot at your own risk. The developers and distributors of this bot assume no responsibility for any financial losses you may incur as a result of using this software. Always test thoroughly with a demo account before trading with real funds.
