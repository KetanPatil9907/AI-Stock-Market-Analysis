"""
Allocation engine and SIP calculator for the Money Planner.

All calculations are EDUCATIONAL approximations and should NOT be
taken as financial advice.
"""

from decimal import Decimal


# ======================================================================
# ALLOCATION PROFILES
# ======================================================================
# Each profile maps a risk level to allocation percentages.
# Values must add up to 100.

ALLOCATION_PROFILES = {
    "CONSERVATIVE": {
        "equity": Decimal("30"),
        "debt": Decimal("50"),
        "gold": Decimal("10"),
        "cash": Decimal("10"),
        "description": (
            "Capital preservation focus. Suitable for retirees or "
            "investors with very low risk appetite."
        ),
        "expected_return_pct": Decimal("7"),
    },
    "MODERATE_CONSERVATIVE": {
        "equity": Decimal("45"),
        "debt": Decimal("35"),
        "gold": Decimal("12"),
        "cash": Decimal("8"),
        "description": (
            "Balanced approach with a lean towards safety. Good for "
            "medium-term goals (3\u20135 years)."
        ),
        "expected_return_pct": Decimal("8.5"),
    },
    "MODERATE": {
        "equity": Decimal("60"),
        "debt": Decimal("25"),
        "gold": Decimal("10"),
        "cash": Decimal("5"),
        "description": (
            "Growth-oriented with moderate risk. Ideal for goals "
            "5\u201310 years away."
        ),
        "expected_return_pct": Decimal("10"),
    },
    "MODERATE_AGGRESSIVE": {
        "equity": Decimal("75"),
        "debt": Decimal("12"),
        "gold": Decimal("8"),
        "cash": Decimal("5"),
        "description": (
            "Aggressive growth with higher volatility. Best for "
            "long-term goals (10+ years)."
        ),
        "expected_return_pct": Decimal("11.5"),
    },
    "AGGRESSIVE": {
        "equity": Decimal("85"),
        "debt": Decimal("5"),
        "gold": Decimal("5"),
        "cash": Decimal("5"),
        "description": (
            "Maximum growth potential. Only for investors with high "
            "risk tolerance and long horizon (12+ years)."
        ),
        "expected_return_pct": Decimal("13"),
    },
}


# ======================================================================
# SIP SUB-ALLOCATION RULES
# ======================================================================
# Maps equity_pct to a list of SIP sub-categories with their share
# of the equity allocation.

SIP_SUB_ALLOCATIONS = {
    "high_equity": [  # equity >= 70
        {"category": "Nifty 50 Index Fund", "share": Decimal("30")},
        {"category": "Nifty Next 50 Fund", "share": Decimal("15")},
        {"category": "Flexi Cap Fund", "share": Decimal("20")},
        {"category": "Mid Cap Fund", "share": Decimal("15")},
        {"category": "Small Cap Fund", "share": Decimal("10")},
        {"category": "International Fund", "share": Decimal("10")},
    ],
    "moderate_equity": [  # 50 <= equity < 70
        {"category": "Nifty 50 Index Fund", "share": Decimal("35")},
        {"category": "Flexi Cap Fund", "share": Decimal("25")},
        {"category": "Mid Cap Fund", "share": Decimal("15")},
        {"category": "ELSS (Tax Saver)", "share": Decimal("15")},
        {"category": "International Fund", "share": Decimal("10")},
    ],
    "low_equity": [  # equity < 50
        {"category": "Nifty 50 Index Fund", "share": Decimal("40")},
        {"category": "Flexi Cap Fund", "share": Decimal("30")},
        {"category": "ELSS (Tax Saver)", "share": Decimal("30")},
    ],
    "debt": [
        {"category": "Corporate Bond Fund", "share": Decimal("35")},
        {"category": "Short Duration Fund", "share": Decimal("25")},
        {"category": "Gilt Fund", "share": Decimal("20")},
        {"category": "Liquid Fund", "share": Decimal("20")},
    ],
    "gold": [
        {"category": "Gold ETF / SGB", "share": Decimal("100")},
    ],
    "cash": [
        {"category": "Liquid Fund / Savings", "share": Decimal("100")},
    ],
}


# ======================================================================
# RISK QUESTIONNAIRE SCORING
# ======================================================================
# Each answer option maps to a score (0\u20134).

RISK_QUESTIONS = [
    {
        "id": "age_group",
        "question": "What is your age group?",
        "options": [
            {"label": "Below 25", "score": 4},
            {"label": "25\u201335", "score": 3},
            {"label": "36\u201345", "score": 2},
            {"label": "46\u201355", "score": 1},
            {"label": "Above 55", "score": 0},
        ],
    },
    {
        "id": "income_stability",
        "question": "How stable is your income?",
        "options": [
            {"label": "Very stable (government / PSU / MNC)", "score": 4},
            {"label": "Stable (large private company)", "score": 3},
            {"label": "Moderate (freelance / small business)", "score": 2},
            {"label": "Variable (commission / gig work)", "score": 1},
            {"label": "Unpredictable / no regular income", "score": 0},
        ],
    },
    {
        "id": "investment_horizon",
        "question": "When do you need the money you are investing?",
        "options": [
            {"label": "More than 10 years", "score": 4},
            {"label": "7\u201310 years", "score": 3},
            {"label": "3\u20137 years", "score": 2},
            {"label": "1\u20133 years", "score": 1},
            {"label": "Less than 1 year", "score": 0},
        ],
    },
    {
        "id": "loss_tolerance",
        "question": "If your \u20b91,00,000 investment dropped to \u20b980,000 in a month, what would you do?",
        "options": [
            {"label": "Buy more \u2014 it is a discount", "score": 4},
            {"label": "Hold and wait for recovery", "score": 3},
            {"label": "Feel anxious but stay invested", "score": 2},
            {"label": "Sell part to reduce risk", "score": 1},
            {"label": "Sell everything immediately", "score": 0},
        ],
    },
    {
        "id": "financial_dependents",
        "question": "How many people depend on your income?",
        "options": [
            {"label": "None (single, no dependents)", "score": 4},
            {"label": "1\u20132 dependents with dual income", "score": 3},
            {"label": "1\u20132 dependents with single income", "score": 2},
            {"label": "3+ dependents with dual income", "score": 1},
            {"label": "3+ dependents with single income", "score": 0},
        ],
    },
    {
        "id": "emergency_fund_status",
        "question": "Do you have an emergency fund covering 6+ months of expenses?",
        "options": [
            {"label": "Yes, 12+ months", "score": 4},
            {"label": "Yes, 6\u201312 months", "score": 3},
            {"label": "Partial (3\u20136 months)", "score": 2},
            {"label": "Minimal (1\u20133 months)", "score": 1},
            {"label": "No emergency fund", "score": 0},
        ],
    },
    {
        "id": "investment_experience",
        "question": "What is your experience with market-linked investments?",
        "options": [
            {"label": "Expert (actively trade / manage portfolio)", "score": 4},
            {"label": "Experienced (3+ years in MFs/stocks)", "score": 3},
            {"label": "Intermediate (1\u20133 years)", "score": 2},
            {"label": "Beginner (started recently)", "score": 1},
            {"label": "No experience", "score": 0},
        ],
    },
    {
        "id": "primary_goal",
        "question": "What is your primary investment goal?",
        "options": [
            {"label": "Aggressive wealth creation", "score": 4},
            {"label": "Long-term growth (retirement / child future)", "score": 3},
            {"label": "Balanced growth and safety", "score": 2},
            {"label": "Regular income with low risk", "score": 1},
            {"label": "Pure capital protection", "score": 0},
        ],
    },
]


def calculate_risk_score(answers):
    """
    Calculate a risk score (0\u2013100) from questionnaire answers.

    Parameters
    ----------
    answers : dict
        Mapping of question_id -> selected option index.

    Returns
    -------
    int
        Risk score between 0 and 100.
    """
    total = 0
    max_possible = len(RISK_QUESTIONS) * 4

    for q in RISK_QUESTIONS:
        idx = answers.get(q["id"])
        if idx is not None and 0 <= idx < len(q["options"]):
            total += q["options"][idx]["score"]

    return round((total / max_possible) * 100)


def risk_score_to_level(score):
    """Map a 0\u2013100 risk score to a risk level string."""
    if score >= 80:
        return "AGGRESSIVE"
    if score >= 60:
        return "MODERATE_AGGRESSIVE"
    if score >= 40:
        return "MODERATE"
    if score >= 20:
        return "MODERATE_CONSERVATIVE"
    return "CONSERVATIVE"


# ======================================================================
# ALLOCATION ENGINE
# ======================================================================


def get_allocation_profile(risk_level):
    """Return the allocation profile dict for a given risk level."""
    return ALLOCATION_PROFILES.get(
        risk_level,
        ALLOCATION_PROFILES["MODERATE"],
    )


def build_sip_breakdown(equity_pct, debt_pct, gold_pct, cash_pct, total_sip):
    """
    Build a detailed SIP breakdown across sub-categories.

    Returns a list of dicts:
        [{"category": ..., "allocation_pct": ..., "monthly_amount": ...}, ...]
    """
    entries = []

    equity_amount = total_sip * (equity_pct / Decimal("100"))
    debt_amount = total_sip * (debt_pct / Decimal("100"))
    gold_amount = total_sip * (gold_pct / Decimal("100"))
    cash_amount = total_sip * (cash_pct / Decimal("100"))

    # Equity sub-categories
    if equity_amount > 0:
        if equity_pct >= 70:
            subs = SIP_SUB_ALLOCATIONS["high_equity"]
        elif equity_pct >= 50:
            subs = SIP_SUB_ALLOCATIONS["moderate_equity"]
        else:
            subs = SIP_SUB_ALLOCATIONS["low_equity"]

        for sub in subs:
            amt = equity_amount * (sub["share"] / Decimal("100"))
            pct = equity_pct * (sub["share"] / Decimal("100"))
            entries.append({
                "category": sub["category"],
                "allocation_pct": round(pct, 2),
                "monthly_amount": round(amt, 0),
                "suggested_return_pct": Decimal("12"),
            })

    # Debt sub-categories
    if debt_amount > 0:
        for sub in SIP_SUB_ALLOCATIONS["debt"]:
            amt = debt_amount * (sub["share"] / Decimal("100"))
            pct = debt_pct * (sub["share"] / Decimal("100"))
            entries.append({
                "category": sub["category"],
                "allocation_pct": round(pct, 2),
                "monthly_amount": round(amt, 0),
                "suggested_return_pct": Decimal("7"),
            })

    # Gold
    if gold_amount > 0:
        entries.append({
            "category": "Gold ETF / SGB",
            "allocation_pct": gold_pct,
            "monthly_amount": round(gold_amount, 0),
            "suggested_return_pct": Decimal("9"),
        })

    # Cash
    if cash_amount > 0:
        entries.append({
            "category": "Liquid Fund / Savings",
            "allocation_pct": cash_pct,
            "monthly_amount": round(cash_amount, 0),
            "suggested_return_pct": Decimal("5"),
        })

    return entries


# ======================================================================
# SIP CALCULATOR
# ======================================================================


def calculate_sip未来值(monthly_amount, annual_return_pct, years):
    """
    Calculate the future value of a monthly SIP.

    Uses the standard SIP formula:
    FV = P × [((1 + r)^n - 1) / r] × (1 + r)

    where P = monthly investment, r = monthly rate, n = total months.
    """
    if monthly_amount <= 0 or annual_return_pct <= 0 or years <= 0:
        return Decimal("0")

    r = annual_return_pct / Decimal("100") / Decimal("12")
    n = years * 12
    p = Decimal(str(monthly_amount))

    factor = ((1 + r) ** n - 1) / r * (1 + r)
    return (p * factor).quantize(Decimal("1"))


def calculate_lumpsum未来值(principal, annual_return_pct, years):
    """Calculate future value of a lump-sum investment."""
    if principal <= 0 or annual_return_pct <= 0 or years <= 0:
        return Decimal("0")

    r = annual_return_pct / Decimal("100")
    p = Decimal(str(principal))
    return (p * (1 + r) ** years).quantize(Decimal("1"))


def calculate_sip_for_goal(target_amount, annual_return_pct, years):
    """
    Calculate the monthly SIP needed to reach a target amount.

    Inverse of the SIP future value formula.
    """
    if target_amount <= 0 or annual_return_pct <= 0 or years <= 0:
        return Decimal("0")

    r = annual_return_pct / Decimal("100") / Decimal("12")
    n = years * 12
    t = Decimal(str(target_amount))

    factor = ((1 + r) ** n - 1) / r * (1 + r)
    return (t / factor).quantize(Decimal("1"))


def build_projection_table(monthly_sip, annual_return_pct):
    """
    Build a year-by-year projection table.

    Returns a list of dicts:
        [{"year": 1, "invested": ..., "value": ..., "returns": ...}, ...]
    """
    table = []
    total_invested = Decimal("0")
    monthly_r = annual_return_pct / Decimal("100") / Decimal("12")
    accumulated = Decimal("0")

    for year in range(1, 21):
        for _ in range(12):
            accumulated = (accumulated + Decimal(str(monthly_sip))) * (1 + monthly_r)
            total_invested += Decimal(str(monthly_sip))

        value = accumulated.quantize(Decimal("1"))
        returns = (value - total_invested).quantize(Decimal("1"))

        table.append({
            "year": year,
            "invested": total_invested.quantize(Decimal("1")),
            "value": value,
            "returns": returns,
        })

    return table


# ======================================================================
# FULL PLAN GENERATOR
# ======================================================================


def generate_plan(investor_profile, goals, plan_name=""):
    """
    Generate a complete MoneyPlan based on the investor profile and goals.

    Returns a dict with all plan data ready to be saved.
    """
    risk_level = investor_profile.risk_tolerance
    profile = get_allocation_profile(risk_level)

    equity_pct = profile["equity"]
    debt_pct = profile["debt"]
    gold_pct = profile["gold"]
    cash_pct = profile["cash"]
    expected_return = profile["expected_return_pct"]

    monthly_savings = investor_profile.monthly_savings
    if monthly_savings <= 0:
        monthly_savings = Decimal("5000")

    # Allocate savings across goals based on priority
    total_sip = monthly_savings
    goal_projections = []

    for goal in goals:
        sip_needed = calculate_sip_for_goal(
            goal.target_amount,
            expected_return,
            goal.target_years,
        )

        projected = calculate_sip未来值(
            sip_needed,
            expected_return,
            goal.target_years,
        )

        shortfall = projected - goal.target_amount

        goal_projections.append({
            "goal": goal,
            "monthly_sip_needed": sip_needed,
            "projected_amount": projected,
            "shortfall": shortfall,
        })

    # SIP breakdown
    sip_breakdown = build_sip_breakdown(
        equity_pct,
        debt_pct,
        gold_pct,
        cash_pct,
        total_sip,
    )

    # Corpus projections
    corpus_5y = calculate_sip未来值(total_sip, expected_return, 5)
    corpus_10y = calculate_sip未来值(total_sip, expected_return, 10)
    corpus_15y = calculate_sip未来值(total_sip, expected_return, 15)
    corpus_20y = calculate_sip未来值(total_sip, expected_return, 20)

    # Year-by-year projection
    projection_table = build_projection_table(total_sip, expected_return)

    return {
        "plan_name": plan_name,
        "risk_level": risk_level,
        "equity_pct": equity_pct,
        "debt_pct": debt_pct,
        "gold_pct": gold_pct,
        "cash_pct": cash_pct,
        "total_monthly_sip": total_sip,
        "expected_return_pct": expected_return,
        "sip_breakdown": sip_breakdown,
        "goal_projections": goal_projections,
        "corpus_5y": corpus_5y,
        "corpus_10y": corpus_10y,
        "corpus_15y": corpus_15y,
        "corpus_20y": corpus_20y,
        "projection_table": projection_table,
        "profile_description": profile["description"],
    }
