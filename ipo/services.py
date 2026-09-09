from agents.ipo_agent import IPOAgent


class IPOAnalysisService:
    """
    Coordinates IPO analysis using the educational IPO agent.
    """

    def __init__(self):
        self.agent = IPOAgent()

    @staticmethod
    def serialize_ipo(ipo):
        return {
            "company_name": ipo.company_name,
            "status": ipo.status,
            "industry": ipo.industry,
            "exchange": ipo.exchange,
            "price_band_min": ipo.price_band_min,
            "price_band_max": ipo.price_band_max,
            "issue_size_crore": ipo.issue_size_crore,
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
            "gmp": ipo.gmp,
            "total_subscription": ipo.total_subscription,
            "qib_subscription": ipo.qib_subscription,
            "nii_subscription": ipo.nii_subscription,
            "retail_subscription": ipo.retail_subscription,
            "revenue_crore": ipo.revenue_crore,
            "profit_crore": ipo.profit_crore,
            "debt_crore": ipo.debt_crore,
            "fresh_issue_crore": ipo.fresh_issue_crore,
            "offer_for_sale_crore": ipo.offer_for_sale_crore,
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
                }
            )

        return sorted(
            ranked_ipos,
            key=lambda item: item["overall_score"],
            reverse=True,
        )