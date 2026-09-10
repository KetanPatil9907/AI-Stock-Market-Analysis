import re
from datetime import datetime, timedelta

import requests
import yfinance as yf


class SentimentAnalysisService:
    """Sentiment analysis for stocks using news and market data."""

    BULLISH_KEYWORDS = [
        "surge", "rally", "gain", "profit", "growth", "upgrade", "buy",
        "outperform", "bullish", "strong", "record high", "breakout",
        "momentum", "recovery", "expansion", "beat", "exceed", "positive",
        "optimistic", "upbeat", "boom", "soar", "jump", "climb", "rise",
    ]

    BEARISH_KEYWORDS = [
        "crash", "fall", "drop", "loss", "decline", "downgrade", "sell",
        "underperform", "bearish", "weak", "record low", "breakdown",
        "slump", "recession", "contraction", "miss", "below", "negative",
        "pessimistic", "downturn", "bust", "plunge", "dip", "sink", "tumble",
    ]

    NEUTRAL_KEYWORDS = [
        "stable", "steady", "unchanged", "flat", "sideways", "consolidation",
        "maintain", "hold", "wait", "watch", "uncertain", "mixed",
    ]

    @staticmethod
    def analyze_text_sentiment(text):
        if not text:
            return 0, "NEUTRAL"

        text_lower = text.lower()
        bullish_count = sum(1 for word in SentimentAnalysisService.BULLISH_KEYWORDS if word in text_lower)
        bearish_count = sum(1 for word in SentimentAnalysisService.BEARISH_KEYWORDS if word in text_lower)
        neutral_count = sum(1 for word in SentimentAnalysisService.NEUTRAL_KEYWORDS if word in text_lower)

        total = bullish_count + bearish_count + neutral_count
        if total == 0:
            return 0, "NEUTRAL"

        score = ((bullish_count - bearish_count) / total) * 100

        if score > 50:
            label = "VERY_BULLISH"
        elif score > 20:
            label = "BULLISH"
        elif score > -20:
            label = "NEUTRAL"
        elif score > -50:
            label = "BEARISH"
        else:
            label = "VERY_BEARISH"

        return round(score, 2), label

    @staticmethod
    def get_market_news_sentiment(symbol):
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.NS"
            params = {"range": "5d", "interval": "1d"}
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                result = data.get("chart", {}).get("result", [{}])[0]
                timestamps = result.get("timestamp", [])
                indicators = result.get("indicators", {}).get("quote", [{}])[0]
                closes = indicators.get("close", [])
                volumes = indicators.get("volume", [])

                if len(closes) >= 2 and closes[-1] and closes[-2]:
                    price_change = closes[-1] - closes[-2]
                    price_change_pct = (price_change / closes[-2]) * 100
                    volume = volumes[-1] if volumes[-1] else 0
                    avg_volume = sum(v for v in volumes if v) / max(1, len([v for v in volumes if v]))

                    sentiment_score = 0
                    if price_change_pct > 2:
                        sentiment_score += 40
                    elif price_change_pct > 0.5:
                        sentiment_score += 20
                    elif price_change_pct < -2:
                        sentiment_score -= 40
                    elif price_change_pct < -0.5:
                        sentiment_score -= 20

                    if avg_volume > 0:
                        volume_ratio = volume / avg_volume
                        if volume_ratio > 1.5 and price_change > 0:
                            sentiment_score += 20
                        elif volume_ratio > 1.5 and price_change < 0:
                            sentiment_score -= 20

                    sentiment_score = max(-100, min(100, sentiment_score))

                    if sentiment_score > 50:
                        label = "VERY_BULLISH"
                    elif sentiment_score > 20:
                        label = "BULLISH"
                    elif sentiment_score > -20:
                        label = "NEUTRAL"
                    elif sentiment_score > -50:
                        label = "BEARISH"
                    else:
                        label = "VERY_BEARISH"

                    return {
                        "score": sentiment_score,
                        "label": label,
                        "price_change": round(price_change, 2),
                        "price_change_pct": round(price_change_pct, 2),
                        "volume": volume,
                        "volume_ratio": round(volume / avg_volume, 2) if avg_volume > 0 else 1,
                        "source": "MARKET_DATA",
                    }
            return {"score": 0, "label": "NEUTRAL", "source": "UNAVAILABLE"}
        except Exception:
            return {"score": 0, "label": "NEUTRAL", "source": "ERROR"}

    @staticmethod
    def get_analyst_sentiment(symbol):
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            info = ticker.info

            target_high = info.get("targetHighPrice", 0)
            target_low = info.get("targetLowPrice", 0)
            target_mean = info.get("targetMeanPrice", 0)
            recommendation = info.get("recommendationKey", "hold")
            number_of_analysts = info.get("numberOfAnalystOpinions", 0)

            current_price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
            if not current_price or not target_mean:
                return {"score": 0, "label": "NEUTRAL", "source": "UNAVAILABLE"}

            upside = ((target_mean - current_price) / current_price) * 100

            score = 0
            if upside > 20:
                score = 60
            elif upside > 10:
                score = 40
            elif upside > 0:
                score = 20
            elif upside > -10:
                score = -20
            elif upside > -20:
                score = -40
            else:
                score = -60

            rec_map = {
                "strong_buy": 30, "buy": 20, "overweight": 10,
                "hold": 0, "underweight": -10, "sell": -20, "strong_sell": -30,
            }
            score += rec_map.get(recommendation, 0)
            score = max(-100, min(100, score))

            if score > 50:
                label = "VERY_BULLISH"
            elif score > 20:
                label = "BULLISH"
            elif score > -20:
                label = "NEUTRAL"
            elif score > -50:
                label = "BEARISH"
            else:
                label = "VERY_BEARISH"

            return {
                "score": score,
                "label": label,
                "target_high": target_high,
                "target_low": target_low,
                "target_mean": target_mean,
                "recommendation": recommendation,
                "num_analysts": number_of_analysts,
                "upside_pct": round(upside, 2),
                "source": "ANALYST",
            }
        except Exception:
            return {"score": 0, "label": "NEUTRAL", "source": "ERROR"}

    @staticmethod
    def get_comprehensive_sentiment(symbol):
        market_sentiment = SentimentAnalysisService.get_market_news_sentiment(symbol)
        analyst_sentiment = SentimentAnalysisService.get_analyst_sentiment(symbol)

        scores = [s["score"] for s in [market_sentiment, analyst_sentiment] if s["score"] != 0]
        avg_score = sum(scores) / len(scores) if scores else 0

        if avg_score > 50:
            label = "VERY_BULLISH"
        elif avg_score > 20:
            label = "BULLISH"
        elif avg_score > -20:
            label = "NEUTRAL"
        elif avg_score > -50:
            label = "BEARISH"
        else:
            label = "VERY_BEARISH"

        return {
            "overall_score": round(avg_score, 2),
            "overall_label": label,
            "market_data": market_sentiment,
            "analyst": analyst_sentiment,
        }
