"""
Technical Indicators Service
-----------------------------
Calculates RSI, MACD, Bollinger Bands, and Moving Averages
from historical price data. All calculations are educational
approximations and should NOT be taken as trading signals.
"""

import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

NOT_AVAILABLE = "Data unavailable"


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def calculate_sma(prices, period):
    """
    Simple Moving Average.

    Returns a list of SMA values (same length as prices).
    First (period - 1) values are None.
    """
    if not prices or len(prices) < period:
        return [None] * len(prices) if prices else []

    result = [None] * (period - 1)
    for i in range(period - 1, len(prices)):
        window = prices[i - period + 1: i + 1]
        avg = sum(window) / period
        result.append(round(avg, 2))

    return result


def calculate_ema(prices, period):
    """
    Exponential Moving Average.

    Returns a list of EMA values (same length as prices).
    First (period - 1) values are None; EMA starts at SMA.
    """
    if not prices or len(prices) < period:
        return [None] * len(prices) if prices else []

    multiplier = 2 / (period + 1)
    result = [None] * (period - 1)

    sma = sum(prices[:period]) / period
    result.append(round(sma, 2))

    for i in range(period, len(prices)):
        ema = (prices[i] - result[-1]) * multiplier + result[-1]
        result.append(round(ema, 2))

    return result


def calculate_rsi(prices, period=14):
    """
    Relative Strength Index (RSI).

    RSI = 100 - (100 / (1 + RS))
    RS = Average Gain / Average Loss over `period` days.

    Returns a list of RSI values (0-100).
    First `period` values are None.
    """
    if not prices or len(prices) < period + 1:
        return [None] * len(prices) if prices else []

    result = [None] * period

    gains = []
    losses = []

    for i in range(1, len(prices)):
        change = prices[i] - prices[i - 1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    if avg_loss == 0:
        result.append(100.0)
    else:
        rs = avg_gain / avg_loss
        result.append(round(100 - (100 / (1 + rs)), 2))

    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        if avg_loss == 0:
            result.append(100.0)
        else:
            rs = avg_gain / avg_loss
            result.append(round(100 - (100 / (1 + rs)), 2))

    return result


def calculate_macd(prices, fast=12, slow=26, signal=9):
    """
    MACD (Moving Average Convergence Divergence).

    MACD Line = EMA(fast) - EMA(slow)
    Signal Line = EMA(MACD Line, signal)
    Histogram = MACD Line - Signal Line

    Returns dict with macd_line, signal_line, histogram lists.
    """
    if not prices or len(prices) < slow + signal:
        empty = [None] * len(prices) if prices else []
        return {"macd_line": empty, "signal_line": empty, "histogram": empty}

    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)

    macd_line = []
    for i in range(len(prices)):
        if ema_fast[i] is not None and ema_slow[i] is not None:
            macd_line.append(round(ema_fast[i] - ema_slow[i], 4))
        else:
            macd_line.append(None)

    macd_values = [v for v in macd_line if v is not None]

    if len(macd_values) >= signal:
        signal_line_raw = calculate_ema(macd_values, signal)
        signal_line = [None] * (len(macd_line) - len(signal_line_raw)) + signal_line_raw
    else:
        signal_line = [None] * len(macd_line)

    histogram = []
    for i in range(len(macd_line)):
        if macd_line[i] is not None and signal_line[i] is not None:
            histogram.append(round(macd_line[i] - signal_line[i], 4))
        else:
            histogram.append(None)

    return {
        "macd_line": macd_line,
        "signal_line": signal_line,
        "histogram": histogram,
    }


def calculate_bollinger_bands(prices, period=20, num_std=2):
    """
    Bollinger Bands.

    Middle Band = SMA(period)
    Upper Band = Middle + (num_std * StdDev)
    Lower Band = Middle - (num_std * StdDev)

    Returns dict with upper, middle, lower lists.
    """
    if not prices or len(prices) < period:
        empty = [None] * len(prices) if prices else []
        return {"upper": empty, "middle": empty, "lower": empty}

    middle = calculate_sma(prices, period)
    upper = []
    lower = []

    for i in range(len(prices)):
        if middle[i] is None:
            upper.append(None)
            lower.append(None)
        else:
            window = prices[i - period + 1: i + 1]
            variance = sum((x - middle[i]) ** 2 for x in window) / period
            std_dev = variance ** 0.5

            upper.append(round(middle[i] + num_std * std_dev, 2))
            lower.append(round(middle[i] - num_std * std_dev, 2))

    return {
        "upper": upper,
        "middle": middle,
        "lower": lower,
    }


def compute_all_indicators(prices):
    """
    Compute all technical indicators from a list of closing prices.

    Returns a dict with:
        sma_20, sma_50, ema_12, ema_26
        rsi_14
        macd (dict with macd_line, signal_line, histogram)
        bollinger (dict with upper, middle, lower)
        latest values for summary
    """
    if not prices or len(prices) < 2:
        return {
            "sma_20": [],
            "sma_50": [],
            "ema_12": [],
            "ema_26": [],
            "rsi_14": [],
            "macd": {"macd_line": [], "signal_line": [], "histogram": []},
            "bollinger": {"upper": [], "middle": [], "lower": []},
            "summary": {},
            "data_points": 0,
        }

    sma_20 = calculate_sma(prices, 20)
    sma_50 = calculate_sma(prices, 50)
    ema_12 = calculate_ema(prices, 12)
    ema_26 = calculate_ema(prices, 26)
    rsi_14 = calculate_rsi(prices, 14)
    macd = calculate_macd(prices)
    bollinger = calculate_bollinger_bands(prices)

    summary = {}

    if rsi_14 and rsi_14[-1] is not None:
        rsi_val = rsi_14[-1]
        summary["rsi"] = rsi_val
        if rsi_val > 70:
            summary["rsi_signal"] = "OVERBOUGHT"
            summary["rsi_note"] = "RSI above 70 suggests the stock may be overbought."
        elif rsi_val < 30:
            summary["rsi_signal"] = "OVERSOLD"
            summary["rsi_note"] = "RSI below 30 suggests the stock may be oversold."
        else:
            summary["rsi_signal"] = "NEUTRAL"
            summary["rsi_note"] = "RSI is in neutral territory (30-70)."

    if macd["macd_line"] and macd["macd_line"][-1] is not None:
        summary["macd"] = macd["macd_line"][-1]
        if macd["signal_line"] and macd["signal_line"][-1] is not None:
            if macd["macd_line"][-1] > macd["signal_line"][-1]:
                summary["macd_signal"] = "BULLISH"
                summary["macd_note"] = "MACD above signal line suggests bullish momentum."
            else:
                summary["macd_signal"] = "BEARISH"
                summary["macd_note"] = "MACD below signal line suggests bearish momentum."

    if sma_20 and sma_20[-1] is not None:
        summary["sma_20"] = sma_20[-1]
    if sma_50 and sma_50[-1] is not None:
        summary["sma_50"] = sma_50[-1]
    if ema_12 and ema_12[-1] is not None:
        summary["ema_12"] = ema_12[-1]
    if ema_26 and ema_26[-1] is not None:
        summary["ema_26"] = ema_26[-1]

    if bollinger["upper"] and bollinger["upper"][-1] is not None:
        summary["bb_upper"] = bollinger["upper"][-1]
        summary["bb_middle"] = bollinger["middle"][-1]
        summary["bb_lower"] = bollinger["lower"][-1]
        last_price = prices[-1]
        if last_price >= bollinger["upper"][-1]:
            summary["bb_signal"] = "ABOVE_UPPER"
            summary["bb_note"] = "Price is at or above the upper Bollinger Band."
        elif last_price <= bollinger["lower"][-1]:
            summary["bb_signal"] = "BELOW_LOWER"
            summary["bb_note"] = "Price is at or below the lower Bollinger Band."
        else:
            summary["bb_signal"] = "WITHIN_BANDS"
            summary["bb_note"] = "Price is within the Bollinger Bands."

    if sma_20 and sma_20[-1] is not None and sma_50 and sma_50[-1] is not None:
        if sma_20[-1] > sma_50[-1]:
            summary["trend"] = "UPTREND"
            summary["trend_note"] = "SMA 20 is above SMA 50, indicating a short-term uptrend."
        else:
            summary["trend"] = "DOWNTREND"
            summary["trend_note"] = "SMA 20 is below SMA 50, indicating a short-term downtrend."

    return {
        "sma_20": sma_20,
        "sma_50": sma_50,
        "ema_12": ema_12,
        "ema_26": ema_26,
        "rsi_14": rsi_14,
        "macd": macd,
        "bollinger": bollinger,
        "summary": summary,
        "data_points": len(prices),
    }
