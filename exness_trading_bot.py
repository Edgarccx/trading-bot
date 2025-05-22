# exness_trading_bot.py

import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import time # Import time module for delays if needed

# --- Signal Generator Function (remains exactly the same) ---
def signal_generator(df):
    open_c = df.Open.iloc[-1]
    close_c = df.Close.iloc[-1]
    previous_open = df.Open.iloc[-2]
    previous_close = df.Close.iloc[-2]

    # Bearish Engulfing Pattern (Sell Signal)
    if (open_c > close_c and
        previous_open < previous_close and
        close_c < previous_open and
        open_c >= previous_close):
        return 1  # Sell Signal

    # Bullish Engulfing Pattern (Buy Signal)
    elif (open_c < close_c and
          previous_open > previous_close and
          close_c > previous_open and
          open_c <= previous_close):
        return 2  # Buy Signal

    else:
        return 0 # No Signal


# --- Function to get live candlestick data from MetaTrader 5 ---
def get_candles_mt5(symbol, timeframe, count):
    if not mt5.initialize():
        print("MetaTrader5 initialization failed, error code =", mt5.last_error())
        return None

    # IMPORTANT: Wait a moment for MT5 to initialize data if it just started
    # time.sleep(1) # Uncomment if you face issues getting initial data

    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)

    mt5.shutdown() # Shutdown MT5 connection after getting data (re-init on next call)

    if rates is None:
        print(f"Failed to get rates for {symbol}, error code =", mt5.last_error())
        return None

    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'tick_volume': 'Volume'}, inplace=True)
    return df[['Open', 'High', 'Low', 'Close', 'Volume']]


# --- Function to place orders in MetaTrader 5 ---
def place_order_mt5(symbol, volume, order_type, sl_price, tp_price):
    if not mt5.initialize():
        print("MetaTrader5 initialization failed, error code =", mt5.last_error())
        return None

    # Get symbol info to check min/max volume, step, etc.
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Failed to get symbol info for {symbol}. Error: {mt5.last_error()}")
        mt5.shutdown()
        return None

    # Normalize volume to ensure it's within min/max/step allowed by the broker for the symbol
    # This is crucial for avoiding 10004 errors (invalid volume)
    normalized_volume = mt5.normalize_request_volume(symbol, volume, order_type)
    if normalized_volume != volume:
        print(f"Warning: Volume adjusted from {volume} to {normalized_volume} for {symbol}")
        volume = normalized_volume

    # Get current prices for accurate order placement
    tick_info = mt5.symbol_info_tick(symbol)
    if tick_info is None:
        print(f"Failed to get tick info for {symbol}. Error: {mt5.last_error()}")
        mt5.shutdown()
        return None

    order_price = 0.0
    if order_type == "buy":
        order_price = tick_info.ask
    elif order_type == "sell":
        order_price = tick_info.bid

    # Define the request dictionary for an order
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type_filling": mt5.ORDER_FILLING_FOC, # Fill or Kill
        "comment": "Python Algo Bot",
        "type_time": mt5.ORDER_TIME_GTC # Good Till Cancel
    }

    if order_type == "buy":
        request["type"] = mt5.ORDER_TYPE_BUY
        request["price"] = order_price
        request["sl"] = sl_price
        request["tp"] = tp_price
    elif order_type == "sell":
        request["type"] = mt5.ORDER_TYPE_SELL
        request["price"] = order_price
        request["sl"] = sl_price
        request["tp"] = tp_price
    else:
        print("Invalid order type.")
        mt5.shutdown()
        return None

    # Send the order
    result = mt5.order_send(request)
    mt5.shutdown()

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order failed: {result.comment} (Retcode: {result.retcode})")
        print(f"Request: {request}")
        # Optionally print detailed result if available
        if result.request:
            print(f"Result Request: {result.request_id}, {result.request.comment}")
        return None
    else:
        print(f"Order successful! Ticket: {result.order}, Type: {order_type}, Volume: {volume}")
        print(f"Price: {result.price}, SL: {result.request.sl}, TP: {result.request.tp}")
        return result

# --- Main Trading Job Function ---
def trading_job():
    print(f"\n--- Running Trading Job at {datetime.now()} ---")

    symbol = "EURUSD" # Confirm this symbol name in your Exness MT5 platform
    timeframe = mt5.TIMEFRAME_M15 # 15-minute timeframe
    num_candles = 3 # Get enough candles for pattern detection (current + 2 previous closed)

    df_live = get_candles_mt5(symbol, timeframe, num_candles)

    if df_live is None or df_live.empty or len(df_live) < num_candles:
        print("Failed to get enough live data or data is incomplete. Skipping trade.")
        return

    # Print live candlestick data (last 'num_candles' for context)
    print("Live Candlestick Data:")
    print(df_live.tail(num_candles)) # Use .tail() for clearer display of recent data

    # Generate the signal using the last two *closed* candles (which are iloc[-2] and iloc[-1] in this df_live)
    # The signal_generator function is designed to look at the last two entries it receives
    # df_live.iloc[-2:] creates a slice with just the last two closed candles for the signal function
    signal = signal_generator(df_live) # Pass the full DF, signal_generator will use its internal iloc logic
    print(f"Generated Signal: {signal}")

    # --- Risk Management: Stop Loss (SL) and Take Profit (TP) Calculation ---
    SLTPRatio = 2.0 # Take Profit is 2 times the Stop Loss distance

    # Use the range of the PREVIOUSLY CLOSED candle (iloc[-2]) for SL/TP distance
    # The current candle (iloc[-1]) is still forming, so its High/Low might not be final.
    previous_candle_high = df_live['High'].iloc[-2]
    previous_candle_low = df_live['Low'].iloc[-2]

    # Calculate range based on High-Low of the previous candle
    previous_candle_range = previous_candle_high - previous_candle_low

    # Get current prices for accurate order placement and SL/TP calculations
    tick_info = mt5.symbol_info_tick(symbol)
    if tick_info is None:
        print(f"Failed to get current tick info for {symbol}. Error: {mt5.last_error()}")
        return

    current_ask_price = tick_info.ask
    current_bid_price = tick_info.bid

    print(f"Current Ask: {current_ask_price:.5f}, Current Bid: {current_bid_price:.5f}")
    print(f"Previous Candle Range (SL Distance): {previous_candle_range:.5f}")

    # Calculate Stop Loss and Take Profit prices based on current market prices
    # Note: These are absolute prices, not distances.
    SLBuy = current_bid_price - previous_candle_range # For Buy, SL is below bid
    SLSell = current_ask_price + previous_candle_range # For Sell, SL is above ask

    TPBuy = current_ask_price + (previous_candle_range * SLTPRatio) # For Buy, TP is above ask
    TPSell = current_bid_price - (previous_candle_range * SLTPRatio) # For Sell, TP is below bid

    print(f"TPBuy: {TPBuy:.5f}, SLBuy: {SLBuy:.5f}")
    print(f"TPSell: {TPSell:.5f}, SLSell: {SLSell:.5f}")

    # --- Order Execution ---
    # Volume (in lots) - Adjust this carefully for your Exness account and risk tolerance.
    # Exness (and MT5) typically uses lots. 0.01 is a micro lot.
    trade_volume = 0.01

    # Sell Order (Signal == 1)
    if signal == 1:
        print(f"Attempting to place SELL order for {symbol} with {trade_volume} lots...")
        place_order_mt5(symbol, trade_volume, "sell", SLSell, TPSell)

    # Buy Order (Signal == 2)
    elif signal == 2:
        print(f"Attempting to place BUY order for {symbol} with {trade_volume} lots...")
        place_order_mt5(symbol, trade_volume, "buy", SLBuy, TPBuy)

    else:
        print("No clear signal. No trade executed.")


# --- Scheduler Setup ---
scheduler = BlockingScheduler()

# Add the trading_job to be executed
# 'cron' trigger allows for precise scheduling similar to cron jobs
# day_of_week='mon-fri': Only run on weekdays
# hour='00-23': Run every hour
# minute='1,16,31,46': Run at these specific minutes past the hour (for 15-minute intervals)
# start_date='YYYY-MM-DD HH:MM:SS': When to start the scheduling (should be in the past or very near future)
# timezone='America/New_York': Set your local timezone (important for correct scheduling)
# Find valid timezones here: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
scheduler.add_job(
    trading_job,
    'cron',
    day_of_week='mon-fri',
    hour='00-23',
    minute='1,16,31,46', # This schedules it at 1 min past, 16 min past, 31 min past, 46 min past every hour
    start_date='2024-01-01 00:00:01', # Adjust this to a recent past date/time
    timezone='America/New_York' # IMPORTANT: Change this to your local timezone!
)

print("Scheduler started. The trading bot will now run automatically.")
print("Press Ctrl+C to exit the scheduler.")

try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    print("Scheduler stopped.")