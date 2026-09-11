from datetime import datetime
from zoneinfo import ZoneInfo

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Count
from django.shortcuts import render

from ipo.models import IPOAnalysis
from investments.models import MoneyPlan
from services.market_data_service import MarketDataService
from stocks.models import StockAnalysis

from .models import AIAnalysisLog


market_service = MarketDataService()


# Activity types -> icon + accent used in the Recent Analyses panel.
ACTIVITY_STYLES = {
    "STOCK_ANALYSIS": ("bi-graph-up-arrow", "blue"),
    "STOCK_SEARCH": ("bi-search", "blue"),
    "STOCK_COMPARISON": ("bi-arrow-left-right", "teal"),
    "IPO_ANALYSIS": ("bi-buildings", "purple"),
    "IPO_SEARCH": ("bi-building", "purple"),
    "INVESTMENT_PLAN": ("bi-piggy-bank", "green"),
    "EDUCATION_VIEW": ("bi-mortarboard", "amber"),
}

DEFAULT_ACTIVITY_STYLE = ("bi-lightning", "gray")

MARKET_CACHE_KEY = "dashboard:market_quotes"
MARKET_CACHE_TTL = 300


def _market_status():
    """Market open/closed based on actual IST time and NSE hours."""
    try:
        now_ist = datetime.now(ZoneInfo("Asia/Kolkata"))
    except Exception:
        now_ist = datetime.now()

    weekday = now_ist.weekday()
    seconds_now = (
        now_ist.hour * 3600
        + now_ist.minute * 60
        + now_ist.second
    )
    market_open = 9 * 3600 + 15 * 60
    market_close = 15 * 3600 + 30 * 60

    is_open = (
        weekday < 5
        and market_open <= seconds_now <= market_close
    )

    return is_open


def _market_snapshot():
    """Cached live index quotes. Returns None when unavailable."""
    cached = cache.get(MARKET_CACHE_KEY)

    if cached is not None:
        return cached

    try:
        data = market_service.get_index_quotes()
    except Exception:
        return None

    quote_data = {
        "quotes": data.get("indices", []),
        "as_of": data.get("as_of"),
    }

    cache.set(MARKET_CACHE_KEY, quote_data, MARKET_CACHE_TTL)

    return quote_data


@login_required
def dashboard_home(request):
    user = request.user

    # ========================================================
    # GREETING
    # ========================================================

    profile = getattr(user, "profile", None)
    display_name = (
        getattr(profile, "full_name", "")
        or user.first_name
        or user.username
    )

    hour = datetime.now(ZoneInfo("Asia/Kolkata")).hour
    if hour < 12:
        time_greeting = "Morning"
    elif hour < 17:
        time_greeting = "Afternoon"
    else:
        time_greeting = "Evening"

    # ========================================================
    # ACTIVITY LOG
    # ========================================================

    recent_activity = list(
        AIAnalysisLog.objects.filter(user=user)
        .select_related("user")
        .order_by("-created_at")[:8]
    )

    for activity in recent_activity:
        icon, color = ACTIVITY_STYLES.get(
            activity.activity_type,
            DEFAULT_ACTIVITY_STYLE,
        )
        activity.icon_class = icon
        activity.color_class = color

    activity_summary = (
        AIAnalysisLog.objects.filter(user=user)
        .values("activity_type")
        .annotate(total=Count("id"))
    )

    summary_map = {
        item["activity_type"]: item["total"]
        for item in activity_summary
    }

    # ========================================================
    # SAVED ANALYSES (real count across all analysis types)
    # ========================================================

    total_saved_analyses = (
        IPOAnalysis.objects.filter(
            user=user, is_saved=True
        ).count()
        + StockAnalysis.objects.filter(
            user=user, is_saved=True
        ).count()
        + MoneyPlan.objects.filter(
            user=user, is_saved=True
        ).count()
    )

    # ========================================================
    # MARKET SNAPSHOT (live, cached, fail-safe)
    # ========================================================

    market_data = _market_snapshot()
    market_quotes = market_data.get("quotes") if market_data else []

    if market_quotes:
        for quote in market_quotes:
            change_pct = quote.get("change_pct")
            quote["up"] = (
                change_pct is not None and change_pct >= 0
            )

    market_status_open = _market_status()

    context = {
        # Greeting
        "user_display_name": display_name,
        "time_greeting": time_greeting,

        # Financial overview (existing counts, unchanged)
        "total_stock_analyses": summary_map.get(
            "STOCK_ANALYSIS", 0
        ),
        "total_ipo_analyses": summary_map.get(
            "IPO_ANALYSIS", 0
        ),
        "total_investment_plans": summary_map.get(
            "INVESTMENT_PLAN", 0
        ),
        "total_saved_analyses": total_saved_analyses,

        # Existing recent activity (now with icon/color hints)
        "recent_activity": recent_activity,

        # Market snapshot
        "market_quotes": market_quotes,
        "market_as_of": market_data.get("as_of")
        if market_data else None,
        "market_status_open": market_status_open,
    }

    return render(
        request,
        "dashboard/home.html",
        context,
    )