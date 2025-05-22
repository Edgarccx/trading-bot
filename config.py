"""
Configuration File for Exness Trading Bot

This file stores all the key parameters for the trading bot, allowing for easy
customization without modifying the main bot script.

Sections:
- Trading Parameters: Settings related to the trading instrument, volume, risk management.
- Scheduler Parameters: Settings for when and how often the trading job runs.
- Logging Parameters: Settings for log file name and logging verbosity.
"""

import MetaTrader5 as mt5
import logging # For LOG_LEVEL constants

# --- Trading Parameters ---
TRADING_SYMBOL = "EURUSD"  # The symbol to trade (e.g., "EURUSD", "GBPUSD", "XAUUSD").
                           # Ensure this symbol is available and enabled in your MetaTrader 5 terminal.

TIMEFRAME = mt5.TIMEFRAME_M15  # Timeframe for candlestick data.
                               # Examples: mt5.TIMEFRAME_M1, mt5.TIMEFRAME_M5, mt5.TIMEFRAME_M15,
                               #           mt5.TIMEFRAME_M30, mt5.TIMEFRAME_H1, mt5.TIMEFRAME_H4,
                               #           mt5.TIMEFRAME_D1.

TRADE_VOLUME = 0.01  # Trading volume in lots.
                     # Adjust based on your account size, risk tolerance, and broker's minimum volume.
                     # Common lot sizes: 0.01 (micro), 0.1 (mini), 1.0 (standard).

SL_TP_RATIO = 2.0  # Take Profit to Stop Loss ratio.
                   # E.g., 2.0 means Take Profit distance will be twice the Stop Loss distance.
                   # A value of 0 means no Take Profit will be set (if SL is also 0, order is placed without SL/TP).

NUM_CANDLES_FOR_SIGNAL = 3 # Number of candles to fetch from MetaTrader 5 for signal generation.
                           # For patterns like engulfing, this typically includes:
                           # - The current, forming candle (T)
                           # - The most recently closed candle (T-1)
                           # - The candle before the most recently closed (T-2)
                           # The signal_generator will then use T-1 and T-2.

# --- Scheduler Parameters ---
# IMPORTANT: Set this to your local timezone or the timezone of your trading server
# to ensure the scheduler runs at the intended times.
# Find valid timezones here: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
# Examples: "America/New_York", "Europe/London", "Asia/Tokyo", "UTC"
SCHEDULER_TIMEZONE = "America/New_York"

SCHEDULER_START_DATE = "2024-01-01 00:00:01" # Start date for the scheduler, format: YYYY-MM-DD HH:MM:SS.
                                             # Can be set to a date in the past to start immediately.

# Cron-like schedule for the trading job.
# Default: Runs every 15 minutes (at 1, 16, 31, 46 minutes past the hour) on weekdays.
SCHEDULER_DAY_OF_WEEK = 'mon-fri'  # e.g., 'mon-fri', 'sun,sat', '*' for all days.
SCHEDULER_HOUR = '00-23'           # e.g., '9-17' (9 AM to 5 PM), '*' for every hour.
SCHEDULER_MINUTE = '1,16,31,46'    # e.g., '0,15,30,45' for on the hour and quarter hours.

# --- Logging Parameters ---
LOG_FILE = "trading_bot.log"  # Name of the log file where bot activities will be recorded.

# Log level for the application. Determines the verbosity of the logs.
# Options (from least to most verbose): "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG".
# It's recommended to use "INFO" for normal operation and "DEBUG" for troubleshooting.
LOG_LEVEL_STR = "INFO" 
LOG_LEVEL = logging.getLevelName(LOG_LEVEL_STR.upper()) # Converts string to logging level object (e.g., logging.INFO)
                                                     # Ensures the string is uppercase for getLevelName.
```
