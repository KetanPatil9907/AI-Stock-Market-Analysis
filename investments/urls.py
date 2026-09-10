from django.urls import path

from . import views

app_name = "investments"

urlpatterns = [
    # Home
    path(
        "",
        views.home,
        name="home",
    ),

    # Risk Assessment
    path(
        "risk-assessment/",
        views.risk_assessment,
        name="risk_assessment",
    ),

    # Profile Setup
    path(
        "profile/",
        views.profile_setup,
        name="profile_setup",
    ),

    # Goals
    path(
        "goals/",
        views.goals,
        name="goals",
    ),
    path(
        "goals/<int:goal_id>/edit/",
        views.goal_edit,
        name="goal_edit",
    ),
    path(
        "goals/<int:goal_id>/delete/",
        views.goal_delete,
        name="goal_delete",
    ),

    # Generate & View Plan
    path(
        "generate/",
        views.generate_plan_view,
        name="generate_plan",
    ),
    path(
        "plan/<int:plan_id>/",
        views.plan_result,
        name="plan_result",
    ),
    path(
        "plan/<int:plan_id>/save/",
        views.save_plan,
        name="save_plan",
    ),
    path(
        "plan/<int:plan_id>/delete/",
        views.delete_plan,
        name="delete_plan",
    ),
    path(
        "plan/<int:plan_id>/chart-data/",
        views.plan_chart_data,
        name="plan_chart_data",
    ),

    # Saved Plans
    path(
        "saved/",
        views.saved_plans,
        name="saved_plans",
    ),

    # Calculators
    path(
        "sip-calculator/",
        views.sip_calculator,
        name="sip_calculator",
    ),
    path(
        "lumpsum-calculator/",
        views.lumpsum_calculator,
        name="lumpsum_calculator",
    ),

    # Mutual Funds Education
    path(
        "mf-vs-fd/",
        views.mf_vs_fd,
        name="mf_vs_fd",
    ),
    path(
        "funds/",
        views.funds_explore,
        name="funds_explore",
    ),
    path(
        "funds/compare/",
        views.funds_compare,
        name="funds_compare",
    ),
]
