import math
from datetime import timedelta

import numpy as np
import yfinance as yf


class MLPredictionService:
    """ML-based stock prediction using technical analysis and statistical models."""

    @staticmethod
    def get_historical_data(symbol, period="1y"):
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            df = ticker.history(period=period, interval="1d")
            if df.empty:
                df = yf.Ticker(symbol).history(period=period, interval="1d")
            return df
        except Exception:
            return None

    @staticmethod
    def calculate_sma(prices, window):
        if len(prices) < window:
            return None
        return np.mean(prices[-window:])

    @staticmethod
    def calculate_ema(prices, window):
        if len(prices) < window:
            return None
        multiplier = 2 / (window + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
        return ema

    @staticmethod
    def calculate_rsi(prices, period=14):
        if len(prices) < period + 1:
            return 50
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_macd(prices):
        if len(prices) < 26:
            return 0, 0, 0
        ema12 = MLPredictionService.calculate_ema(prices, 12)
        ema26 = MLPredictionService.calculate_ema(prices, 26)
        if ema12 is None or ema26 is None:
            return 0, 0, 0
        macd_line = ema12 - ema26
        signal_line = MLPredictionService.calculate_ema(
            np.array([macd_line]), 9
        ) or macd_line
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def calculate_bollinger_bands(prices, window=20, num_std=2):
        if len(prices) < window:
            return None, None, None
        sma = np.mean(prices[-window:])
        std = np.std(prices[-window:])
        upper = sma + (num_std * std)
        lower = sma - (num_std * std)
        return upper, sma, lower

    @staticmethod
    def calculate_volatility(prices, window=20):
        if len(prices) < window:
            return 0
        returns = np.diff(prices[-window:]) / prices[-window:-1]
        return np.std(returns) * np.sqrt(252) * 100

    @staticmethod
    def linear_regression_predict(prices, days_ahead=30):
        if len(prices) < 30:
            return None
        x = np.arange(len(prices))
        coeffs = np.polyfit(x, prices, 1)
        future_x = len(prices) + days_ahead
        return np.polyval(coeffs, future_x)

    @staticmethod
    def momentum_score(prices, period=20):
        if len(prices) < period:
            return 0
        current = prices[-1]
        past = prices[-period]
        return ((current - past) / past) * 100

    @staticmethod
    def predict_stock(symbol, horizon_months=12):
        df = MLPredictionService.get_historical_data(symbol, period="2y")
        if df is None or df.empty or len(df) < 30:
            return None

        close_prices = df["Close"].values
        current_price = float(close_prices[-1])

        sma_20 = MLPredictionService.calculate_sma(close_prices, 20)
        sma_50 = MLPredictionService.calculate_sma(close_prices, 50)
        sma_200 = MLPredictionService.calculate_sma(close_prices, 200)
        rsi = MLPredictionService.calculate_rsi(close_prices)
        macd_line, signal_line, histogram = MLPredictionService.calculate_macd(
            close_prices
        )
        bb_upper, bb_middle, bb_lower = MLPredictionService.calculate_bollinger_bands(
            close_prices
        )
        volatility = MLPredictionService.calculate_volatility(close_prices)
        momentum = MLPredictionService.momentum_score(close_prices)

        technical_score = 50
        if sma_20 and current_price > sma_20:
            technical_score += 5
        elif sma_20 and current_price < sma_20:
            technical_score -= 5
        if sma_50 and current_price > sma_50:
            technical_score += 5
        elif sma_50 and current_price < sma_50:
            technical_score -= 5
        if sma_200 and current_price > sma_200:
            technical_score += 10
        elif sma_200 and current_price < sma_200:
            technical_score -= 10
        if rsi < 30:
            technical_score += 15
        elif rsi > 70:
            technical_score -= 15
        elif 40 <= rsi <= 60:
            technical_score += 5
        if macd_line > signal_line:
            technical_score += 10
        else:
            technical_score -= 10
        if momentum > 0:
            technical_score += min(momentum, 10)
        else:
            technical_score += max(momentum, -10)

        technical_score = max(0, min(100, technical_score))

        predicted_1m = MLPredictionService.linear_regression_predict(close_prices, 30)
        predicted_3m = MLPredictionService.linear_regression_predict(close_prices, 90)
        predicted_6m = MLPredictionService.linear_regression_predict(close_prices, 180)
        predicted_1y = MLPredictionService.linear_regression_predict(close_prices, 365)

        trend_factor = 1 + (momentum / 100) * 0.3
        vol_factor = 1 - (volatility / 200)
        if predicted_1m:
            predicted_1m *= trend_factor * vol_factor
        if predicted_3m:
            predicted_3m *= trend_factor * vol_factor
        if predicted_6m:
            predicted_6m *= trend_factor * vol_factor
        if predicted_1y:
            predicted_1y *= trend_factor * vol_factor

        expected_return = 0
        if predicted_1y and current_price:
            expected_return = ((predicted_1y - current_price) / current_price) * 100

        if technical_score >= 70:
            signal = "STRONG_BUY"
        elif technical_score >= 55:
            signal = "BUY"
        elif technical_score >= 45:
            signal = "HOLD"
        elif technical_score >= 30:
            signal = "SELL"
        else:
            signal = "STRONG_SELL"

        confidence = min(95, max(20, technical_score * 0.8 + abs(momentum) * 0.5))

        risk_rating = "MODERATE"
        if volatility > 40:
            risk_rating = "HIGH"
        elif volatility > 25:
            risk_rating = "MODERATE_HIGH"
        elif volatility > 15:
            risk_rating = "MODERATE"
        elif volatility > 8:
            risk_rating = "MODERATE_LOW"
        else:
            risk_rating = "LOW"

        return {
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "predicted_price_1m": round(predicted_1m, 2) if predicted_1m else None,
            "predicted_price_3m": round(predicted_3m, 2) if predicted_3m else None,
            "predicted_price_6m": round(predicted_6m, 2) if predicted_6m else None,
            "predicted_price_1y": round(predicted_1y, 2) if predicted_1y else None,
            "expected_return_pct": round(expected_return, 2),
            "signal": signal,
            "confidence_score": round(confidence, 2),
            "technical_score": round(technical_score, 2),
            "risk_rating": risk_rating,
            "indicators": {
                "sma_20": round(sma_20, 2) if sma_20 else None,
                "sma_50": round(sma_50, 2) if sma_50 else None,
                "sma_200": round(sma_200, 2) if sma_200 else None,
                "rsi": round(rsi, 2),
                "macd": round(macd_line, 4),
                "macd_signal": round(signal_line, 4),
                "macd_histogram": round(histogram, 4),
                "bb_upper": round(bb_upper, 2) if bb_upper else None,
                "bb_middle": round(bb_middle, 2) if bb_middle else None,
                "bb_lower": round(bb_lower, 2) if bb_lower else None,
                "volatility": round(volatility, 2),
                "momentum": round(momentum, 2),
            },
        }
