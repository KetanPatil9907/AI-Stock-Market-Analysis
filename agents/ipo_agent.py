from decimal import Decimal


class IPOAgent:
    """
    Educational IPO analysis agent.

    It evaluates only the data provided by the IPO record. It does not create
    financial figures, GMP, subscription numbers, or return predictions.
    """

    @staticmethod
    def _value(value):
        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _clamp(score):
        return max(0, min(100, int(round(score))))

    def _has_enough_data(self, ipo_data):
        important_fields = [
            "price_band_max",
            "revenue_crore",
            "profit_crore",
            "debt_crore",
            "total_subscription",
            "gmp",
        ]

        available = sum(
            1
            for field in important_fields
            if ipo_data.get(field) is not None
        )

        return available >= 3

    def _fundamental_score(self, data):
        score = 50
        revenue = self._value(data.get("revenue_crore"))
        profit = self._value(data.get("profit_crore"))
        debt = self._value(data.get("debt_crore"))

        if revenue is not None and revenue > 0:
            score += 10

        if profit is not None:
            if profit > 0:
                score += 20
            else:
                score -= 25

        if revenue is not None and revenue > 0 and profit is not None:
            profit_margin = (profit / revenue) * 100

            if profit_margin >= 15:
                score += 15
            elif profit_margin >= 8:
                score += 8
            elif profit_margin < 0:
                score -= 15

        if debt is not None:
            if revenue is not None and revenue > 0:
                debt_to_revenue = debt / revenue

                if debt_to_revenue <= 0.5:
                    score += 10
                elif debt_to_revenue > 1.5:
                    score -= 20
            elif debt > 0:
                score -= 5

        return self._clamp(score)

    def _gmp_score(self, data):
        """
        GMP is unofficial. This only measures reported GMP relative to the
        top price band for educational context; it does not predict listing.
        """
        gmp = self._value(data.get("gmp"))
        price = self._value(data.get("price_band_max"))

        if gmp is None or price is None or price <= 0:
            return 0

        percentage = (gmp / price) * 100

        if percentage >= 25:
            return 75
        if percentage >= 15:
            return 65
        if percentage >= 5:
            return 55
        if percentage >= 0:
            return 45

        return 25

    def _subscription_score(self, data):
        subscription = self._value(data.get("total_subscription"))

        if subscription is None:
            return 0

        if subscription >= 20:
            return 85
        if subscription >= 10:
            return 75
        if subscription >= 5:
            return 65
        if subscription >= 1:
            return 50

        return 30

    def _valuation_score(self, data):
        """
        Valuation cannot be calculated reliably without full financial metrics
        such as EPS, peer comparison, and offer valuation. It intentionally
        stays neutral where the data is insufficient.
        """
        price = self._value(data.get("price_band_max"))
        revenue = self._value(data.get("revenue_crore"))
        profit = self._value(data.get("profit_crore"))

        if price is None:
            return 0

        if revenue is None or profit is None:
            return 45

        if profit <= 0:
            return 30

        return 55

    def _risk_score(self, data):
        """
        Higher score means lower relative risk in this limited educational model.
        It never means risk-free.
        """
        score = 50
        revenue = self._value(data.get("revenue_crore"))
        profit = self._value(data.get("profit_crore"))
        debt = self._value(data.get("debt_crore"))
        subscription = self._value(data.get("total_subscription"))

        if profit is not None:
            if profit > 0:
                score += 15
            else:
                score -= 25

        if debt is not None and revenue is not None and revenue > 0:
            debt_to_revenue = debt / revenue

            if debt_to_revenue <= 0.5:
                score += 15
            elif debt_to_revenue > 1.5:
                score -= 25

        if subscription is not None:
            if subscription >= 1:
                score += 5
            elif subscription < 1:
                score -= 10

        if not data.get("official_source_url"):
            score -= 10

        return self._clamp(score)

    @staticmethod
    def _classification(overall_score):
        if overall_score >= 70:
            return "POSITIVE"
        if overall_score >= 50:
            return "NEUTRAL"
        if overall_score >= 30:
            return "NEEDS_MORE_RESEARCH"
        return "HIGH_RISK"

    def _strengths(self, data):
        items = []

        revenue = self._value(data.get("revenue_crore"))
        profit = self._value(data.get("profit_crore"))
        debt = self._value(data.get("debt_crore"))
        subscription = self._value(data.get("total_subscription"))

        if revenue is not None and revenue > 0:
            items.append(
                "Revenue information is available in the supplied IPO data."
            )

        if profit is not None and profit > 0:
            items.append(
                "The supplied data reports a positive profit figure."
            )

        if (
            debt is not None
            and revenue is not None
            and revenue > 0
            and debt / revenue <= 0.5
        ):
            items.append(
                "Reported debt appears relatively modest compared with reported revenue."
            )

        if subscription is not None and subscription >= 1:
            items.append(
                "Reported overall subscription is at or above one time."
            )

        if data.get("official_source_url"):
            items.append(
                "An official or primary-source link is available for further review."
            )

        if not items:
            items.append(
                "No major strength can be established confidently from the available data."
            )

        return items

    def _weaknesses(self, data):
        items = []

        profit = self._value(data.get("profit_crore"))
        revenue = self._value(data.get("revenue_crore"))
        debt = self._value(data.get("debt_crore"))
        subscription = self._value(data.get("total_subscription"))

        if profit is not None and profit <= 0:
            items.append(
                "The supplied data reports no positive profit figure."
            )

        if (
            debt is not None
            and revenue is not None
            and revenue > 0
            and debt / revenue > 1.5
        ):
            items.append(
                "Reported debt appears high relative to reported revenue."
            )

        if subscription is not None and subscription < 1:
            items.append(
                "Reported subscription is below one time, which may indicate lower demand."
            )

        if not data.get("official_source_url"):
            items.append(
                "An official offer-document or exchange link has not been provided."
            )

        if not items:
            items.append(
                "No clear weakness was detected by this limited educational model."
            )

        return items

    def _risks(self, data):
        items = [
            "IPO investments carry market risk, business risk, valuation risk, and listing-price volatility.",
            "Past company performance does not guarantee future performance.",
            "GMP is unofficial, can change quickly, and does not guarantee a listing gain.",
        ]

        if not data.get("official_source_url"):
            items.append(
                "Important information should be verified against official offer documents before any decision."
            )

        if not data.get("risk_factors"):
            items.append(
                "No detailed official risk-factor summary is currently stored in this application."
            )

        return items

    def analyze(self, ipo_data):
        if not self._has_enough_data(ipo_data):
            return {
                "fundamental_score": 0,
                "gmp_score": 0,
                "subscription_score": 0,
                "valuation_score": 0,
                "risk_score": 0,
                "overall_score": 0,
                "classification": "INSUFFICIENT_DATA",
                "assessment": (
                    "Insufficient data for a reliable IPO assessment. Review the "
                    "official offer document, financial statements, valuation, "
                    "industry conditions, and risk factors before considering any IPO."
                ),
                "strengths": [
                    "The IPO is listed in the application for educational tracking."
                ],
                "weaknesses": [
                    "Important financial, valuation, GMP, or subscription information is missing."
                ],
                "risks": [
                    "Do not treat incomplete IPO information as a basis for an investment decision."
                ],
                "things_to_check": [
                    "Official RHP/DRHP or exchange announcement.",
                    "Revenue, profit, debt, and cash-flow trends.",
                    "Peer valuation comparison.",
                    "Fresh issue versus offer for sale.",
                    "Business and industry-specific risks.",
                ],
            }

        fundamental_score = self._fundamental_score(ipo_data)
        gmp_score = self._gmp_score(ipo_data)
        subscription_score = self._subscription_score(ipo_data)
        valuation_score = self._valuation_score(ipo_data)
        risk_score = self._risk_score(ipo_data)

        score_parts = [
            (fundamental_score, 0.35),
            (risk_score, 0.25),
        ]

        if gmp_score > 0:
            score_parts.append((gmp_score, 0.10))

        if subscription_score > 0:
            score_parts.append((subscription_score, 0.15))

        if valuation_score > 0:
            score_parts.append((valuation_score, 0.15))

        total_weight = sum(weight for _, weight in score_parts)

        overall_score = self._clamp(
            sum(score * weight for score, weight in score_parts)
            / total_weight
        )

        classification = self._classification(overall_score)

        return {
            "fundamental_score": fundamental_score,
            "gmp_score": gmp_score,
            "subscription_score": subscription_score,
            "valuation_score": valuation_score,
            "risk_score": risk_score,
            "overall_score": overall_score,
            "classification": classification,
            "assessment": (
                f"Based on the available information, this IPO is classified as "
                f"{classification.replace('_', ' ')} in this educational model. "
                "This is not a recommendation to apply, avoid, buy, or sell. "
                "Investors should independently review official documents, "
                "valuation, financial performance, and personal risk tolerance."
            ),
            "strengths": self._strengths(ipo_data),
            "weaknesses": self._weaknesses(ipo_data),
            "risks": self._risks(ipo_data),
            "things_to_check": [
                "Read the official Red Herring Prospectus or exchange announcement.",
                "Understand whether proceeds are a fresh issue or offer for sale.",
                "Check revenue, profit, debt, margins, and operating cash flow.",
                "Compare valuation with listed peers where reliable data is available.",
                "Review promoter background, related-party transactions, and governance disclosures.",
                "Do not rely on GMP alone; it is unofficial and can change.",
                "Consider your investment horizon, liquidity needs, and risk tolerance.",
            ],
        }

    def build_ranking_analysis(self, ipo_data):
        """
        Reuses normal analysis for IPO Center ranking.
        No analysis is persisted here, so list ranking remains efficient.
        """
        return self.analyze(ipo_data)