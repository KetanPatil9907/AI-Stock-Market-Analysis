"""
Enhanced 3-6 Month Stock Prediction & Recommendation Engine.

Uses multi-factor scoring combining technical momentum, fundamentals,
relative strength, valuation attractiveness, and sector strength
to identify stocks likely to appreciate over 3-6 months.
"""

import logging
from datetime import timedelta

import numpy as np
import yfinance as yf

logger = logging.getLogger(__name__)

NSE_UNIVERSE = [
    {"symbol": "RELIANCE", "name": "Reliance Industries", "sector": "Energy"},
    {"symbol": "TCS", "name": "Tata Consultancy Services", "sector": "Technology"},
    {"symbol": "HDFCBANK", "name": "HDFC Bank", "sector": "Financial Services"},
    {"symbol": "INFY", "name": "Infosys", "sector": "Technology"},
    {"symbol": "ICICIBANK", "name": "ICICI Bank", "sector": "Financial Services"},
    {"symbol": "HINDUNILVR", "name": "Hindustan Unilever", "sector": "Consumer Defensive"},
    {"symbol": "SBIN", "name": "State Bank of India", "sector": "Financial Services"},
    {"symbol": "BHARTIARTL", "name": "Bharti Airtel", "sector": "Communication Services"},
    {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank", "sector": "Financial Services"},
    {"symbol": "ITC", "name": "ITC Limited", "sector": "Consumer Defensive"},
    {"symbol": "LT", "name": "Larsen & Toubro", "sector": "Industrials"},
    {"symbol": "AXISBANK", "name": "Axis Bank", "sector": "Financial Services"},
    {"symbol": "BAJFINANCE", "name": "Bajaj Finance", "sector": "Financial Services"},
    {"symbol": "ASIANPAINT", "name": "Asian Paints", "sector": "Basic Materials"},
    {"symbol": "MARUTI", "name": "Maruti Suzuki", "sector": "Consumer Cyclical"},
    {"symbol": "SUNPHARMA", "name": "Sun Pharma", "sector": "Healthcare"},
    {"symbol": "TITAN", "name": "Titan Company", "sector": "Consumer Cyclical"},
    {"symbol": "ULTRACEMCO", "name": "UltraTech Cement", "sector": "Basic Materials"},
    {"symbol": "NESTLEIND", "name": "Nestle India", "sector": "Consumer Defensive"},
    {"symbol": "WIPRO", "name": "Wipro", "sector": "Technology"},
    {"symbol": "HCLTECH", "name": "HCL Technologies", "sector": "Technology"},
    {"symbol": "POWERGRID", "name": "Power Grid Corp", "sector": "Utilities"},
    {"symbol": "NTPC", "name": "NTPC Limited", "sector": "Utilities"},
    {"symbol": "ONGC", "name": "Oil & Natural Gas Corp", "sector": "Energy"},
    {"symbol": "TATAMOTORS", "name": "Tata Motors", "sector": "Consumer Cyclical"},
    {"symbol": "ADANIENT", "name": "Adani Enterprises", "sector": "Industrials"},
    {"symbol": "ADANIPORTS", "name": "Adani Ports", "sector": "Industrials"},
    {"symbol": "M&M", "name": "Mahindra & Mahindra", "sector": "Consumer Cyclical"},
    {"symbol": "BAJAJFINSV", "name": "Bajaj Finserv", "sector": "Financial Services"},
    {"symbol": "TATASTEEL", "name": "Tata Steel", "sector": "Basic Materials"},
    {"symbol": "JSWSTEEL", "name": "JSW Steel", "sector": "Basic Materials"},
    {"symbol": "TECHM", "name": "Tech Mahindra", "sector": "Technology"},
    {"symbol": "HDFCLIFE", "name": "HDFC Life Insurance", "sector": "Financial Services"},
    {"symbol": "SBILIFE", "name": "SBI Life Insurance", "sector": "Financial Services"},
    {"symbol": "DIVISLAB", "name": "Divi's Laboratories", "sector": "Healthcare"},
    {"symbol": "DRREDDY", "name": "Dr. Reddy's Labs", "sector": "Healthcare"},
    {"symbol": "CIPLA", "name": "Cipla", "sector": "Healthcare"},
    {"symbol": "APOLLOHOSP", "name": "Apollo Hospitals", "sector": "Healthcare"},
    {"symbol": "EICHERMOT", "name": "Eicher Motors", "sector": "Consumer Cyclical"},
    {"symbol": "HEROMOTOCO", "name": "Hero MotoCorp", "sector": "Consumer Cyclical"},
    {"symbol": "BAJAJ-AUTO", "name": "Bajaj Auto", "sector": "Consumer Cyclical"},
    {"symbol": "GRASIM", "name": "Grasim Industries", "sector": "Basic Materials"},
    {"symbol": "COALINDIA", "name": "Coal India", "sector": "Energy"},
    {"symbol": "BPCL", "name": "Bharat Petroleum", "sector": "Energy"},
    {"symbol": "TRENT", "name": "Trent Limited", "sector": "Consumer Cyclical"},
    {"symbol": "ZOMATO", "name": "Zomato", "sector": "Consumer Cyclical"},
    {"symbol": "DMART", "name": "Avenue Supermarts", "sector": "Consumer Defensive"},
    {"symbol": "INDUSINDBK", "name": "IndusInd Bank", "sector": "Financial Services"},
    {"symbol": "HINDALCO", "name": "Hindalco Industries", "sector": "Basic Materials"},
    {"symbol": "VEDL", "name": "Vedanta Limited", "sector": "Basic Materials"},
    {"symbol": "PIDILITIND", "name": "Pidilite Industries", "sector": "Basic Materials"},
    {"symbol": "DABUR", "name": "Dabur India", "sector": "Consumer Defensive"},
    {"symbol": "MARICO", "name": "Marico Limited", "sector": "Consumer Defensive"},
    {"symbol": "COLPAL", "name": "Colgate-Palmolive", "sector": "Consumer Defensive"},
    {"symbol": "BRITANNIA", "name": "Britannia Industries", "sector": "Consumer Defensive"},
    {"symbol": "GODREJCP", "name": "Godrej Consumer Products", "sector": "Consumer Defensive"},
    {"symbol": "SIEMENS", "name": "Siemens India", "sector": "Industrials"},
    {"symbol": "ABB", "name": "ABB India", "sector": "Industrials"},
    {"symbol": "BHEL", "name": "Bharat Heavy Electricals", "sector": "Industrials"},
    {"symbol": "BEL", "name": "Bharat Electronics", "sector": "Industrials"},
    {"symbol": "HAL", "name": "Hindustan Aeronautics", "sector": "Industrials"},
    {"symbol": "IRCTC", "name": "IRCTC", "sector": "Industrials"},
    {"symbol": "DLF", "name": "DLF Limited", "sector": "Real Estate"},
    {"symbol": "GODREJPROP", "name": "Godrej Properties", "sector": "Real Estate"},
    {"symbol": "Phoenix", "name": "Phoenix Mills", "sector": "Real Estate"},
    {"symbol": "DEEPAKNTR", "name": "Deepak Nitrite", "sector": "Basic Materials"},
    {"symbol": "ATUL", "name": "Atul Limited", "sector": "Basic Materials"},
    {"symbol": "NAVINFLUOR", "name": "Navin Fluorine", "sector": "Basic Materials"},
    {"symbol": "LALPATHLAB", "name": "Dr. Lal PathLabs", "sector": "Healthcare"},
    {"symbol": "MAXHEALTH", "name": "Max Healthcare", "sector": "Healthcare"},
    {"symbol": "MUTHOOTFIN", "name": "Muthoot Finance", "sector": "Financial Services"},
    {"symbol": "CHOLAFIN", "name": "Cholamandalam Finance", "sector": "Financial Services"},
    {"symbol": "MANAPPURAM", "name": "Manappuram Finance", "sector": "Financial Services"},
    {"symbol": "SRIRAMFIN", "name": "Shriram Finance", "sector": "Financial Services"},
    {"symbol": "POLYCAB", "name": "Polycab India", "sector": "Industrials"},
    {"symbol": "KAJARIACER", "name": "Kajaria Ceramics", "sector": "Basic Materials"},
    {"symbol": "TORNTPHARM", "name": "Torrent Pharmaceuticals", "sector": "Healthcare"},
    {"symbol": "IPCALAB", "name": "IPCA Laboratories", "sector": "Healthcare"},
    {"symbol": "PERSISTENT", "name": "Persistent Systems", "sector": "Technology"},
    {"symbol": "COFORGE", "name": "Coforge", "sector": "Technology"},
    {"symbol": "MPHASIS", "name": "Mphasis", "sector": "Technology"},
    {"symbol": "LTIM", "name": "LTIMindtree", "sector": "Technology"},
    {"symbol": "CROMPTON", "name": "Crompton Greaves CE", "sector": "Consumer Cyclical"},
    {"symbol": "VOLTAS", "name": "Voltas", "sector": "Consumer Cyclical"},
    {"symbol": "BLUESTARCO", "name": "Blue Star", "sector": "Consumer Cyclical"},
    {"symbol": "WHIRLPOOL", "name": "Whirlpool India", "sector": "Consumer Cyclical"},
    {"symbol": "SONACOMS", "name": "Sona BLW Precision", "sector": "Consumer Cyclical"},
    {"symbol": "BALKRISIND", "name": "Balkrishna Industries", "sector": "Consumer Cyclical"},
]


class FuturePredictionEngine:
    """
    Multi-factor stock prediction engine for 3-6 month horizons.

    Scoring weights:
      - Technical momentum  : 25%
      - Fundamental quality  : 20%
      - Valuation gap        : 20%
      - Relative strength    : 20%
      - Volume confirmation  : 15%
    """

    MOMENTUM_WEIGHT = 0.25
    FUNDAMENTAL_WEIGHT = 0.20
    VALUATION_WEIGHT = 0.20
    RELATIVE_STRENGTH_WEIGHT = 0.20
    VOLUME_WEIGHT = 0.15

    @staticmethod
    def _safe_float(val, default=0.0):
        if val is None:
            return default
        try:
            return float(val)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _fetch_data(symbol, period="1y"):
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            hist = ticker.history(period=period)
            if hist.empty or len(hist) < 50:
                return None, None
            info = ticker.info or {}
            return hist, info
        except Exception as e:
            logger.warning("Data fetch failed for %s: %s", symbol, e)
            return None, None

    @staticmethod
    def _sma(prices, window):
        if len(prices) < window:
            return np.nan
        return float(np.mean(prices[-window:]))

    @staticmethod
    def _ema(prices, span):
        if len(prices) < span:
            return np.nan
        arr = np.array(prices, dtype=float)
        alpha = 2 / (span + 1)
        ema = arr[0]
        for val in arr[1:]:
            ema = alpha * val + (1 - alpha) * ema
        return float(ema)

    @staticmethod
    def _rsi(prices, period=14):
        if len(prices) < period + 1:
            return 50.0
        deltas = np.diff(prices[-(period + 1):])
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = float(np.mean(gains))
        avg_loss = float(np.mean(losses))
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return float(100 - (100 / (1 + rs)))

    @staticmethod
    def _macd_signal(prices):
        if len(prices) < 35:
            return 0.0
        arr = np.array(prices, dtype=float)
        def _ema_arr(data, span):
            alpha = 2 / (span + 1)
            out = [data[0]]
            for v in data[1:]:
                out.append(alpha * v + (1 - alpha) * out[-1])
            return out
        ema12 = _ema_arr(arr, 12)
        ema26 = _ema_arr(arr, 26)
        macd_line = [a - b for a, b in zip(ema12, ema26)]
        signal_line = _ema_arr(macd_line, 9)
        return float(macd_line[-1] - signal_line[-1])

    @staticmethod
    def _momentum_score(prices):
        if len(prices) < 60:
            return 50.0
        ret_1m = (prices[-1] / prices[-22] - 1) if len(prices) >= 22 else 0
        ret_3m = (prices[-1] / prices[-66] - 1) if len(prices) >= 66 else 0
        ret_6m = (prices[-1] / prices[-132] - 1) if len(prices) >= 132 else 0
        score = 50
        score += ret_1m * 100
        score += ret_3m * 60
        score += ret_6m * 40
        sma20 = float(np.mean(prices[-20:]))
        sma50 = float(np.mean(prices[-50:]))
        if prices[-1] > sma20 > sma50:
            score += 8
        elif prices[-1] < sma20 < sma50:
            score -= 8
        return max(0, min(100, score))

    @staticmethod
    def _volume_confirmation(hist):
        if len(hist) < 50:
            return 50.0
        vols = hist["Volume"].values
        avg_vol_20 = float(np.mean(vols[-20:]))
        avg_vol_50 = float(np.mean(vols[-50:]))
        if avg_vol_50 == 0:
            return 50.0
        vol_ratio = avg_vol_20 / avg_vol_50
        closes = hist["Close"].values
        recent_up = closes[-1] > closes[-5]
        score = 50
        if vol_ratio > 1.3 and recent_up:
            score = 75
        elif vol_ratio > 1.1 and recent_up:
            score = 65
        elif vol_ratio > 1.3 and not recent_up:
            score = 30
        elif vol_ratio < 0.7:
            score = 40
        return float(max(0, min(100, score)))

    @staticmethod
    def _valuation_score(info, current_price):
        score = 50
        high_52w = FuturePredictionEngine._safe_float(info.get("fiftyTwoWeekHigh"), 0)
        low_52w = FuturePredictionEngine._safe_float(info.get("fiftyTwoWeekLow"), 0)
        if high_52w > 0 and low_52w > 0:
            range_pos = (current_price - low_52w) / (high_52w - low_52w) if high_52w != low_52w else 0.5
            if range_pos < 0.3:
                score += 20
            elif range_pos < 0.5:
                score += 10
            elif range_pos > 0.85:
                score -= 15
            elif range_pos > 0.7:
                score -= 5
        pe = FuturePredictionEngine._safe_float(info.get("trailingPE"), 0)
        sector = info.get("sector", "")
        sector_pe_ranges = {
            "Technology": (20, 35),
            "Financial Services": (10, 20),
            "Consumer Defensive": (25, 45),
            "Consumer Cyclical": (15, 30),
            "Healthcare": (20, 40),
            "Energy": (8, 15),
            "Basic Materials": (10, 25),
            "Industrials": (15, 30),
            "Utilities": (10, 20),
        }
        if pe > 0 and sector in sector_pe_ranges:
            low, high = sector_pe_ranges[sector]
            if pe < low:
                score += 10
            elif pe < (low + high) / 2:
                score += 5
            elif pe > high * 1.5:
                score -= 10
        pb = FuturePredictionEngine._safe_float(info.get("priceToBook"), 0)
        if 0 < pb < 1.5:
            score += 5
        elif pb > 10:
            score -= 5
        return float(max(0, min(100, score)))

    @staticmethod
    def _fundamental_score(info):
        score = 50
        roe = FuturePredictionEngine._safe_float(info.get("returnOnEquity"), 0)
        if roe:
            roe_pct = roe * 100 if roe < 1 else roe
            if roe_pct > 20:
                score += 15
            elif roe_pct > 12:
                score += 8
            elif roe_pct < 5:
                score -= 10
        profit_margin = FuturePredictionEngine._safe_float(info.get("profitMargins"), 0)
        if profit_margin:
            pm = profit_margin * 100 if abs(profit_margin) < 1 else profit_margin
            if pm > 20:
                score += 10
            elif pm > 10:
                score += 5
            elif pm < 0:
                score -= 15
        de = FuturePredictionEngine._safe_float(info.get("debtToEquity"), 0)
        if de > 0:
            if de < 30:
                score += 5
            elif de > 150:
                score -= 10
        revenue_growth = FuturePredictionEngine._safe_float(info.get("revenueGrowth"), 0)
        rg = revenue_growth * 100 if abs(revenue_growth) < 5 else revenue_growth
        if rg > 20:
            score += 10
        elif rg > 10:
            score += 5
        elif rg < -10:
            score -= 10
        return float(max(0, min(100, score)))

    @staticmethod
    def _relative_strength_score(prices, benchmark_prices=None):
        if len(prices) < 66:
            return 50.0
        stock_ret_3m = (prices[-1] / prices[-66] - 1) * 100
        if benchmark_prices is None or len(benchmark_prices) < 66:
            market_avg = 8.0
        else:
            market_avg = (benchmark_prices[-1] / benchmark_prices[-66] - 1) * 100
        rs = stock_ret_3m - market_avg
        score = 50 + rs * 2
        return float(max(0, min(100, score)))

    @staticmethod
    def _price_targets(prices, info, current_price):
        if len(prices) < 60:
            return {}
        recent_3m = prices[-66:] if len(prices) >= 66 else prices
        recent_6m = prices[-132:] if len(prices) >= 132 else prices
        n_3m = len(recent_3m)
        x_3m = np.arange(n_3m).reshape(-1, 1)
        y_3m = np.array(recent_3m, dtype=float)
        x_mean_3m = x_3m.mean()
        y_mean_3m = y_3m.mean()
        ss_xy_3m = float(np.sum((x_3m.flatten() - x_mean_3m) * (y_3m - y_mean_3m)))
        ss_xx_3m = float(np.sum((x_3m.flatten() - x_mean_3m) ** 2))
        if ss_xx_3m > 0:
            slope_3m = ss_xy_3m / ss_xx_3m
        else:
            slope_3m = 0
        intercept_3m = y_mean_3m - slope_3m * x_mean_3m
        base_3m = slope_3m * (n_3m + 66) + intercept_3m
        n_6m = len(recent_6m)
        x_6m = np.arange(n_6m).reshape(-1, 1)
        y_6m = np.array(recent_6m, dtype=float)
        x_mean_6m = x_6m.mean()
        y_mean_6m = y_6m.mean()
        ss_xy_6m = float(np.sum((x_6m.flatten() - x_mean_6m) * (y_6m - y_mean_6m)))
        ss_xx_6m = float(np.sum((x_6m.flatten() - x_mean_6m) ** 2))
        if ss_xx_6m > 0:
            slope_6m = ss_xy_6m / ss_xx_6m
        else:
            slope_6m = 0
        intercept_6m = y_mean_6m - slope_6m * x_mean_6m
        base_6m = slope_6m * (n_6m + 132) + intercept_6m
        volatility = float(np.std(np.diff(prices[-20:]) / prices[-20:-1])) if len(prices) > 20 else 0.02
        vol_adj_3m = current_price * volatility * np.sqrt(66)
        vol_adj_6m = current_price * volatility * np.sqrt(132)
        high_52w = FuturePredictionEngine._safe_float(info.get("fiftyTwoWeekHigh"), current_price * 1.2)
        low_52w = FuturePredictionEngine._safe_float(info.get("fiftyTwoWeekLow"), current_price * 0.8)
        target_3m = base_3m + 0.3 * vol_adj_3m
        target_6m = base_6m + 0.4 * vol_adj_6m
        if target_3m > high_52w * 1.15:
            target_3m = high_52w * 1.05
        if target_3m < low_52w * 0.85:
            target_3m = low_52w * 0.95
        if target_6m > high_52w * 1.30:
            target_6m = high_52w * 1.10
        if target_6m < low_52w * 0.80:
            target_6m = low_52w * 0.90
        return {
            "target_3m": round(float(target_3m), 2),
            "target_6m": round(float(target_6m), 2),
            "return_3m_pct": round(((target_3m / current_price) - 1) * 100, 2) if current_price else 0,
            "return_6m_pct": round(((target_6m / current_price) - 1) * 100, 2) if current_price else 0,
        }

    @classmethod
    def analyze_stock(cls, stock_info, nifty_prices=None):
        symbol = stock_info["symbol"]
        hist, info = cls._fetch_data(symbol)
        if hist is None or hist.empty or len(hist) < 50:
            return None
        prices = hist["Close"].values.tolist()
        current_price = prices[-1]
        momentum = cls._momentum_score(prices)
        fundamental = cls._fundamental_score(info)
        valuation = cls._valuation_score(info, current_price)
        relative = cls._relative_strength_score(prices, nifty_prices)
        volume = cls._volume_confirmation(hist)
        composite = (
            cls.MOMENTUM_WEIGHT * momentum
            + cls.FUNDAMENTAL_WEIGHT * fundamental
            + cls.VALUATION_WEIGHT * valuation
            + cls.RELATIVE_STRENGTH_WEIGHT * relative
            + cls.VOLUME_WEIGHT * volume
        )
        targets = cls._price_targets(prices, info, current_price)
        if composite >= 70:
            signal = "STRONG_BUY"
        elif composite >= 60:
            signal = "BUY"
        elif composite >= 45:
            signal = "HOLD"
        elif composite >= 35:
            signal = "SELL"
        else:
            signal = "STRONG_SELL"
        rsi = cls._rsi(prices)
        macd_val = cls._macd_signal(prices)
        sma20 = cls._sma(prices, 20)
        sma50 = cls._sma(prices, 50)
        sma200 = cls._sma(prices, 200)
        pe = cls._safe_float(info.get("trailingPE"), 0)
        roe = cls._safe_float(info.get("returnOnEquity"), 0)
        if roe > 1:
            roe *= 100
        high_52w = cls._safe_float(info.get("fiftyTwoWeekHigh"), 0)
        low_52w = cls._safe_float(info.get("fiftyTwoWeekLow"), 0)
        reasons = []
        if momentum >= 65:
            reasons.append("Strong price momentum across multiple timeframes")
        elif momentum >= 55:
            reasons.append("Positive momentum trend")
        elif momentum < 35:
            reasons.append("Weak or negative momentum")
        if fundamental >= 60:
            reasons.append("Solid fundamentals with good profitability and growth")
        elif fundamental >= 50:
            reasons.append("Average fundamental profile")
        elif fundamental < 40:
            reasons.append("Weak fundamentals or high leverage")
        if valuation >= 60:
            reasons.append("Attractively valued relative to peers and history")
        elif valuation < 40:
            reasons.append("Premium valuation limits near-term upside")
        if relative >= 60:
            reasons.append("Outperforming the broader market")
        elif relative < 40:
            reasons.append("Underperforming the broader market")
        if volume >= 60:
            reasons.append("Volume confirms the price trend")
        if rsi < 35:
            reasons.append("RSI in oversold zone — potential bounce")
        elif rsi > 75:
            reasons.append("RSI in overbought zone — caution warranted")
        if targets.get("return_3m_pct", 0) > 15:
            reasons.append(
                f"Projected ~{targets['return_3m_pct']:.0f}% upside in 3 months"
            )
        elif targets.get("return_3m_pct", 0) > 8:
            reasons.append(
                f"Projected ~{targets['return_3m_pct']:.0f}% upside in 3 months"
            )
        if targets.get("return_6m_pct", 0) > 20:
            reasons.append(
                f"Projected ~{targets['return_6m_pct']:.0f}% upside in 6 months"
            )
        return {
            "symbol": symbol,
            "name": stock_info.get("name", symbol),
            "sector": stock_info.get("sector", info.get("sector", "Unknown")),
            "current_price": round(float(current_price), 2),
            "high_52w": round(high_52w, 2) if high_52w else None,
            "low_52w": round(low_52w, 2) if low_52w else None,
            "pe_ratio": round(pe, 2) if pe else None,
            "roe": round(roe, 2) if roe else None,
            "composite_score": round(composite, 1),
            "momentum_score": round(momentum, 1),
            "fundamental_score": round(fundamental, 1),
            "valuation_score": round(valuation, 1),
            "relative_strength_score": round(relative, 1),
            "volume_score": round(volume, 1),
            "signal": signal,
            "rsi": round(rsi, 1),
            "macd_positive": macd_val > 0,
            "above_sma20": current_price > sma20 if not np.isnan(sma20) else None,
            "above_sma50": current_price > sma50 if not np.isnan(sma50) else None,
            "above_sma200": current_price > sma200 if not np.isnan(sma200) else None,
            "target_3m": targets.get("target_3m"),
            "target_6m": targets.get("target_6m"),
            "return_3m_pct": targets.get("return_3m_pct", 0),
            "return_6m_pct": targets.get("return_6m_pct", 0),
            "reasons": reasons,
        }


def get_top_recommendations(min_score=55, max_results=30, sector_filter=None):
    """
    Scan the full NSE universe and return the best 3-6 month picks.
    """
    try:
        nifty = yf.Ticker("^NSEI")
        nifty_hist = nifty.history(period="1y")
        nifty_prices = nifty_hist["Close"].values.tolist() if not nifty_hist.empty else None
    except Exception:
        nifty_prices = None

    results = []
    for stock in NSE_UNIVERSE:
        if sector_filter and stock["sector"] != sector_filter:
            continue
        try:
            analysis = FuturePredictionEngine.analyze_stock(stock, nifty_prices)
            if analysis and analysis["composite_score"] >= min_score:
                results.append(analysis)
        except Exception as e:
            logger.warning("Analysis failed for %s: %s", stock["symbol"], e)
            continue

    results.sort(key=lambda x: x["composite_score"], reverse=True)
    return results[:max_results]


def get_single_stock_forecast(symbol):
    """
    Detailed forecast for a single stock.
    """
    symbol = symbol.upper().strip()
    stock_info = next(
        (s for s in NSE_UNIVERSE if s["symbol"] == symbol),
        {"symbol": symbol, "name": symbol, "sector": "Unknown"},
    )
    try:
        nifty = yf.Ticker("^NSEI")
        nifty_hist = nifty.history(period="1y")
        nifty_prices = nifty_hist["Close"].values.tolist() if not nifty_hist.empty else None
    except Exception:
        nifty_prices = None
    return FuturePredictionEngine.analyze_stock(stock_info, nifty_prices)
