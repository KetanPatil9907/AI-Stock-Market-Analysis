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

    def get_dividend_history(self, symbol: str) -> dict:
        """
        Fetch dividend payment history for a stock.
        Returns the last 10 dividend payments.
        """
        clean = _clean_symbol(symbol)
        try:
            t = self._ticker(clean)
            dividends = t.dividends
        except Exception as e:
            logger.error("get_dividend_history failed for %s: %s", clean, e)
            return {"dividends": [], "total_dividends": 0, "avg_dividend": 0}

        if dividends is None or dividends.empty:
            return {"dividends": [], "total_dividends": 0, "avg_dividend": 0}

        records = []
        for date, amount in dividends.tail(10).items():
            records.append({
                "date": date.strftime("%d %b %Y"),
                "amount": round(float(amount), 2),
            })

        amounts = [float(a) for _, a in dividends.items()]
        total = round(sum(amounts), 2)
        avg = round(total / len(amounts), 2) if amounts else 0

        return {
            "dividends": list(reversed(records)),
            "total_dividends": len(records),
            "avg_dividend": avg,
        }

    def get_insider_transactions(self, symbol: str) -> dict:
        """
        Fetch insider buying/selling activity.
        Returns the last 10 insider transactions.
        """
        clean = _clean_symbol(symbol)
        try:
            t = self._ticker(clean)
            insider = t.insider_transactions
        except Exception as e:
            logger.error("get_insider_transactions failed for %s: %s", clean, e)
            return {"transactions": [], "summary": {}}

        if insider is None or insider.empty:
            return {"transactions": [], "summary": {}}

        records = []
        for _, row in insider.tail(10).iterrows():
            text = str(row.get("Text", ""))
            shares = row.get("Shares", None)
            value = row.get("Value", None)
            pos = row.get("Position", "")
            start_date = str(row.get("Start Date", ""))

            action = "UNKNOWN"
            text_lower = text.lower()
            if "purchase" in text_lower or "buy" in text_lower:
                action = "PURCHASE"
            elif "sale" in text_lower or "sell" in text_lower:
                action = "SALE"
            elif "grant" in text_lower or "option" in text_lower:
                action = "GRANT"
            elif "exercise" in text_lower:
                action = "EXERCISE"

            records.append({
                "date": start_date[:10] if start_date else "N/A",
                "insider": str(row.get("Insider", "Unknown")),
                "position": str(pos) if pos else "Unknown",
                "action": action,
                "shares": int(shares) if shares and str(shares).replace(".", "").replace("-", "").isdigit() else None,
                "value": round(float(value), 2) if value and str(value).replace(".", "").replace("-", "").isdigit() else None,
                "text": text[:100] if text else "",
            })

        purchases = sum(1 for r in records if r["action"] == "PURCHASE")
        sales = sum(1 for r in records if r["action"] == "SALE")

        if purchases > sales:
            sentiment = "NET_BUYING"
            sentiment_note = "More insider purchases than sales recently."
        elif sales > purchases:
            sentiment = "NET_SELLING"
            sentiment_note = "More insider sales than purchases recently."
        else:
            sentiment = "BALANCED"
            sentiment_note = "Insider transactions are balanced between buys and sells."

        return {
            "transactions": records,
            "summary": {
                "total_transactions": len(records),
                "purchases": purchases,
                "sales": sales,
                "sentiment": sentiment,
                "sentiment_note": sentiment_note,
            },
        }

    def get_peer_stocks(self, sector: str, industry: str, exclude_symbol: str = "") -> list:
        """
        Find peer stocks in the same sector/industry.
        Returns a list of well-known NSE stocks in the same sector.
        Falls back to sector-level peers if industry match not found.
        """
        SECTOR_PEERS = {
            "Technology": [
                {"symbol": "TCS", "name": "Tata Consultancy Services"},
                {"symbol": "INFY", "name": "Infosys"},
                {"symbol": "HCLTECH", "name": "HCL Technologies"},
                {"symbol": "WIPRO", "name": "Wipro"},
                {"symbol": "TECHM", "name": "Tech Mahindra"},
                {"symbol": "LTIM", "name": "LTIMindtree"},
                {"symbol": "PERSISTENT", "name": "Persistent Systems"},
                {"symbol": "COFORGE", "name": "Coforge"},
            ],
            "Financial Services": [
                {"symbol": "HDFCBANK", "name": "HDFC Bank"},
                {"symbol": "ICICIBANK", "name": "ICICI Bank"},
                {"symbol": "SBIN", "name": "State Bank of India"},
                {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank"},
                {"symbol": "AXISBANK", "name": "Axis Bank"},
                {"symbol": "BHARTIFIN", "name": "Bharti Airtel"},
                {"symbol": "BAJFINANCE", "name": "Bajaj Finance"},
                {"symbol": "HDFCLIFE", "name": "HDFC Life Insurance"},
            ],
            "Energy": [
                {"symbol": "RELIANCE", "name": "Reliance Industries"},
                {"symbol": "ONGC", "name": "Oil and Natural Gas Corp"},
                {"symbol": "BPCL", "name": "Bharat Petroleum"},
                {"symbol": "IOC", "name": "Indian Oil Corporation"},
                {"symbol": "NTPC", "name": "NTPC"},
                {"symbol": "POWERGRID", "name": "Power Grid Corp"},
                {"symbol": "ADANIENT", "name": "Adani Enterprises"},
                {"symbol": "TATAPOWER", "name": "Tata Power"},
            ],
            "Consumer Cyclical": [
                {"symbol": "TATAMOTORS", "name": "Tata Motors"},
                {"symbol": "M&M", "name": "Mahindra & Mahindra"},
                {"symbol": "MARUTI", "name": "Maruti Suzuki"},
                {"symbol": "BAJAJ-AUTO", "name": "Bajaj Auto"},
                {"symbol": "HEROMOTOCO", "name": "Hero MotoCorp"},
                {"symbol": "TVSMOTOR", "name": "TVS Motor"},
                {"symbol": "EICHERMOT", "name": "Eicher Motors"},
                {"symbol": "ASHOKLEY", "name": "Ashok Leyland"},
            ],
            "Consumer Defensive": [
                {"symbol": "HINDUNILVR", "name": "Hindustan Unilever"},
                {"symbol": "ITC", "name": "ITC"},
                {"symbol": "NESTLEIND", "name": "Nestle India"},
                {"symbol": "BRITANNIA", "name": "Britannia Industries"},
                {"symbol": "DABUR", "name": "Dabur India"},
                {"symbol": "MARICO", "name": "Marico"},
                {"symbol": "COLPAL", "name": "Colgate-Palmolive"},
                {"symbol": "EMAMILTD", "name": "Emami"},
            ],
            "Industrials": [
                {"symbol": "LT", "name": "Larsen & Toubro"},
                {"symbol": "TATASTEEL", "name": "Tata Steel"},
                {"symbol": "TORNTPHARM", "name": "Torrent Pharma"},
                {"symbol": "ADANIPORTS", "name": "Adani Ports"},
                {"symbol": "GODREJCP", "name": "Godrej Consumer"},
                {"symbol": "BEL", "name": "Bharat Electronics"},
                {"symbol": "HAL", "name": "Hindustan Aeronautics"},
                {"symbol": "SIEMENS", "name": "Siemens India"},
            ],
            "Healthcare": [
                {"symbol": "SUNPHARMA", "name": "Sun Pharma"},
                {"symbol": "DRREDDY", "name": "Dr. Reddy's Laboratories"},
                {"symbol": "CIPLA", "name": "Cipla"},
                {"symbol": "DIVISLAB", "name": "Divi's Laboratories"},
                {"symbol": "TRENT", "name": "Trent"},
                {"symbol": "APOLLOHOSP", "name": "Apollo Hospitals"},
                {"symbol": "LALPATHLAB", "name": "Dr. Lal PathLabs"},
                {"symbol": "MAXHEALTH", "name": "Max Healthcare"},
            ],
            "Basic Materials": [
                {"symbol": "TATASTEEL", "name": "Tata Steel"},
                {"symbol": "JSWSTEEL", "name": "JSW Steel"},
                {"symbol": "HINDALCO", "name": "Hindalco Industries"},
                {"symbol": "VEDL", "name": "Vedanta"},
                {"symbol": "ULTRACEMCO", "name": "UltraTech Cement"},
                {"symbol": "ACC", "name": "ACC"},
                {"symbol": "AMBUJACEM", "name": "Ambuja Cements"},
                {"symbol": "GRASIM", "name": "Grasim Industries"},
            ],
            "Communication Services": [
                {"symbol": "BHARTIARTL", "name": "Bharti Airtel"},
                {"symbol": "IDEA", "name": "Vodafone Idea"},
                {"symbol": "INDUSTOWER", "name": "Indus Towers"},
            ],
            "Real Estate": [
                {"symbol": "DLF", "name": "DLF"},
                {"symbol": "GODREJPROP", "name": "Godrej Properties"},
                {"symbol": "OBEROIRLTY", "name": "Oberoi Realty"},
                {"symbol": "PRESTIGE", "name": "Prestige Estates"},
                {"symbol": "BRIGADE", "name": "Brigade Enterprises"},
            ],
            "Utilities": [
                {"symbol": "NTPC", "name": "NTPC"},
                {"symbol": "POWERGRID", "name": "Power Grid Corp"},
                {"symbol": "TATAPOWER", "name": "Tata Power"},
                {"symbol": "ADANIPOWER", "name": "Adani Power"},
                {"symbol": "NHPC", "name": "NHPC"},
                {"symbol": "SJVN", "name": "SJVN"},
            ],
        }

        clean_exclude = _clean_symbol(exclude_symbol) if exclude_symbol else ""

        sector_key = None
        for key in SECTOR_PEERS:
            if sector and key.lower() in sector.lower():
                sector_key = key
                break

        if not sector_key:
            sector_key = "Technology"

        peers = SECTOR_PEERS.get(sector_key, [])

        filtered = [
            p for p in peers
            if p["symbol"] != clean_exclude
        ]

        return filtered[:6]