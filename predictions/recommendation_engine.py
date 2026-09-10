import random

from predictions.ml_service import MLPredictionService
from predictions.sentiment_service import SentimentAnalysisService


class RecommendationEngine:
    """Risk-based stock and mutual fund recommendation engine."""

    RISK_PROFILES = {
        "CONSERVATIVE": {
            "name": "Conservative",
            "description": "Capital preservation with steady returns",
            "equity_pct": 20,
            "debt_pct": 50,
            "gold_pct": 15,
            "cash_pct": 15,
            "expected_return": 8,
            "max_risk": "LOW",
            "stock_allocation_pct": 30,
            "mf_allocation_pct": 70,
            "preferred_sectors": ["IT", "Pharma", "FMCG", "Utilities"],
            "avoid_sectors": ["Crypto", "Startups"],
            "min_market_cap": 50000,
            "max_volatility": 20,
        },
        "MODERATE_CONSERVATIVE": {
            "name": "Moderately Conservative",
            "description": "Balanced approach with focus on stability",
            "equity_pct": 35,
            "debt_pct": 40,
            "gold_pct": 15,
            "cash_pct": 10,
            "expected_return": 10,
            "max_risk": "MODERATE_LOW",
            "stock_allocation_pct": 40,
            "mf_allocation_pct": 60,
            "preferred_sectors": ["IT", "Pharma", "FMCG", "Banking", "Auto"],
            "avoid_sectors": ["Crypto"],
            "min_market_cap": 30000,
            "max_volatility": 30,
        },
        "MODERATE": {
            "name": "Moderate",
            "description": "Balanced growth with moderate risk",
            "equity_pct": 50,
            "debt_pct": 30,
            "gold_pct": 15,
            "cash_pct": 5,
            "expected_return": 12,
            "max_risk": "MODERATE",
            "stock_allocation_pct": 50,
            "mf_allocation_pct": 50,
            "preferred_sectors": ["IT", "Banking", "Auto", "Chemicals", "Infrastructure"],
            "avoid_sectors": [],
            "min_market_cap": 15000,
            "max_volatility": 40,
        },
        "MODERATE_AGGRESSIVE": {
            "name": "Moderately Aggressive",
            "description": "Growth-focused with higher risk tolerance",
            "equity_pct": 65,
            "debt_pct": 20,
            "gold_pct": 10,
            "cash_pct": 5,
            "expected_return": 14,
            "max_risk": "MODERATE_HIGH",
            "stock_allocation_pct": 60,
            "mf_allocation_pct": 40,
            "preferred_sectors": ["IT", "Banking", "Auto", "Chemicals", "Infrastructure", "Real Estate"],
            "avoid_sectors": [],
            "min_market_cap": 5000,
            "max_volatility": 50,
        },
        "AGGRESSIVE": {
            "name": "Aggressive",
            "description": "Maximum growth potential with high risk",
            "equity_pct": 80,
            "debt_pct": 10,
            "gold_pct": 5,
            "cash_pct": 5,
            "expected_return": 16,
            "max_risk": "HIGH",
            "stock_allocation_pct": 70,
            "mf_allocation_pct": 30,
            "preferred_sectors": ["IT", "Banking", "Auto", "Chemicals", "Infrastructure", "Real Estate", "Small Cap"],
            "avoid_sectors": [],
            "min_market_cap": 1000,
            "max_volatility": 100,
        },
    }

    NSE_BLUE_CHIPS = [
        {"symbol": "RELIANCE", "name": "Reliance Industries", "sector": "Oil & Gas", "market_cap": 1800000},
        {"symbol": "TCS", "name": "Tata Consultancy Services", "sector": "IT", "market_cap": 1300000},
        {"symbol": "HDFCBANK", "name": "HDFC Bank", "sector": "Banking", "market_cap": 1200000},
        {"symbol": "INFY", "name": "Infosys", "sector": "IT", "market_cap": 600000},
        {"symbol": "ICICIBANK", "name": "ICICI Bank", "sector": "Banking", "market_cap": 700000},
        {"symbol": "HINDUNILVR", "name": "Hindustan Unilever", "sector": "FMCG", "market_cap": 550000},
        {"symbol": "SBIN", "name": "State Bank of India", "sector": "Banking", "market_cap": 650000},
        {"symbol": "BHARTIARTL", "name": "Bharti Airtel", "sector": "Telecom", "market_cap": 500000},
        {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank", "sector": "Banking", "market_cap": 400000},
        {"symbol": "ITC", "name": "ITC Limited", "sector": "FMCG", "market_cap": 450000},
        {"symbol": "LT", "name": "Larsen & Toubro", "sector": "Infrastructure", "market_cap": 350000},
        {"symbol": "AXISBANK", "name": "Axis Bank", "sector": "Banking", "market_cap": 300000},
        {"symbol": "BAJFINANCE", "name": "Bajaj Finance", "sector": "NBFC", "market_cap": 280000},
        {"symbol": "MARUTI", "name": "Maruti Suzuki", "sector": "Auto", "market_cap": 250000},
        {"symbol": "SUNPHARMA", "name": "Sun Pharmaceutical", "sector": "Pharma", "market_cap": 220000},
        {"symbol": "TATAMOTORS", "name": "Tata Motors", "sector": "Auto", "market_cap": 200000},
        {"symbol": "WIPRO", "name": "Wipro", "sector": "IT", "market_cap": 180000},
        {"symbol": "HCLTECH", "name": "HCL Technologies", "sector": "IT", "market_cap": 170000},
        {"symbol": "ASIANPAINT", "name": "Asian Paints", "sector": "Consumer", "market_cap": 160000},
        {"symbol": "TITAN", "name": "Titan Company", "sector": "Consumer", "market_cap": 150000},
        {"symbol": "ADANIENT", "name": "Adani Enterprises", "sector": "Conglomerate", "market_cap": 140000},
        {"symbol": "NTPC", "name": "NTPC", "sector": "Utilities", "market_cap": 130000},
        {"symbol": "POWERGRID", "name": "Power Grid Corp", "sector": "Utilities", "market_cap": 120000},
        {"symbol": "ONGC", "name": "Oil & Natural Gas Corp", "sector": "Oil & Gas", "market_cap": 110000},
        {"symbol": "TATASTEEL", "name": "Tata Steel", "sector": "Metals", "market_cap": 100000},
    ]

    NSE_MID_CAPS = [
        {"symbol": "PIDILITIND", "name": "Pidilite Industries", "sector": "Chemicals", "market_cap": 80000},
        {"symbol": "DABUR", "name": "Dabur India", "sector": "FMCG", "market_cap": 75000},
        {"symbol": "COLPAL", "name": "Colgate-Palmolive", "sector": "FMCG", "market_cap": 70000},
        {"symbol": "BRITANNIA", "name": "Britannia Industries", "sector": "FMCG", "market_cap": 65000},
        {"symbol": "NESTLEIND", "name": "Nestle India", "sector": "FMCG", "market_cap": 60000},
        {"symbol": "INDUSINDBK", "name": "IndusInd Bank", "sector": "Banking", "market_cap": 55000},
        {"symbol": "BIOCON", "name": "Biocon", "sector": "Pharma", "market_cap": 50000},
        {"symbol": "MUTHOOTFIN", "name": "Muthoot Finance", "sector": "NBFC", "market_cap": 45000},
        {"symbol": "LALPATHLAB", "name": "Dr Lal PathLabs", "sector": "Healthcare", "market_cap": 40000},
        {"symbol": "VOLTAS", "name": "Voltas", "sector": "Consumer Durables", "market_cap": 35000},
    ]

    MUTUAL_FUNDS = [
        {"symbol": "NIFTY50", "name": "Nifty 50 Index Fund", "type": "Index", "risk": "MODERATE", "return_1y": 12, "return_3y": 14},
        {"symbol": "NIFTYNEXT50", "name": "Nifty Next 50 Index Fund", "type": "Index", "risk": "MODERATE_HIGH", "return_1y": 15, "return_3y": 16},
        {"symbol": "SENSEX", "name": "Sensex Index Fund", "type": "Index", "risk": "MODERATE", "return_1y": 11, "return_3y": 13},
        {"symbol": "FLEXICAP", "name": "Flexi Cap Fund", "type": "Equity", "risk": "MODERATE", "return_1y": 14, "return_3y": 15},
        {"symbol": "MIDCAP", "name": "Mid Cap Fund", "type": "Equity", "risk": "MODERATE_HIGH", "return_1y": 18, "return_3y": 20},
        {"symbol": "SMALLCAP", "name": "Small Cap Fund", "type": "Equity", "risk": "HIGH", "return_1y": 22, "return_3y": 25},
        {"symbol": "LARGECAP", "name": "Large Cap Fund", "type": "Equity", "risk": "MODERATE", "return_1y": 10, "return_3y": 12},
        {"symbol": "BALANCED", "name": "Balanced Advantage Fund", "type": "Hybrid", "risk": "MODERATE", "return_1y": 11, "return_3y": 12},
        {"symbol": "DEBT", "name": "Corporate Bond Fund", "type": "Debt", "risk": "LOW", "return_1y": 7, "return_3y": 7.5},
        {"symbol": "GILT", "name": "Gilt Fund", "type": "Debt", "risk": "LOW", "return_1y": 6.5, "return_3y": 7},
        {"symbol": "GOLD", "name": "Gold Fund", "type": "Commodity", "risk": "MODERATE", "return_1y": 15, "return_3y": 12},
        {"symbol": "ELSS", "name": "ELSS Tax Saver Fund", "type": "Equity", "risk": "MODERATE_HIGH", "return_1y": 16, "return_3y": 18},
        {"symbol": "NIFTYBEES", "name": "Nifty 50 ETF", "type": "ETF", "risk": "MODERATE", "return_1y": 12, "return_3y": 14},
        {"symbol": "JUNIORBEES", "name": "Nifty Next 50 ETF", "type": "ETF", "risk": "MODERATE_HIGH", "return_1y": 15, "return_3y": 16},
        {"symbol": "BANKBEES", "name": "Nifty Bank ETF", "type": "ETF", "risk": "HIGH", "return_1y": 18, "return_3y": 15},
    ]

    US_STOCKS = [
        {"symbol": "AAPL", "name": "Apple Inc", "sector": "Technology", "market_cap": 3000000},
        {"symbol": "MSFT", "name": "Microsoft", "sector": "Technology", "market_cap": 2800000},
        {"symbol": "GOOGL", "name": "Alphabet", "sector": "Technology", "market_cap": 1800000},
        {"symbol": "AMZN", "name": "Amazon", "sector": "Consumer", "market_cap": 1500000},
        {"symbol": "NVDA", "name": "NVIDIA", "sector": "Semiconductors", "market_cap": 1200000},
        {"symbol": "META", "name": "Meta Platforms", "sector": "Technology", "market_cap": 900000},
        {"symbol": "TSLA", "name": "Tesla", "sector": "Automotive", "market_cap": 800000},
        {"symbol": "JPM", "name": "JPMorgan Chase", "sector": "Banking", "market_cap": 500000},
        {"symbol": "V", "name": "Visa", "sector": "Finance", "market_cap": 500000},
        {"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "market_cap": 400000},
        {"symbol": "WMT", "name": "Walmart", "sector": "Retail", "market_cap": 400000},
        {"symbol": "PG", "name": "Procter & Gamble", "sector": "Consumer", "market_cap": 350000},
        {"symbol": "MA", "name": "Mastercard", "sector": "Finance", "market_cap": 350000},
        {"symbol": "UNH", "name": "UnitedHealth", "sector": "Healthcare", "market_cap": 300000},
        {"symbol": "HD", "name": "Home Depot", "sector": "Retail", "market_cap": 300000},
    ]

    @classmethod
    def get_recommendations(cls, risk_level, amount, market="NSE", include_stocks=True, include_mf=True):
        profile = cls.RISK_PROFILES.get(risk_level, cls.RISK_PROFILES["MODERATE"])
        recommendations = []

        if include_stocks:
            if market == "NSE":
                stocks = cls.NSE_BLUE_CHIPS + cls.NSE_MID_CAPS
            elif market == "US":
                stocks = cls.US_STOCKS
            else:
                stocks = cls.NSE_BLUE_CHIPS + cls.NSE_MID_CAPS + cls.US_STOCKS

            filtered_stocks = []
            for stock in stocks:
                if market == "NSE" and stock["market_cap"] >= profile["min_market_cap"]:
                    filtered_stocks.append(stock)
                elif market == "US":
                    filtered_stocks.append(stock)

            for stock in filtered_stocks[:15]:
                try:
                    prediction = MLPredictionService.predict_stock(stock["symbol"], horizon_months=12)
                    sentiment = SentimentAnalysisService.get_comprehensive_sentiment(stock["symbol"])

                    if prediction:
                        combined_score = (
                            prediction["technical_score"] * 0.4
                            + sentiment["overall_score"] * 0.3
                            + min(100, stock["market_cap"] / 1000) * 0.3
                        )

                        if combined_score >= 70:
                            signal = "STRONG_BUY"
                        elif combined_score >= 55:
                            signal = "BUY"
                        elif combined_score >= 45:
                            signal = "HOLD"
                        elif combined_score >= 30:
                            signal = "SELL"
                        else:
                            signal = "STRONG_SELL"

                        stock_amount = amount * (profile["stock_allocation_pct"] / 100) / max(1, len(filtered_stocks[:15]))

                        recommendations.append({
                            "symbol": stock["symbol"],
                            "company_name": stock["name"],
                            "asset_type": "EQ",
                            "sector": stock["sector"],
                            "current_price": prediction["current_price"],
                            "predicted_price_1m": prediction["predicted_price_1m"],
                            "predicted_price_3m": prediction["predicted_price_3m"],
                            "predicted_price_6m": prediction["predicted_price_6m"],
                            "predicted_price_1y": prediction["predicted_price_1y"],
                            "expected_return_pct": prediction["expected_return_pct"],
                            "signal": signal,
                            "confidence_score": round(combined_score, 2),
                            "sentiment_score": sentiment["overall_score"],
                            "technical_score": prediction["technical_score"],
                            "risk_rating": prediction["risk_rating"],
                            "suggested_amount": round(stock_amount, 2),
                            "reasoning": cls._generate_reasoning(prediction, sentiment, stock),
                        })
                except Exception:
                    continue

        if include_mf:
            risk_map = {
                "CONSERVATIVE": ["LOW", "MODERATE"],
                "MODERATE_CONSERVATIVE": ["LOW", "MODERATE"],
                "MODERATE": ["MODERATE", "MODERATE_HIGH"],
                "MODERATE_AGGRESSIVE": ["MODERATE_HIGH", "HIGH"],
                "AGGRESSIVE": ["HIGH"],
            }
            allowed_risks = risk_map.get(risk_level, ["MODERATE"])

            for fund in cls.MUTUAL_FUNDS:
                if fund["risk"] in allowed_risks or fund["type"] == "Debt":
                    mf_amount = amount * (profile["mf_allocation_pct"] / 100) / 5

                    if fund["return_3y"] > 15:
                        signal = "STRONG_BUY"
                    elif fund["return_3y"] > 12:
                        signal = "BUY"
                    elif fund["return_3y"] > 8:
                        signal = "HOLD"
                    else:
                        signal = "SELL"

                    recommendations.append({
                        "symbol": fund["symbol"],
                        "company_name": fund["name"],
                        "asset_type": "MF" if fund["type"] != "ETF" else "ETF",
                        "sector": fund["type"],
                        "current_price": 0,
                        "predicted_price_1y": 0,
                        "expected_return_pct": fund["return_3y"],
                        "signal": signal,
                        "confidence_score": min(90, 50 + fund["return_3y"]),
                        "sentiment_score": 0,
                        "technical_score": 0,
                        "risk_rating": fund["risk"],
                        "suggested_amount": round(mf_amount, 2),
                        "reasoning": f"{fund['type']} fund with {fund['return_3y']}% 3-year returns. Risk: {fund['risk']}",
                    })

        recommendations.sort(key=lambda x: x["confidence_score"], reverse=True)
        return recommendations[:20]

    @staticmethod
    def _generate_reasoning(prediction, sentiment, stock):
        reasons = []
        if prediction["technical_score"] > 60:
            reasons.append("Strong technical indicators")
        elif prediction["technical_score"] < 40:
            reasons.append("Weak technical signals")

        if sentiment["overall_score"] > 30:
            reasons.append("Positive market sentiment")
        elif sentiment["overall_score"] < -30:
            reasons.append("Negative market sentiment")

        if prediction["expected_return_pct"] > 15:
            reasons.append(f"High expected return ({prediction['expected_return_pct']}%)")
        elif prediction["expected_return_pct"] < -5:
            reasons.append(f"Negative outlook ({prediction['expected_return_pct']}%)")

        if prediction["risk_rating"] in ["LOW", "MODERATE_LOW"]:
            reasons.append("Low volatility stock")
        elif prediction["risk_rating"] in ["HIGH"]:
            reasons.append("High volatility - trade with caution")

        indicators = prediction.get("indicators", {})
        if indicators.get("rsi", 50) < 30:
            reasons.append("RSI indicates oversold condition")
        elif indicators.get("rsi", 50) > 70:
            reasons.append("RSI indicates overbought condition")

        return ". ".join(reasons) if reasons else "Based on technical and sentiment analysis"
