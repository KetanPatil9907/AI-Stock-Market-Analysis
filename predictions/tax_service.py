from datetime import date, timedelta
from decimal import Decimal


class TaxHarvestingService:
    """Tax harvesting service for LTCG and STCG calculations (India)."""

    STCG_RATE = 20
    LTCG_RATE = 10
    LTCG_EXEMPTION = 100000
    STCG_EXEMPTION = 0

    @classmethod
    def calculate_tax(cls, gain_loss, holding_period_days, is_debt=False):
        gain_loss = Decimal(str(gain_loss))
        if gain_loss <= 0:
            return {
                "tax_type": "NONE",
                "tax_amount": Decimal("0"),
                "tax_rate": 0,
                "exemption": Decimal("0"),
                "net_taxable": Decimal("0"),
            }

        if is_debt:
            if holding_period_days <= 365:
                tax_rate = cls.STCG_RATE
                exemption = cls.STCG_EXEMPTION
                tax_type = "STCG"
            else:
                tax_rate = 20
                exemption = Decimal("0")
                tax_type = "LTCG"
        else:
            if holding_period_days <= 365:
                tax_rate = cls.STCG_RATE
                exemption = cls.STCG_EXEMPTION
                tax_type = "STCG"
            else:
                tax_rate = cls.LTCG_RATE
                exemption = Decimal(str(cls.LTCG_EXEMPTION))
                tax_type = "LTCG"

        net_taxable = max(Decimal("0"), gain_loss - exemption)
        tax_amount = (net_taxable * tax_rate / 100).quantize(Decimal("0.01"))

        return {
            "tax_type": tax_type,
            "tax_amount": tax_amount,
            "tax_rate": tax_rate,
            "exemption": exemption,
            "net_taxable": net_taxable,
        }

    @classmethod
    def analyze_portfolio_for_harvesting(cls, holdings):
        harvesting_opportunities = []
        total_potential_savings = Decimal("0")

        for holding in holdings:
            if holding.profit_loss >= 0:
                continue

            loss_amount = abs(Decimal(str(holding.profit_loss)))
            holding_period = (date.today() - holding.buy_date).days

            if holding_period > 365:
                potential_tax_saved = loss_amount * cls.LTCG_RATE / 100
                tax_type = "LTCG"
            else:
                potential_tax_saved = loss_amount * cls.STCG_RATE / 100
                tax_type = "STCG"

            harvesting_opportunities.append({
                "symbol": holding.symbol,
                "company_name": holding.company_name,
                "buy_price": holding.buy_price,
                "current_price": holding.current_price,
                "quantity": holding.quantity,
                "loss_amount": loss_amount,
                "holding_period_days": holding_period,
                "tax_type": tax_type,
                "potential_tax_saved": potential_tax_saved.quantize(Decimal("0.01")),
                "recommendation": cls._get_harvesting_recommendation(holding, loss_amount),
            })

            total_potential_savings += potential_tax_saved

        harvesting_opportunities.sort(key=lambda x: x["potential_tax_saved"], reverse=True)

        return {
            "opportunities": harvesting_opportunities,
            "total_potential_savings": total_potential_savings.quantize(Decimal("0.01")),
            "num_holdings": len(harvesting_opportunities),
        }

    @staticmethod
    def _get_harvesting_recommendation(holding, loss_amount):
        if loss_amount > 50000:
            return "HIGH PRIORITY: Significant loss available for tax harvesting"
        elif loss_amount > 20000:
            return "MEDIUM: Good opportunity to book losses for tax benefit"
        elif loss_amount > 5000:
            return "LOW: Small loss - consider if transaction costs are justified"
        else:
            return "MINIMAL: Very small loss - harvesting may not be cost-effective"

    @classmethod
    def calculate_optimal_harvesting(cls, holdings, target_tax_savings=None):
        all_opportunities = []
        for holding in holdings:
            if holding.profit_loss >= 0:
                continue

            loss_amount = abs(Decimal(str(holding.profit_loss)))
            holding_period = (date.today() - holding.buy_date).days

            if holding_period > 365:
                tax_saved = loss_amount * cls.LTCG_RATE / 100
                tax_type = "LTCG"
            else:
                tax_saved = loss_amount * cls.STCG_RATE / 100
                tax_type = "STCG"

            all_opportunities.append({
                "symbol": holding.symbol,
                "loss_amount": loss_amount,
                "tax_saved": tax_saved,
                "tax_type": tax_type,
                "holding_period": holding_period,
            })

        all_opportunities.sort(key=lambda x: x["tax_saved"], reverse=True)

        selected = []
        cumulative_savings = Decimal("0")

        for opp in all_opportunities:
            if target_tax_savings and cumulative_savings >= target_tax_savings:
                break
            selected.append(opp)
            cumulative_savings += opp["tax_saved"]

        return {
            "selected_for_harvesting": selected,
            "total_tax_savings": cumulative_savings.quantize(Decimal("0.01")),
            "total_loss_booked": sum(o["loss_amount"] for o in selected),
            "num_trades": len(selected),
        }

    @classmethod
    def generate_tax_report(cls, holdings, transactions=None):
        total_invested = Decimal("0")
        total_current = Decimal("0")
        total_gain = Decimal("0")
        total_loss = Decimal("0")
        stcg_gain = Decimal("0")
        stcg_loss = Decimal("0")
        ltcg_gain = Decimal("0")
        ltcg_loss = Decimal("0")

        for holding in holdings:
            invested = Decimal(str(holding.invested_amount))
            current = Decimal(str(holding.current_value))
            gain_loss = current - invested

            total_invested += invested
            total_current += current

            if gain_loss >= 0:
                total_gain += gain_loss
            else:
                total_loss += abs(gain_loss)

            holding_period = (date.today() - holding.buy_date).days
            if holding_period > 365:
                if gain_loss >= 0:
                    ltcg_gain += gain_loss
                else:
                    ltcg_loss += abs(gain_loss)
            else:
                if gain_loss >= 0:
                    stcg_gain += gain_loss
                else:
                    stcg_loss += abs(gain_loss)

        stcg_tax = cls.calculate_tax(stcg_gain, 100)
        ltcg_tax = cls.calculate_tax(ltcg_gain, 400)

        harvest_analysis = cls.analyze_portfolio_for_harvesting(holdings)

        return {
            "total_invested": total_invested,
            "total_current_value": total_current,
            "total_gain": total_gain,
            "total_loss": total_loss,
            "net_gain_loss": total_gain - total_loss,
            "stcg_gain": stcg_gain,
            "stcg_loss": stcg_loss,
            "ltcg_gain": ltcg_gain,
            "ltcg_loss": ltcg_loss,
            "stcg_tax_estimate": stcg_tax["tax_amount"],
            "ltcg_tax_estimate": ltcg_tax["tax_amount"],
            "total_tax_estimate": stcg_tax["tax_amount"] + ltcg_tax["tax_amount"],
            "harvesting_analysis": harvest_analysis,
            "num_holdings": len(holdings),
        }
