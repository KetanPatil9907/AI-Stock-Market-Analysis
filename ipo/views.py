from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from dashboard.models import AIAnalysisLog
from services.gmp_data_service import GmpDataService

from .models import IPO, IPOAnalysis
from .services import IPOAnalysisService


@login_required
def ipo_center_view(request):
    analysis_service = IPOAnalysisService()

    # =========================================================
    # OPEN IPOs
    # =========================================================

    open_ipos = list(
        IPO.objects.filter(
            status="OPEN",
            is_active=True,
        )
    )

    # Separate Open IPOs into SME and Mainboard
    #
    # IPO Size = Lot Size × Maximum Price
    #
    # Size > ₹15,000  -> SME
    # Size <= ₹15,000 -> Mainboard

    sme_ipos = []
    mainboard_ipos = []

    for ipo in open_ipos:

        # We can classify the IPO only when both values exist
        if (
            ipo.lot_size is not None
            and ipo.price_band_max is not None
        ):
            # Calculate application size
            ipo_size = ipo.lot_size * ipo.price_band_max

            # Attach calculated size to the object
            # so it can be displayed in the template
            ipo.calculated_size = ipo_size

            # SME
            if ipo_size > 15000:
                sme_ipos.append(ipo)

            # Mainboard
            else:
                mainboard_ipos.append(ipo)

    # =========================================================
    # AI RANKING
    # =========================================================

    sme_ipos = analysis_service.get_ranked_ipos(
        sme_ipos
    )

    mainboard_ipos = analysis_service.get_ranked_ipos(
        mainboard_ipos
    )

    # Total number of Open IPOs
    open_ipo_count = (
        len(sme_ipos) + len(mainboard_ipos)
    )

    # =========================================================
    # UPCOMING IPOs
    # =========================================================

    upcoming_raw_ipos = list(
        IPO.objects.filter(
            status="UPCOMING",
            is_active=True,
        )
    )

    upcoming_ipos = analysis_service.get_ranked_ipos(
        upcoming_raw_ipos
    )

    # =========================================================
    # CLOSED IPOs
    # =========================================================

    closed_ipos = analysis_service.get_ranked_ipos(
        IPO.objects.filter(
            status="CLOSED",
            is_active=True,
        ).order_by("-close_date")
    )

    # =========================================================
    # RECENTLY LISTED IPOs
    # =========================================================

    recently_listed_ipos = analysis_service.get_ranked_ipos(
        IPO.objects.filter(
            status="LISTED",
            is_active=True,
        ).order_by("-listing_date")
    )

    # =========================================================
    # OUR IPO RECOMMENDATIONS
    # =========================================================
    # Built only for IPOs that can still be applied to.

    recommendations = analysis_service.build_recommendations(
        open_ipos + upcoming_raw_ipos
    )

    # =========================================================
    # ALL VISIBLE IPOs
    # =========================================================

    all_visible_ipos = IPO.objects.filter(
        is_active=True,
    )

    all_visible_ipos = analysis_service.get_ranked_ipos(
        all_visible_ipos
    )

    # =========================================================
    # HIGHEST RANKED IPO
    # =========================================================

    highest_ranked_ipo = next(
        (
            item
            for item in all_visible_ipos
            if item["has_sufficient_data"]
        ),
        None,
    )

    # =========================================================
    # SEND DATA TO TEMPLATE
    # =========================================================

    return render(
        request,
        "ipo/ipo_center.html",
        {
            # Open IPOs
            "sme_ipos": sme_ipos,
            "mainboard_ipos": mainboard_ipos,
            "open_ipo_count": open_ipo_count,

            # Other IPO sections
            "upcoming_ipos": upcoming_ipos,
            "closed_ipos": closed_ipos,
            "recently_listed_ipos": recently_listed_ipos,

            # Our IPO recommendations
            "recommendations": recommendations,

            # Highest ranked IPO
            "highest_ranked_ipo": highest_ranked_ipo,
        },
    )


# =============================================================
# REFRESH IPO GMP
# =============================================================

@login_required
@require_POST
def refresh_gmp_view(request):
    result = GmpDataService.sync_gmp_to_database()

    if result["updated"]:
        messages.success(
            request,
            f"GMP refreshed for {result['updated']} IPO records "
            f"({len(result['matched'])} live IPOs matched).",
        )
    else:
        messages.info(
            request,
            "No GMP updates were applied. "
            "The source may have no live data right now.",
        )

    return redirect("ipo:center")


# =============================================================
# IPO EXPLAIN - WHAT IS AN IPO
# =============================================================

@login_required
def ipo_explain_view(request):
    return render(
        request,
        "ipo/ipo_explain.html",
    )


# =============================================================
# IPO DETAIL
# =============================================================

@login_required
def ipo_detail_view(request, slug):
    ipo = get_object_or_404(
        IPO,
        slug=slug,
        is_active=True,
    )

    analysis_service = IPOAnalysisService()

    ipo_data, agent_result = analysis_service.analyze_ipo(
        ipo
    )

    # Save analysis
    analysis = IPOAnalysis.objects.create(
        user=request.user,
        ipo=ipo,

        fundamental_score=agent_result[
            "fundamental_score"
        ],

        gmp_score=agent_result[
            "gmp_score"
        ],

        subscription_score=agent_result[
            "subscription_score"
        ],

        valuation_score=agent_result[
            "valuation_score"
        ],

        risk_score=agent_result[
            "risk_score"
        ],

        overall_score=agent_result[
            "overall_score"
        ],

        classification=agent_result[
            "classification"
        ],

        assessment=agent_result[
            "assessment"
        ],

        strengths=agent_result[
            "strengths"
        ],

        weaknesses=agent_result[
            "weaknesses"
        ],

        risks=agent_result[
            "risks"
        ],

        things_to_check=agent_result[
            "things_to_check"
        ],

        analysis_snapshot=ipo_data,
    )

    # Log AI analysis activity
    AIAnalysisLog.objects.create(
        user=request.user,
        activity_type="IPO_ANALYSIS",

        title=f"IPO analysis: {ipo.company_name}",

        description=(
            f"Educational IPO score: "
            f"{analysis.overall_score}/100 "
            f"({analysis.get_classification_display()})."
        ),

        reference_id=analysis.id,
    )

    return render(
        request,
        "ipo/ipo_detail.html",
        {
            "ipo": ipo,
            "analysis": analysis,
        },
    )


# =============================================================
# SAVE IPO ANALYSIS
# =============================================================

@login_required
@require_POST
def save_ipo_analysis_view(
    request,
    analysis_id,
):
    analysis = get_object_or_404(
        IPOAnalysis,
        id=analysis_id,
        user=request.user,
    )

    if analysis.is_saved:

        messages.info(
            request,
            "This IPO analysis is already saved.",
        )

    else:

        analysis.is_saved = True

        analysis.save(
            update_fields=[
                "is_saved",
                "updated_at",
            ]
        )

        messages.success(
            request,
            f"{analysis.ipo.company_name} "
            f"IPO analysis was saved.",
        )

    return redirect(
        "ipo:saved",
        analysis_id=analysis.id,
    )


# =============================================================
# SAVED IPO ANALYSIS
# =============================================================

@login_required
def saved_ipo_analysis_view(
    request,
    analysis_id,
):
    analysis = get_object_or_404(
        IPOAnalysis,
        id=analysis_id,
        user=request.user,
    )

    return render(
        request,
        "ipo/ipo_saved.html",
        {
            "analysis": analysis,
        },
    )