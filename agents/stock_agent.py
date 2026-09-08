"""
StockAgent
----------
Orchestrates stock analysis: tries AIService first, falls back to a
transparent rule-based scorer (clearly labeled) if no AI key is set.
"""

import logging

from services.ai_service import AIService, AIServiceError

logger = logging.getLogger(__name__)

NOT_AVAILABLE = "Data unavailable"


class StockAgent:
    def __init__(self):
        self.ai_service = AIService()

    def analyze(self, quote: dict, fundamentals: dict) -> dict:
        combined = {**quote, **fundamentals}

        if self.ai_service.is_configured:
            try:
                result = self.ai_service.analyze_stock(combined)
                result["source"] = "ai"
                return self._clamp_scores(result)
            except AIServiceError as e:
                logger.warning("AI analysis failed, using fallback: %s", e)

        result = self._rule_based_analysis(combined)
        result["source"] = "rule_based"
        return result

    @staticmethod
    def _clamp_scores(result: dict) -> dict:
        for key in ("fundamental_score", "technical_score", "growth_score",
                    "risk_score", "overall_score"):
            val = result.get(key)
            if isinstance(val, (int, float)):
                result[key] = max(0, min(100, int(val)))
            else:
                result[key] = None
        return result

    def _rule_based_analysis(self, data: dict) -> dict:
        available = [k for k, v in data.items() if v != NOT_AVAILABLE and v is not None]
        missing = [k for k, v in data.items() if v == NOT_AVAILABLE]

        if len(available) < 4:
            return {
                "company_overview": "Insufficient data was available for this stock.",
                "fundamental_score": None,
                "technical_score": None,
                "growth_score": None,
                "risk_score": None,
                "overall_score": None,
                "strengths": [],
                "weaknesses": [],
                "opportunities": [],
                "risks": [],
                "important_factors": ["Insufficient data for a reliable assessment."],
                "conclusion": "Insufficient data for a reliable assessment.",
                "classification": "NEUTRAL",
            }

        pe = data.get("pe_ratio")
        roe = data.get("roe")
        debt = data.get("debt_to_equity")

        fundamental_score = 50
        strengths, weaknesses, risks = [], [], []

        if isinstance(pe, (int, float)):
            if 0 < pe < 25:
                fundamental_score += 10
                strengths.append("P/E ratio is within a moderate range based on available data.")
            elif pe >= 40:
                fundamental_score -= 10
                weaknesses.append("P/E ratio appears relatively high based on available data.")

        if isinstance(roe, (int, float)):
            if roe > 0.15:
                fundamental_score += 15
                strengths.append("Return on equity appears relatively strong based on available data.")
            elif roe < 0.05:
                fundamental_score -= 10
                weaknesses.append("Return on equity appears relatively low based on available data.")

        if isinstance(debt, (int, float)):
            if debt > 100:
                fundamental_score -= 10
                risks.append("Debt-to-equity appears elevated based on available data.")
            else:
                fundamental_score += 5

        fundamental_score = max(0, min(100, fundamental_score))
        overall_score = fundamental_score

        if overall_score >= 70:
            classification = "POSITIVE"
        elif overall_score >= 50:
            classification = "NEUTRAL"
        elif overall_score >= 35:
            classification = "CAUTION"
        else:
            classification = "HIGH RISK"

        return {
            "company_overview": (
                "This is a rule-based educational summary generated because no "
                "AI provider is currently configured (AI_API_KEY not set)."
            ),
            "fundamental_score": fundamental_score,
            "technical_score": None,
            "growth_score": None,
            "risk_score": None,
            "overall_score": overall_score,
            "strengths": strengths or ["No strong signals identified from available data."],
            "weaknesses": weaknesses or ["No notable weaknesses identified from available data."],
            "opportunities": ["Configure AI_API_KEY for a fuller AI-generated analysis."],
            "risks": risks or ["Risk could not be fully assessed with available fields."],
            "important_factors": [f"Fields unavailable: {', '.join(missing)}"] if missing else [],
            "conclusion": (
                "Based on the available data, this is an educational, rule-based "
                "estimate only. Requires further research."
            ),
            "classification": classification,
        }