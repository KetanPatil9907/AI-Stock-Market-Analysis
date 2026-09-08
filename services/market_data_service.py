"""
MarketDataService
------------------
Abstracts the external market data provider so the rest of the app never
talks to yfinance (or any API) directly. If you swap providers later,
only this file needs to change.

Currently backed by yfinance for NSE-listed stocks (symbol + ".NS").
No API key is required for yfinance, but the class is written so a
paid/official API can be dropped in later using MARKET_API_KEY.
"""

import logging
from datetime import datetime, timedelta

import yfinance as yf

logger = logging.getLogger(__name__)

NOT_AVAILABLE = "Data unavailable"

def _clean_symbol(symbol: str) -> str:
    return symbol.strip().upper().replace(" ", "")


class MarketDataServiceError(Exception):
    """Raised when the market data provider cannot be reached at all."""
    pass


class MarketDataService:
    SUFFIX = ".NS"  # NSE

    PERIOD_MAP = {
        "1D": ("1d", "5m"),
        "1W": ("5d", "15m"),
        "1M": ("1mo", "1d"),
        "6M": ("6mo", "1d"),
        "1Y": ("1y", "1wk"),
        "5Y": ("5y", "1mo"),
    }

    def _ticker(self, symbol: str):
        clean = _clean_symbol(symbol)
        return yf.Ticker(f"{clean}{self.SUFFIX}")

    def search_stock(self, query: str) -> dict:
        clean = _clean_symbol(query)
        try:
            info = self._ticker(clean).fast_info
            if info and info.get("lastPrice") is not None:
                return {"found": True, "symbol": clean}
        except Exception as e:
            logger.warning("search_stock failed for %s: %s", clean, e)
        return {"found": False, "symbol": clean}

    def get_stock_quote(self, symbol: str) -> dict:
        clean = _clean_symbol(symbol)
        try:
            t = self._ticker(clean)
            fast = t.fast_info
        except Exception as e:
            logger.error("get_stock_quote failed for %s: %s", clean, e)
            raise MarketDataServiceError(str(e))

        if not fast or fast.get("lastPrice") is None:
            return {"symbol": clean, "found": False}

        def g(key):
            val = fast.get(key)
            return val if val is not None else NOT_AVAILABLE

        return {
            "symbol": clean,
            "found": True,
            "current_price": g("lastPrice"),
            "previous_close": g("previousClose"),
            "day_high": g("dayHigh"),
            "day_low": g("dayLow"),
            "fifty_two_week_high": g("yearHigh"),
            "fifty_two_week_low": g("yearLow"),
            "volume": g("lastVolume"),
            "market_cap": g("marketCap"),
            "as_of": datetime.now().isoformat(),
        }

    def get_stock_fundamentals(self, symbol: str) -> dict:
        clean = _clean_symbol(symbol)
        try:
            info = self._ticker(clean).info or {}
        except Exception as e:
            logger.error("get_stock_fundamentals failed for %s: %s", clean, e)
            raise MarketDataServiceError(str(e))

        def g(key):
            val = info.get(key)
            return val if val not in (None, "") else NOT_AVAILABLE

        return {
            "symbol": clean,
            "company_name": g("longName"),
            "sector": g("sector"),
            "industry": g("industry"),
            "pe_ratio": g("trailingPE"),
            "eps": g("trailingEps"),
            "dividend_yield": g("dividendYield"),
            "book_value": g("bookValue"),
            "roe": g("returnOnEquity"),
            "debt_to_equity": g("debtToEquity"),
            "revenue": g("totalRevenue"),
            "profit_margin": g("profitMargins"),
            "market_cap": g("marketCap"),
        }

    def get_historical_data(self, symbol: str, period: str = "1M") -> dict:
        clean = _clean_symbol(symbol)
        yf_period, yf_interval = self.PERIOD_MAP.get(period, ("1mo", "1d"))
        try:
            t = self._ticker(clean)
            hist = t.history(period=yf_period, interval=yf_interval)
        except Exception as e:
            logger.error("get_historical_data failed for %s: %s", clean, e)
            raise MarketDataServiceError(str(e))

        if hist is None or hist.empty:
            return {"labels": [], "prices": [], "volumes": []}

        fmt = "%d %b %H:%M" if yf_interval.endswith("m") else "%d %b %Y"
        return {
            "labels": [ts.strftime(fmt) for ts in hist.index],
            "prices": [round(float(p), 2) for p in hist["Close"].tolist()],
            "volumes": [int(v) for v in hist["Volume"].tolist()],
        }