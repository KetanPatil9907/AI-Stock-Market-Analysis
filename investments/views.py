import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from dashboard.models import AIAnalysisLog

from .forms import (
    FundComparisonForm,
    InvestmentGoalForm,
    InvestorProfileForm,
    LumpsumCalculatorForm,
    RiskQuestionnaireForm,
    SIPCalculatorForm,
)
from .funds_data import (
    FUND_CATEGORIES,
    MF_VS_FD_COMPARISON,
    best_fund_for_risk,
    compare_funds,
)
from .models import (
    GoalProjection,
    InvestmentGoal,
    InvestorProfile,
    MoneyPlan,
    SIPEntry,
)
from .services import (
    RISK_QUESTIONS,
    calculate_lumpsum未来值,
    calculate_risk_score,
    calculate_sip未来值,
    generate_plan,
    risk_score_to_level,
)


# ======================================================================
# HOME
# ======================================================================


@login_required
def home(request):
    """Money Planner landing page with overview and quick actions."""
    profile = InvestorProfile.objects.filter(
        user=request.user,
    ).first()

    goals = InvestmentGoal.objects.filter(
        user=request.user,
    )

    plans = MoneyPlan.objects.filter(
        user=request.user,
        is_saved=True,
    )

    return render(
        request,
        "investments/home.html",
        {
            "profile": profile,
            "goals": goals,
            "saved_plans": plans,
        },
    )


# ======================================================================
# RISK ASSESSMENT
# ======================================================================


@login_required
def risk_assessment(request):
    """Questionnaire to determine the user's risk profile."""

    if request.method == "POST":
        form = RiskQuestionnaireForm(
            request.POST,
            questions=RISK_QUESTIONS,
        )

        if form.is_valid():
            answers = {
                q: form.cleaned_data[q]
                for q in form.cleaned_data
            }

            score = calculate_risk_score(answers)
            level = risk_score_to_level(score)

            # Create or update investor profile
            profile, _ = InvestorProfile.objects.get_or_create(
                user=request.user,
            )
            profile.risk_score = score
            profile.risk_tolerance = level
            profile.save(update_fields=[
                "risk_score",
                "risk_tolerance",
                "updated_at",
            ])

            AIAnalysisLog.objects.create(
                user=request.user,
                activity_type="INVESTMENT_PLAN",
                title="Risk Assessment Completed",
                description=(
                    f"Risk score: {score}/100 "
                    f"({profile.get_risk_tolerance_display()})."
                ),
            )

            messages.success(
                request,
                f"Your risk profile is: {profile.get_risk_tolerance_display()} "
                f"(Score: {score}/100)",
            )

            return redirect("investments:profile_setup")
    else:
        form = RiskQuestionnaireForm(questions=RISK_QUESTIONS)

    # Build selected_answers dict from POST data for radio pre-selection
    selected_answers = {}
    if request.method == "POST":
        for q in RISK_QUESTIONS:
            val = request.POST.get(q["id"])
            if val is not None:
                try:
                    selected_answers[q["id"]] = int(val)
                except (ValueError, TypeError):
                    pass

    return render(
        request,
        "investments/risk_assessment.html",
        {
            "form": form,
            "questions": RISK_QUESTIONS,
            "selected_answers": selected_answers,
        },
    )


# ======================================================================
# PROFILE SETUP
# ======================================================================


@login_required
def profile_setup(request):
    """Create or update the investor financial profile."""
    profile, _ = InvestorProfile.objects.get_or_create(
        user=request.user,
    )

    if request.method == "POST":
        form = InvestorProfileForm(request.POST, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, "Profile saved successfully.")
            return redirect("investments:goals")
    else:
        form = InvestorProfileForm(instance=profile)

    return render(
        request,
        "investments/profile_setup.html",
        {
            "form": form,
            "profile": profile,
        },
    )


# ======================================================================
# GOALS MANAGEMENT
# ======================================================================


@login_required
def goals(request):
    """List and manage investment goals."""
    goals_qs = InvestmentGoal.objects.filter(
        user=request.user,
    )

    if request.method == "POST":
        form = InvestmentGoalForm(request.POST)

        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, "Goal added.")
            return redirect("investments:goals")
    else:
        form = InvestmentGoalForm()

    return render(
        request,
        "investments/goals.html",
        {
            "goals": goals_qs,
            "form": form,
        },
    )


@login_required
def goal_edit(request, goal_id):
    """Edit an existing goal."""
    goal = get_object_or_404(
        InvestmentGoal,
        id=goal_id,
        user=request.user,
    )

    if request.method == "POST":
        form = InvestmentGoalForm(request.POST, instance=goal)

        if form.is_valid():
            form.save()
            messages.success(request, "Goal updated.")
            return redirect("investments:goals")
    else:
        form = InvestmentGoalForm(instance=goal)

    return render(
        request,
        "investments/goal_edit.html",
        {
            "form": form,
            "goal": goal,
        },
    )


@login_required
@require_POST
def goal_delete(request, goal_id):
    """Delete a goal."""
    goal = get_object_or_404(
        InvestmentGoal,
        id=goal_id,
        user=request.user,
    )
    goal.delete()
    messages.success(request, "Goal deleted.")
    return redirect("investments:goals")


# ======================================================================
# GENERATE PLAN
# ======================================================================


@login_required
def generate_plan_view(request):
    """Generate a money plan based on profile and goals."""
    profile = InvestorProfile.objects.filter(
        user=request.user,
    ).first()

    if not profile:
        messages.warning(
            request,
            "Please complete your risk assessment and profile first.",
        )
        return redirect("investments:risk_assessment")

    goals = InvestmentGoal.objects.filter(
        user=request.user,
    )

    if not goals.exists():
        messages.warning(
            request,
            "Please add at least one investment goal.",
        )
        return redirect("investments:goals")

    plan_data = generate_plan(profile, goals)

    # Save plan
    plan = MoneyPlan.objects.create(
        user=request.user,
        investor_profile=profile,
        plan_name=plan_data["plan_name"],
        equity_pct=plan_data["equity_pct"],
        debt_pct=plan_data["debt_pct"],
        gold_pct=plan_data["gold_pct"],
        cash_pct=plan_data["cash_pct"],
        total_monthly_sip=plan_data["total_monthly_sip"],
        sip_returns_pct=plan_data["expected_return_pct"],
        projected_corpus_5y=plan_data["corpus_5y"],
        projected_corpus_10y=plan_data["corpus_10y"],
        projected_corpus_15y=plan_data["corpus_15y"],
        projected_corpus_20y=plan_data["corpus_20y"],
    )

    # Save SIP entries
    for entry in plan_data["sip_breakdown"]:
        SIPEntry.objects.create(
            plan=plan,
            category=entry["category"],
            allocation_pct=entry["allocation_pct"],
            monthly_amount=entry["monthly_amount"],
            suggested_return_pct=entry["suggested_return_pct"],
        )

    # Save goal projections
    for gp in plan_data["goal_projections"]:
        GoalProjection.objects.create(
            plan=plan,
            goal=gp["goal"],
            monthly_sip_needed=gp["monthly_sip_needed"],
            projected_amount=gp["projected_amount"],
            shortfall=gp["shortfall"],
        )

    AIAnalysisLog.objects.create(
        user=request.user,
        activity_type="INVESTMENT_PLAN",
        title="Money Plan Generated",
        description=(
            f"Monthly SIP: \u20b9{plan.total_monthly_sip:,.0f} | "
            f"Equity: {plan.equity_pct}% | "
            f"10y corpus: \u20b9{plan.projected_corpus_10y:,.0f}"
        ),
        reference_id=plan.id,
    )

    return redirect("investments:plan_result", plan_id=plan.id)


# ======================================================================
# PLAN RESULT
# ======================================================================


@login_required
def plan_result(request, plan_id):
    """Display the generated money plan with charts and tables."""
    plan = get_object_or_404(
        MoneyPlan,
        id=plan_id,
        user=request.user,
    )

    sip_entries = SIPEntry.objects.filter(plan=plan)
    goal_projections = GoalProjection.objects.filter(plan=plan)

    return render(
        request,
        "investments/plan_result.html",
        {
            "plan": plan,
            "sip_entries": sip_entries,
            "goal_projections": goal_projections,
        },
    )


@login_required
@require_POST
def save_plan(request, plan_id):
    """Mark a plan as saved."""
    plan = get_object_or_404(
        MoneyPlan,
        id=plan_id,
        user=request.user,
    )

    if not plan.is_saved:
        plan.is_saved = True
        plan.save(update_fields=["is_saved", "updated_at"])
        messages.success(request, "Plan saved to your collection.")
    else:
        messages.info(request, "Plan is already saved.")

    return redirect("investments:plan_result", plan_id=plan.id)


@login_required
def saved_plans(request):
    """List all saved plans."""
    plans = MoneyPlan.objects.filter(
        user=request.user,
        is_saved=True,
    )

    return render(
        request,
        "investments/saved_plans.html",
        {"plans": plans},
    )


@login_required
@require_POST
def delete_plan(request, plan_id):
    """Delete a saved plan."""
    plan = get_object_or_404(
        MoneyPlan,
        id=plan_id,
        user=request.user,
    )
    plan.delete()
    messages.success(request, "Plan deleted.")
    return redirect("investments:saved_plans")


# ======================================================================
# SIP CALCULATOR
# ======================================================================


@login_required
def sip_calculator(request):
    """Standalone SIP calculator with projections."""
    result = None

    if request.method == "POST":
        form = SIPCalculatorForm(request.POST)

        if form.is_valid():
            monthly = form.cleaned_data["monthly_amount"]
            ret = form.cleaned_data["annual_return"]
            yrs = form.cleaned_data["years"]

            future = calculate_sip未来值(monthly, ret, yrs)
            total_invested = monthly * 12 * yrs
            total_returns = future - total_invested

            # Year-by-year table
            table = []
            r = ret / 100 / 12
            acc = 0
            inv = 0

            for year in range(1, yrs + 1):
                for _ in range(12):
                    acc = (acc + monthly) * (1 + r)
                    inv += monthly

                table.append({
                    "year": year,
                    "invested": int(inv),
                    "value": int(acc),
                    "returns": int(acc - inv),
                })

            result = {
                "monthly": monthly,
                "annual_return": ret,
                "years": yrs,
                "future_value": future,
                "total_invested": int(total_invested),
                "total_returns": total_returns,
                "table": table,
            }
    else:
        form = SIPCalculatorForm()

    return render(
        request,
        "investments/sip_calculator.html",
        {
            "form": form,
            "result": result,
        },
    )


# ======================================================================
# LUMPSUM CALCULATOR
# ======================================================================


@login_required
def lumpsum_calculator(request):
    """Standalone lump-sum calculator."""
    result = None

    if request.method == "POST":
        form = LumpsumCalculatorForm(request.POST)

        if form.is_valid():
            principal = form.cleaned_data["principal"]
            ret = form.cleaned_data["annual_return"]
            yrs = form.cleaned_data["years"]

            future = calculate_lumpsum未来值(principal, ret, yrs)
            total_returns = future - principal

            result = {
                "principal": principal,
                "annual_return": ret,
                "years": yrs,
                "future_value": future,
                "total_returns": total_returns,
            }
    else:
        form = LumpsumCalculatorForm()

    return render(
        request,
        "investments/lumpsum_calculator.html",
        {
            "form": form,
            "result": result,
        },
    )


# ======================================================================
# API: CHART DATA
# ======================================================================


@login_required
def plan_chart_data(request, plan_id):
    """Return JSON data for plan projection charts."""
    plan = get_object_or_404(
        MoneyPlan,
        id=plan_id,
        user=request.user,
    )

    # Rebuild projection table
    from .services import build_projection_table

    table = build_projection_table(
        plan.total_monthly_sip,
        plan.sip_returns_pct,
    )

    # Allocation pie chart data
    allocation = {
        "labels": ["Equity", "Debt", "Gold", "Cash"],
        "values": [
            float(plan.equity_pct),
            float(plan.debt_pct),
            float(plan.gold_pct),
            float(plan.cash_pct),
        ],
        "colors": ["#155eef", "#0e9f6e", "#f59e0b", "#94a3b8"],
    }

    # Corpus projection line chart
    corpus_labels = []
    corpus_values = []
    invested_values = []

    for row in table:
        if row["year"] in [1, 2, 3, 5, 7, 10, 15, 20]:
            corpus_labels.append(f"Year {row['year']}")
            corpus_values.append(float(row["value"]))
            invested_values.append(float(row["invested"]))

    return JsonResponse({
        "allocation": allocation,
        "corpus": {
            "labels": corpus_labels,
            "corpus": corpus_values,
            "invested": invested_values,
        },
    })


# ======================================================================
# MUTUAL FUNDS EDUCATION
# ======================================================================


@login_required
def mf_vs_fd(request):
    """Educational page comparing mutual funds vs fixed deposits."""
    comparison = MF_VS_FD_COMPARISON

    return render(
        request,
        "investments/mf_vs_fd.html",
        {
            "compare": comparison,
            "fd": comparison["fd"],
            "mf": comparison["mutual_fund"],
            "points": comparison["comparison_points"],
        },
    )


@login_required
def funds_explore(request):
    """Explore all mutual fund categories with education content."""
    # Recommend funds based on the user's risk profile if available
    profile = InvestorProfile.objects.filter(
        user=request.user,
    ).first()

    recommended = None
    if profile:
        recommended = best_fund_for_risk(profile.risk_tolerance)

    return render(
        request,
        "investments/funds_explore.html",
        {
            "categories": FUND_CATEGORIES,
            "profile": profile,
            "recommended": recommended,
        },
    )


@login_required
def funds_compare(request):
    """Compare selected mutual fund categories and show which is best."""
    fund_choices = [
        (f["key"], f"{f['name']} \u2014 {f['expected_return']}")
        for f in FUND_CATEGORIES
    ]

    result = None
    form = FundComparisonForm(fund_choices=fund_choices)

    if request.method == "POST":
        form = FundComparisonForm(
            request.POST,
            fund_choices=fund_choices,
        )

        if form.is_valid():
            keys = [
                form.cleaned_data["fund_a"],
                form.cleaned_data["fund_b"],
            ]
            if form.cleaned_data.get("fund_c"):
                keys.append(form.cleaned_data["fund_c"])
            if form.cleaned_data.get("fund_d"):
                keys.append(form.cleaned_data["fund_d"])

            keys = list(dict.fromkeys(keys))  # de-duplicate preserving order

            result = compare_funds(keys)

            if not result["selected"]:
                messages.warning(
                    request,
                    "Please select at least two funds to compare.",
                )
                result = None

            AIAnalysisLog.objects.create(
                user=request.user,
                activity_type="EDUCATION_VIEW",
                title="Mutual Fund Comparison",
                description=(
                    "Compared: "
                    + ", ".join(f["name"] for f in result["selected"])
                ) if result else "Mutual fund comparison attempted",
            )
    else:
        # Pre-select from user's risk profile
        profile = InvestorProfile.objects.filter(
            user=request.user,
        ).first()

        if profile:
            rec = best_fund_for_risk(profile.risk_tolerance)
            if len(rec) >= 2:
                form.initial = {
                    "fund_a": rec[0]["key"],
                    "fund_b": rec[1]["key"],
                }

    return render(
        request,
        "investments/funds_compare.html",
        {
            "form": form,
            "result": result,
            "categories": FUND_CATEGORIES,
        },
    )
