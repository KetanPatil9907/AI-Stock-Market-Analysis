from decimal import Decimal

from agents.ipo_agent import IPOAgent


class IPOAnalysisService:
    """
    Coordinates IPO analysis using the educational IPO agent.
    """

    RECOMMENDATION_ORDER = {
        "STRONG_APPLY": 4,
        "APPLY": 3,
        "NEUTRAL": 2,
        "AVOID": 1,
        "INSUFFICIENT_DATA": 0,
    }

    RECOMMENDATION_LABELS = {
        "STRONG_APPLY": "Strong Apply",
        "APPLY": "Apply",
        "NEUTRAL": "Evaluate",
        "AVOID": "Avoid",
        "INSUFFICIENT_DATA": "Insufficient Data",
    }

    RECOMMENDATION_SUMMARIES = {
        "STRONG_APPLY": (
            "Strong educational score with a healthy GMP premium and demand."
        ),
        "APPLY": "Educational score supports considering an application.",
        "NEUTRAL": (
            "Mixed factors. Review the details carefully before deciding."
        ),
        "AVOID": (
            "Weak educational score or negative GMP suggests caution."
        ),
        "INSUFFICIENT_DATA": (
            "Not enough data to form a reliable view."
        ),
    }

    def __init__(self):
        self.agent = IPOAgent()

    @staticmethod
    def _to_float(value):
        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def gmp_premium_pct(self, ipo):
        """
        Returns GMP as a percentage of the maximum price band.
        For example, gmp Rs.25 on a Rs.100 price band -> 25.0.
        """
        gmp = self._to_float(ipo.gmp)
        price = self._to_float(ipo.price_band_max)

        if gmp is None or price is None or price <= 0:
            return None

        return round((gmp / price) * 100, 1)

    @staticmethod
    def _json_value(value):
        """
        Converts ORM values into JSON-safe primitives so they can be
        stored in JSON fields such as analysis_snapshot.
        """
        if isinstance(value, Decimal):
            return float(value)

        if hasattr(value, "isoformat"):
            return value.isoformat()

        return value

    @staticmethod
    def serialize_ipo(ipo):
        return {
            "company_name": ipo.company_name,
            "status": ipo.status,
            "industry": ipo.industry,
            "exchange": ipo.exchange,
            "price_band_min": IPOAnalysisService._json_value(
                ipo.price_band_min
            ),
            "price_band_max": IPOAnalysisService._json_value(
                ipo.price_band_max
            ),
            "issue_size_crore": IPOAnalysisService._json_value(
                ipo.issue_size_crore
            ),
            "lot_size": ipo.lot_size,
            "open_date": ipo.open_date.isoformat() if ipo.open_date else None,
            "close_date": ipo.close_date.isoformat() if ipo.close_date else None,
            "allotment_date": (
                ipo.allotment_date.isoformat()
                if ipo.allotment_date
                else None
            ),
            "listing_date": (
                ipo.listing_date.isoformat()
                if ipo.listing_date
                else None
            ),
            "gmp": IPOAnalysisService._json_value(ipo.gmp),
            "total_subscription": IPOAnalysisService._json_value(
                ipo.total_subscription
            ),
            "qib_subscription": IPOAnalysisService._json_value(
                ipo.qib_subscription
            ),
            "nii_subscription": IPOAnalysisService._json_value(
                ipo.nii_subscription
            ),
            "retail_subscription": IPOAnalysisService._json_value(
                ipo.retail_subscription
            ),
            "revenue_crore": IPOAnalysisService._json_value(
                ipo.revenue_crore
            ),
            "profit_crore": IPOAnalysisService._json_value(
                ipo.profit_crore
            ),
            "debt_crore": IPOAnalysisService._json_value(
                ipo.debt_crore
            ),
            "fresh_issue_crore": IPOAnalysisService._json_value(
                ipo.fresh_issue_crore
            ),
            "offer_for_sale_crore": IPOAnalysisService._json_value(
                ipo.offer_for_sale_crore
            ),
            "promoter_information": ipo.promoter_information,
            "business_summary": ipo.business_summary,
            "risk_factors": ipo.risk_factors,
            "official_source_url": ipo.official_source_url,
            "source_name": ipo.source_name,
        }

    def analyze_ipo(self, ipo):
        ipo_data = self.serialize_ipo(ipo)
        analysis = self.agent.analyze(ipo_data)
        return ipo_data, analysis

    def get_ranked_ipos(self, ipos):
        ranked_ipos = []

        for ipo in ipos:
            ipo_data = self.serialize_ipo(ipo)
            ranking = self.agent.build_ranking_analysis(ipo_data)

            ranked_ipos.append(
                {
                    "ipo": ipo,
                    "overall_score": ranking["overall_score"],
                    "classification": ranking["classification"],
                    "has_sufficient_data": (
                        ranking["classification"] != "INSUFFICIENT_DATA"
                    ),
                    "gmp_premium_pct": self.gmp_premium_pct(ipo),
                }
            )

        return sorted(
            ranked_ipos,
            key=lambda item: item["overall_score"],
            reverse=True,
        )

    def _recommendation(self, ranking, ipo_data, ipo):
        """
        Builds an apply/no-apply guidance using only transparent rules:
        GMP premium, subscription, and the educational agent's score.
        It is educational, never guaranteed, and not financial advice.
        """
        overall = ranking["overall_score"]
        gmp_premium = self.gmp_premium_pct(ipo)
        subscription = self._to_float(ipo_data.get("total_subscription"))
        price = self._to_float(ipo_data.get("price_band_max"))
        revenue = self._to_float(ipo_data.get("revenue_crore"))

        # We need at minimum a price band or some financial data
        has_price = price is not None
        has_any_signal = (
            has_price
            or gmp_premium is not None
            or subscription is not None
            or revenue is not None
        )

        if not has_any_signal:
            return "INSUFFICIENT_DATA", [
                self.RECOMMENDATION_SUMMARIES["INSUFFICIENT_DATA"],
                "No price band, GMP, subscription, or financial data is "
                "available in the stored IPO record.",
            ]

        reasons = []

        if gmp_premium is not None:
            if gmp_premium >= 15:
                reasons.append(
                    f"GMP premium is strong at +{gmp_premium:.0f}%."
                )
            elif gmp_premium >= 5:
                reasons.append(
                    f"GMP premium is moderate at +{gmp_premium:.0f}%."
                )
            elif gmp_premium >= 0:
                reasons.append(
                    f"GMP premium is modest at +{gmp_premium:.0f}%."
                )
            else:
                reasons.append(
                    "GMP is currently trading below the upper price band."
                )
        else:
            reasons.append("GMP is not available in the stored record.")

        if subscription is not None:
            if subscription >= 10:
                reasons.append(
                    f"Subscription is very strong at {subscription}x."
                )
            elif subscription >= 1:
                reasons.append(
                    f"Subscription is healthy at {subscription}x."
                )
            else:
                reasons.append(
                    f"Subscription is low at {subscription}x."
                )
        else:
            reasons.append(
                "Subscription data is not yet available in the record."
            )

        if gmp_premium is not None and gmp_premium >= 15:
            reasons.append(
                "GMP premium is well above the issue price band."
            )

        if (
            gmp_premium is not None
            and gmp_premium >= 15
            and overall >= 65
        ):
            verdict = "STRONG_APPLY"
        elif overall >= 55 and (gmp_premium is None or gmp_premium >= 5):
            verdict = "APPLY"
        elif overall < 45 or (
            gmp_premium is not None and gmp_premium < 0
        ):
            verdict = "AVOID"
        else:
            verdict = "NEUTRAL"

        reasons.insert(0, self.RECOMMENDATION_SUMMARIES[verdict])

        return verdict, reasons

    def build_recommendations(self, ipos):
        """
        Returns apply/no-apply guidance for currently applicable IPOs
        (open and upcoming), sorted from highest to lowest conviction.
        Uses a relaxed data mode so we can score IPOs even when some
        fields (like GMP or financials) are not yet populated.
        """
        recommendations = []

        for ipo in ipos:
            ipo_data = self.serialize_ipo(ipo)
            ranking = self.agent.analyze(ipo_data, require_data=False)
            verdict, reasons = self._recommendation(
                ranking,
                ipo_data,
                ipo,
            )

            recommendations.append(
                {
                    "ipo": ipo,
                    "overall_score": ranking["overall_score"],
                    "classification": ranking["classification"],
                    "has_sufficient_data": (
                        self.agent._has_enough_data(ipo_data)
                    ),
                    "gmp_premium_pct": self.gmp_premium_pct(ipo),
                    "recommendation": verdict,
                    "recommendation_label": self.RECOMMENDATION_LABELS.get(
                        verdict,
                        verdict,
                    ),
                    "recommendation_reasons": reasons,
                }
            )

        return sorted(
            recommendations,
            key=lambda item: (
                self.RECOMMENDATION_ORDER.get(
                    item["recommendation"],
                    0,
                ),
                item["overall_score"] or 0,
            ),
            reverse=True,
        )