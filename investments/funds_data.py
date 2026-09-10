"""
Educational data about mutual funds vs fixed deposits and
different mutual fund categories.

All figures are INDICATIVE historical averages for education only.
They are NOT promises of future returns.
"""

from decimal import Decimal


# ======================================================================
# MF vs FD COMPARISON
# ======================================================================

FD_FACTORY = {
    "name": "Shop Talk",
    "icon": "shop",
}


MF_VS_FD_COMPARISON = {
    "fd": {
        "name": "Fixed Deposit (FD)",
        "icon": "bank",
        "color": "#0e9f6e",
        "return_pct": "6\u20137%",
        "risk": "Very Low (SAFE)",
        "risk_score": 10,
        "tax": "Interest taxed at your slab rate",
        "liquidity": "Locked; premature withdrawal penalty",
        "horizon": "Best for 1\u20133 years",
        "inflation_fighting": "Often less than inflation \u2014 money loses real value over time",
        "power_of_compounding": "Compounds, but low rate limits growth",
        "highlights": [
            "Guaranteed/assured returns",
            "Deposit insurance up to \u20b95 lakh (DICGC)",
            "Zero market risk",
            "Easy to open \u2014 banks, post office, NBFCs",
            "Good for emergency money",
        ],
        "limitations": [
            "Return is often below inflation after tax",
            "Lock-in period + premature withdrawal penalty",
            "Interest fully taxable at your slab",
            "No equity upside \u2014 capital grows slowly",
            "Compounding benefit is weak at ~6% p.a.",
        ],
    },
    "mutual_fund": {
        "name": "Mutual Funds",
        "icon": "graph-up",
        "color": "#155eef",
        "return_pct": "9\u201315% (equity funds)",
        "risk_score": 70,
        "risk_label": "Medium\u2013High (depends on category)",
        "tax": "LTCG \u20b91.25L exempt; above taxed at 12.5%",
        "liquidity": "High \u2014 redeem anytime (T+2/3) in most funds",
        "horizon": "3+ years (equity), 1\u20133 (debt)",
        "inflation_fighting": "Typically beats inflation over long periods",
        "power_of_compounding": "Equity compounding can grow wealth 8\u201310x in 20 years",
        "highlights": [
            "Historically beats FD returns over 5+ years",
            "Beats inflation, preserving real purchasing power",
            "Professional fund managers pick investments",
            "Easy SIP \u2014 start with \u20b9500/month, automate",
            "Diversification across many stocks/bonds",
            "Tax efficient \u2014 LTCG \u20b91.25L tax-free, only 12.5% above",
            "Liquidity \u2014 redeem anytime, no lock-in (except ELSS)",
        ],
        "limitations": [
            "Market-linked \u2014 returns not guaranteed",
            "Short-term value can fluctuate",
            "Fund expenses (TER) reduce net returns",
        ],
    },
    "comparison_points": [
        {
            "title": "Returns after 10 Years (\u20b91,00,000 invested once)",
            "fd_column": "\u20b91,79,084 (6.5% p.a.)",
            "mf_column": "\u20b93,10,585 (12% p.a.)",
            "note": "MF made \u20b91,31,501 more \u2014 73% more than FD",
        },
        {
            "title": "Monthly SIP of \u20b910,000 for 10 Years",
            "fd_column": "\u20b916.7 lakh (6.5% p.a.)",
            "mf_column": "\u20b923.2 lakh (12% p.a.)",
            "note": "MF corpus is \u20b913 lakh vs \u20b910 lakh invested",
        },
        {
            "title": "Beats Inflation (typically 5\u20136%)?",
            "fd_column": "Barely / sometimes no",
            "mf_column": "Usually yes over 5+ years",
            "note": "Money grows in REAL terms only if return > inflation",
        },
        {
            "title": "Tax on Returns",
            "fd_column": "Full interest at slab rate",
            "mf_column": "\u20b91.25L LTCG free, rest 12.5%",
            "note": "After tax, MF advantage widens further",
        },
    ],
    "takeaway": (
        "FDs win on SAFETY and guaranteed returns. Mutual funds win on "
        "growth, inflation-beating power, and tax efficiency. The smart "
        "strategy for most people: keep emergency money in FD, invest "
        "long-term goals in mutual funds."
    ),
}


# ======================================================================
# MUTUAL FUND CATEGORIES
# ======================================================================

FUND_CATEGORIES = [
    {
        "key": "LARGE_CAP",
        "name": "Large Cap Funds",
        "icon": "buildings",
        "color": "#155eef",
        "tagline": "Top 100 largest listed companies \u2014 stability + growth",
        "invests_in": "Companies like Reliance, HDFC Bank, TCS, Infosys",
        "risk": "Moderate",
        "risk_bar": 30,
        "expected_return": "10\u201312% p.a.",
        "best_horizon": "5\u20137+ years",
        "min_sip": "\u20b9100",
        "expense_ratio": "~0.5\u20131.5%",
        "who_for": "Beginners, conservative investors, core of every portfolio",
        "why_choose": (
            "Large, established companies are less volatile than smaller "
            "ones. Great starting point for first-time equity investors."
        ),
        "cons": "Lower upside than mid/small cap in bull markets",
        "examples": ["Nippon India Large Cap", "SBI Blue Chip", "UTI Nifty 50 Index"],
    },
    {
        "key": "MID_CAP",
        "name": "Mid Cap Funds",
        "icon": "graph-up-arrow",
        "color": "#0e9f6e",
        "tagline": "Companies ranked 101\u2013250 \u2014 tomorrow's large caps",
        "invests_in": "Fast-growing mid-sized businesses",
        "risk": "Moderately High",
        "risk_bar": 55,
        "expected_return": "12\u201315% p.a.",
        "best_horizon": "7\u201310+ years",
        "min_sip": "\u20b9100",
        "expense_ratio": "~0.8\u20131.8%",
        "who_for": "Investors willing to accept higher volatility for more growth",
        "why_choose": (
            "Mid-sized companies have more room to grow. They can "
            "deliver higher returns but swing more than large caps."
        ),
        "cons": "Drops harder in market corrections",
        "examples": ["HDFC Mid-Cap Opportunities", "Kotak Emerging Equity", "Axis Midcap"],
    },
    {
        "key": "SMALL_CAP",
        "name": "Small Cap Funds",
        "icon": "lightning-charge",
        "color": "#f59e0b",
        "tagline": "Companies ranked 251+ \u2014 high risk, high (potential) reward",
        "invests_in": "Small, emerging businesses",
        "risk": "High",
        "risk_bar": 80,
        "expected_return": "14\u201318% p.a.",
        "best_horizon": "10+ years",
        "min_sip": "\u20b9100",
        "expense_ratio": "~1\u20132.5%",
        "who_for": "Aggressive long-term investors who can ignore volatility",
        "why_choose": (
            "The biggest multi-baggers come from the small-cap space. "
            "But these funds can fall 30\u201350% in bad years."
        ),
        "cons": "Extreme volatility, needs long horizon + emotional discipline",
        "examples": ["SBI Small Cap", "Nippon India Small Cap", "HDFC Small Cap"],
    },
    {
        "key": "FLEXI_CAP",
        "name": "Flexi Cap Funds",
        "icon": "sliders",
        "color": "#6d5dfc",
        "tagline": "One fund. Any market cap. Manager decides the mix.",
        "invests_in": "All market caps \u2014 large, mid, small, combined",
        "risk": "Moderate\u2013High",
        "risk_bar": 45,
        "expected_return": "11\u201314% p.a.",
        "best_horizon": "5\u20137+ years",
        "min_sip": "\u20b9100",
        "expense_ratio": "~0.7\u20131.7%",
        "who_for": "Investors who want diversification in a single fund",
        "why_choose": (
            "The fund manager shifts allocation as markets change \u2014 "
            "more large caps in bear markets, more small caps in bull "
            "markets. Set and forget."
        ),
        "cons": "Performance depends heavily on the manager's calls",
        "examples": ["Parag Parikh Flexi Cap", "HDFC Flexi Cap", "Quant Flexi Cap"],
    },
    {
        "key": "MULTI_CAP",
        "name": "Multi Cap Funds",
        "icon": "pie-chart",
        "color": "#0e7490",
        "tagline": "Mandatory allocation across large, mid, and small caps",
        "invests_in": "At least 25% each in large, mid, and small caps",
        "risk": "Moderate\u2013High",
        "risk_bar": 50,
        "expected_return": "12\u201315% p.a.",
        "best_horizon": "7+ years",
        "min_sip": "\u20b9100",
        "expense_ratio": "~0.8\u20131.8%",
        "who_for": "Investors who want all market caps without choosing",
        "why_choose": (
            "SEBI mandates broad diversification, so no single market "
            "cap dominates. Balanced exposure across the equity market."
        ),
        "cons": "May lag in rallies when one segment outperforms",
        "examples": ["Kotak Multi Cap", "Mahindra Manulife Multi Cap", "Quant Multi Cap"],
    },
    {
        "key": "ELSS",
        "name": "ELSS (Tax Saver) Funds",
        "icon": "shield-check",
        "color": "#166534",
        "tagline": "Equity with tax savings \u2014 Section 80C up to \u20b91.5 lakh",
        "invests_in": "Diversified equity (similar to flexi/multi cap)",
        "risk": "Moderate\u2013High",
        "risk_bar": 50,
        "expected_return": "11\u201314% p.a.",
        "best_horizon": "3 years min lock-in, best 7+ years",
        "min_sip": "\u20b9500",
        "expense_ratio": "~0.8\u20132%",
        "who_for": "Salaried people who want to save tax while investing in equity",
        "why_choose": (
            "Save up to \u20b946,800 in tax (30% slab) on \u20b91.5 lakh "
            "invested, WITH equity growth. Only mutual fund with tax "
            "benefit under 80C."
        ),
        "cons": "3-year lock-in period \u2014 money is stuck",
        "examples": ["SBI Long Term Equity Fund", "Axis ELSS", "Quant ELSS Tax Saver"],
    },
    {
        "key": "INDEX",
        "name": "Index Funds / ETFs",
        "icon": "list-ol",
        "color": "#334155",
        "tagline": "Buy the whole index (Nifty 50, Sensex) at near-zero cost",
        "invests_in": "Mirrors a stock index automatically",
        "risk": "Following the market",
        "risk_bar": 35,
        "expected_return": "Market return (10\u201313% long term)",
        "best_horizon": "5\u20137+ years",
        "min_sip": "\u20b9100",
        "expense_ratio": "Very low ~0.05\u20130.4%",
        "who_for": "Low-cost investors, beginners, Buffett-style 'buy the market' fans",
        "why_choose": (
            "Most active managers fail to beat the index long term. "
            "Index funds give you the market's return at almost zero cost."
        ),
        "cons": "No downside protection \u2014 falls with the market",
        "examples": ["UTI Nifty 50 Index", "HDFC Nifty 50 Index", "Nippon India ETF Nifty BeES"],
    },
    {
        "key": "SECTORAL",
        "name": "Sectoral / Thematic Funds",
        "icon": "fc-bank",
        "color": "#be123c",
        "tagline": "Single sector bets \u2014 IT, Pharma, Banking, Infra, etc.",
        "invests_in": "One industry (e.g. only IT stocks or only pharma stocks)",
        "risk": "Very High",
        "risk_bar": 90,
        "expected_return": "Wide range \u2014 8\u201320% p.a. depending on sector cycle",
        "best_horizon": "10+ years and only with knowledge",
        "min_sip": "\u20b9500",
        "expense_ratio": "~1\u20132%",
        "who_for": "Experienced investors with sector conviction (NOT beginners)",
        "why_choose": (
            "If you strongly believe a sector will outperform. High "
            "reward if right, big drawdowns if the sector falls out of favor."
        ),
        "cons": "Aggressive concentration \u2014 can lag badly for years",
        "examples": ["ICICI Prudential IT", "SBI Healthcare", "Nippon India Banking & Financial"],
    },
    {
        "key": "INTERNATIONAL",
        "name": "International / Global Funds",
        "icon": "globe2",
        "color": "#0891b2",
        "tagline": "Invest in US, S&P 500, Nasdaq, and global markets",
        "invests_in": "Foreign stocks like Apple, Microsoft, Amazon",
        "risk": "Moderate\u2013High + currency risk",
        "risk_bar": 45,
        "expected_return": "9\u201312% p.a. (USD)",
        "best_horizon": "7+ years",
        "min_sip": "\u20b9500",
        "expense_ratio": "~0.5\u20131.5%",
        "who_for": "Investors wanting global diversification away from India",
        "why_choose": (
            "Diversify across countries \u2014 if Indian markets underperform, "
            "US/global exposure can cushion it. Rupee depreciation also helps."
        ),
        "cons": "Currency swings can hurt returns, no tax-beat advantage",
        "examples": ["Motilal Oswal S&P 500 Index", "Navi US Total Stock Market", "JM Tax Advantage"],
    },
    {
        "key": "DEBT",
        "name": "Debt / Bond Funds",
        "icon": "file-earmark-text",
        "color": "#0e9f6e",
        "tagline": "Bonds instead of stocks \u2014 FD-like safety with better liquidity",
        "invests_in": "Corporate bonds, government securities, T-bills",
        "risk": "Low",
        "risk_bar": 15,
        "expected_return": "6\u20138% p.a.",
        "best_horizon": "1\u20133 years",
        "min_sip": "\u20b9500",
        "expense_ratio": "~0.2\u20131%",
        "who_for": "Conservative investors, short-term goals, retirement corpus",
        "why_choose": (
            "Better than FD post-tax for some investors. No lock-in, "
            "redeem anytime. Reduces overall portfolio risk when mixed "
            "with equity."
        ),
        "cons": "Not guaranteed; bond prices can dip slightly",
        "examples": ["HDFC Corporate Bond", "ICICI Prudential Liquid", "Franklin India Short Term"],
    },
    {
        "key": "HYBRID",
        "name": "Hybrid / Balanced Funds",
        "icon": "balance-scale",
        "color": "#7c2d12",
        "tagline": "Automatic equity + debt blended into one fund",
        "invests_in": "Mix of stocks and bonds (e.g. 65% equity + 35% debt)",
        "risk": "Moderate",
        "risk_bar": 35,
        "expected_return": "8\u201311% p.a.",
        "best_horizon": "3\u20135+ years",
        "min_sip": "\u20b9100",
        "expense_ratio": "~0.6\u20131.5%",
        "who_for": "One-fund investors, moderate risk takers",
        "why_choose": (
            "One fund gives you balance \u2014 equity for growth, debt "
            "for stability. Suitable for conservative-to-moderate investors."
        ),
        "cons": "Equity portion still volatile short term",
        "examples": ["HDFC Balanced Advantage", "SBI Conservative Hybrid", "ICICI Equity & Debt"],
    },
]

FUND_CATEGORY_MAP = {f["key"]: f for f in FUND_CATEGORIES}

RISK_TO_FUNDS = {
    "CONSERVATIVE": ["DEBT", "HYBRID", "INDEX", "LARGE_CAP"],
    "MODERATE_CONSERVATIVE": ["DEBT", "INDEX", "LARGE_CAP", "HYBRID"],
    "MODERATE": ["LARGE_CAP", "FLEXI_CAP", "INDEX", "MID_CAP", "HYBRID"],
    "MODERATE_AGGRESSIVE": ["LARGE_CAP", "FLEXI_CAP", "MULTI_CAP", "MID_CAP", "ELSS", "INTERNATIONAL"],
    "AGGRESSIVE": ["FLEXI_CAP", "MULTI_CAP", "MID_CAP", "SMALL_CAP", "ELSS", "SECTORAL", "INTERNATIONAL"],
}


# ======================================================================
# COMPARISON ENGINE
# ======================================================================


def get_fund_category(key):
    """Return the fund category dict for a key, or None."""
    return FUND_CATEGORY_MAP.get(key)


def compare_funds(selected_keys):
    """
    Compare selected fund categories.

    Returns dict with ranked list and insights.
    """
    selected = [get_fund_category(k) for k in selected_keys]
    selected = [f for f in selected if f is not None]

    if not selected:
        return {
            "selected": [],
            "ranked": [],
            "insights": [],
            "best_risk_profile": None,
        }

    # Rank by risk_bar ascending (lower risk first) and return expectation
    def risk_score_of(fund):
        return fund["risk_bar"]

    # Best for conservative vs aggressive
    conservative_best = min(selected, key=lambda f: f["risk_bar"])
    aggressive_best = min(
        selected,
        key=lambda f: abs(f["risk_bar"] - 75),
    )

    insights = [
        {
            "title": "Lowest Risk Option",
            "text": (
                f"{conservative_best['name']} has the lowest risk "
                f"({conservative_best['risk_bar']}/100). Best for "
                f"safety-first investors looking to protect capital."
            ),
            "fund_key": conservative_best["key"],
        },
        {
            "title": "Best Growth Potential",
            "text": (
                f"{aggressive_best['name']} sits closest to what "
                f"aggressive long-term investors need \u2014 historically "
                f"{aggressive_best['expected_return']} p.a."
            ),
            "fund_key": aggressive_best["key"],
        },
    ]

    # Balanced recommendation
    if len(selected) > 1:
        fundamentals = [f for f in selected if f["risk_bar"] >= 30]
        if fundamentals:
            best_value = min(
                fundamentals,
                key=lambda f: f["risk_bar"],
            )
            insights.append({
                "title": "Best Balanced Pick",
                "text": (
                    f"{best_value['name']} balances risk and return "
                    f"well for a core portfolio holding."
                ),
                "fund_key": best_value["key"],
            })

    ranked = sorted(selected, key=lambda f: (-f["risk_bar"], f["name"]))

    return {
        "selected": selected,
        "ranked": ranked,
        "insights": insights,
        "conservative_best": conservative_best,
        "aggressive_best": aggressive_best,
    }


def best_fund_for_risk(risk_level):
    """Recommend fund categories for a given risk level."""
    keys = RISK_TO_FUNDS.get(
        risk_level,
        RISK_TO_FUNDS["MODERATE"],
    )
    return [get_fund_category(k) for k in keys if get_fund_category(k)]