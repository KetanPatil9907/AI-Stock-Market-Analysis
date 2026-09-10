from django.contrib import admin

from .models import (
    GoalProjection,
    InvestmentGoal,
    InvestorProfile,
    MoneyPlan,
    SIPEntry,
)


class SIPEntryInline(admin.TabularInline):
    model = SIPEntry
    extra = 0
    readonly_fields = [
        "category",
        "allocation_pct",
        "monthly_amount",
        "suggested_return_pct",
    ]


class GoalProjectionInline(admin.TabularInline):
    model = GoalProjection
    extra = 0
    readonly_fields = [
        "goal",
        "monthly_sip_needed",
        "projected_amount",
        "shortfall",
    ]


@admin.register(InvestorProfile)
class InvestorProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "age",
        "monthly_income",
        "monthly_expenses",
        "risk_tolerance",
        "risk_score",
        "updated_at",
    ]
    list_filter = ["risk_tolerance", "experience", "income_range"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = ["risk_score", "created_at", "updated_at"]

    fieldsets = (
        ("User", {"fields": ("user",)}),
        ("Financial Info", {
            "fields": (
                "age",
                "monthly_income",
                "monthly_expenses",
                "existing_investments",
                "emergency_fund",
                "income_range",
                "experience",
            ),
        }),
        ("Risk Profile", {
            "fields": ("risk_tolerance", "risk_score"),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )


@admin.register(InvestmentGoal)
class InvestmentGoalAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "goal_type",
        "custom_name",
        "target_amount",
        "target_years",
        "priority",
    ]
    list_filter = ["goal_type"]
    search_fields = ["user__username", "custom_name"]


@admin.register(MoneyPlan)
class MoneyPlanAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "plan_name",
        "risk_level_display",
        "equity_pct",
        "debt_pct",
        "total_monthly_sip",
        "is_saved",
        "created_at",
    ]
    list_filter = ["is_saved"]
    search_fields = ["user__username", "plan_name"]
    readonly_fields = [
        "investor_profile",
        "equity_pct",
        "debt_pct",
        "gold_pct",
        "cash_pct",
        "total_monthly_sip",
        "sip_returns_pct",
        "projected_corpus_5y",
        "projected_corpus_10y",
        "projected_corpus_15y",
        "projected_corpus_20y",
        "created_at",
        "updated_at",
    ]
    inlines = [SIPEntryInline, GoalProjectionInline]

    fieldsets = (
        ("Plan Info", {
            "fields": ("user", "plan_name", "investor_profile", "is_saved"),
        }),
        ("Allocation", {
            "fields": (
                "equity_pct",
                "debt_pct",
                "gold_pct",
                "cash_pct",
                "total_monthly_sip",
                "sip_returns_pct",
            ),
        }),
        ("Projected Corpus", {
            "fields": (
                "projected_corpus_5y",
                "projected_corpus_10y",
                "projected_corpus_15y",
                "projected_corpus_20y",
            ),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    def risk_level_display(self, obj):
        return obj.investor_profile.get_risk_tolerance_display()
    risk_level_display.short_description = "Risk Level"


@admin.register(SIPEntry)
class SIPEntryAdmin(admin.ModelAdmin):
    list_display = [
        "plan",
        "category",
        "allocation_pct",
        "monthly_amount",
        "suggested_return_pct",
    ]
    search_fields = ["category", "plan__user__username"]


@admin.register(GoalProjection)
class GoalProjectionAdmin(admin.ModelAdmin):
    list_display = [
        "plan",
        "goal",
        "monthly_sip_needed",
        "projected_amount",
        "shortfall",
    ]
    search_fields = ["plan__user__username"]
