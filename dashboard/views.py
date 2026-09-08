from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from .models import AIAnalysisLog


@login_required
def dashboard_home(request):
    recent_activity = (
        AIAnalysisLog.objects.filter(user=request.user)
        .select_related("user")
        .order_by("-created_at")[:8]
    )

    activity_summary = (
        AIAnalysisLog.objects.filter(user=request.user)
        .values("activity_type")
        .annotate(total=Count("id"))
    )

    summary_map = {
        item["activity_type"]: item["total"]
        for item in activity_summary
    }

    context = {
        "recent_activity": recent_activity,
        "total_stock_analyses": summary_map.get("STOCK_ANALYSIS", 0),
        "total_ipo_analyses": summary_map.get("IPO_ANALYSIS", 0),
        "total_investment_plans": summary_map.get("INVESTMENT_PLAN", 0),
        "total_saved_analyses": 0,
    }

    return render(
    request,
    "dashboard/home.html",
    context,
)