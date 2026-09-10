from django.conf import settings
from django.db import models


class InvestorProfile(models.Model):
    """User's financial profile used to calculate risk and allocation."""

    class RiskLevel(models.TextChoices):
        CONSERVATIVE = "CONSERVATIVE", "Conservative"
        MODERATE_CONSERVATIVE = "MODERATE_CONSERVATIVE", "Moderate Conservative"
        MODERATE = "MODERATE", "Moderate"
        MODERATE_AGGRESSIVE = "MODERATE_AGGRESSIVE", "Moderate Aggressive"
        AGGRESSIVE = "AGGRESSIVE", "Aggressive"

    class IncomeRange(models.TextChoices):
        BELOW_3L = "BELOW_3L", "Below \u20b93 LPA"
        RANGE_3L_6L = "RANGE_3L_6L", "\u20b93\u20136 LPA"
        RANGE_6L_10L = "RANGE_6L_10L", "\u20b96\u201310 LPA"
        RANGE_10L_20L = "RANGE_10L_20L", "\u20b910\u201320 LPA"
        RANGE_20L_50L = "RANGE_20L_50L", "\u20b920\u201350 LPA"
        ABOVE_50L = "ABOVE_50L", "Above \u20b950 LPA"

    class Experience(models.TextChoices):
        BEGINNER = "BEGINNER", "Beginner (0\u20131 years)"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate (1\u20133 years)"
        EXPERIENCED = "EXPERIENCED", "Experienced (3\u20137 years)"
        EXPERT = "EXPERT", "Expert (7+ years)"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="investor_profile",
    )

    age = models.PositiveIntegerField(
        default=30,
        help_text="Investor age (18\u201370).",
    )

    monthly_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Monthly income in \u20b9.",
    )

    monthly_expenses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Monthly expenses in \u20b9.",
    )

    existing_investments = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        help_text="Total current investment value in \u20b9.",
    )

    emergency_fund = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        help_text="Emergency fund already set aside in \u20b9.",
    )

    income_range = models.CharField(
        max_length=20,
        choices=IncomeRange.choices,
        default=IncomeRange.RANGE_3L_6L,
    )

    experience = models.CharField(
        max_length=20,
        choices=Experience.choices,
        default=Experience.BEGINNER,
    )

    risk_tolerance = models.CharField(
        max_length=25,
        choices=RiskLevel.choices,
        default=RiskLevel.MODERATE,
    )

    # Risk assessment raw score (computed from questionnaire)
    risk_score = models.IntegerField(
        default=50,
        help_text="0\u2013100 risk score from questionnaire.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Investor Profile"
        verbose_name_plural = "Investor Profiles"

    def __str__(self):
        return f"{self.user.username} \u2014 {self.risk_tolerance}"

    @property
    def monthly_savings(self):
        return self.monthly_income - self.monthly_expenses


class InvestmentGoal(models.Model):
    """A specific financial goal the user wants to plan for."""

    class GoalType(models.TextChoices):
        RETIREMENT = "RETIREMENT", "Retirement"
        CHILD_EDUCATION = "CHILD_EDUCATION", "Child Education"
        HOME_PURCHASE = "HOME_PURCHASE", "Home Purchase"
        WEALTH_CREATION = "WEALTH_CREATION", "Wealth Creation"
        EMERGENCY_FUND = "EMERGENCY_FUND", "Emergency Fund"
        VACATION = "VACATION", "Vacation / Travel"
        WEDDING = "WEDDING", "Wedding"
        CAR_PURCHASE = "CAR_PURCHASE", "Car Purchase"
        OTHER = "OTHER", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="investment_goals",
    )

    goal_type = models.CharField(
        max_length=25,
        choices=GoalType.choices,
        default=GoalType.WEALTH_CREATION,
    )

    custom_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Custom name when goal_type is OTHER.",
    )

    target_amount = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        help_text="Target amount in \u20b9.",
    )

    target_years = models.PositiveIntegerField(
        help_text="Number of years to reach this goal.",
    )

    priority = models.PositiveIntegerField(
        default=1,
        help_text="1 = highest priority.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "created_at"]

    def __str__(self):
        name = self.custom_name or self.get_goal_type_display()
        return f"{name} \u2014 \u20b9{self.target_amount:,.0f} in {self.target_years}y"


class MoneyPlan(models.Model):
    """A computed investment plan with allocation and SIP recommendations."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="money_plans",
    )

    investor_profile = models.ForeignKey(
        InvestorProfile,
        on_delete=models.CASCADE,
        related_name="plans",
    )

    plan_name = models.CharField(max_length=150, blank=True)

    # Allocation percentages (must add up to 100)
    equity_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=60,
        help_text="Equity allocation %.",
    )
    debt_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=25,
        help_text="Debt / Fixed Income allocation %.",
    )
    gold_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10,
        help_text="Gold allocation %.",
    )
    cash_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=5,
        help_text="Cash / Liquid allocation %.",
    )

    total_monthly_sip = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Recommended total monthly SIP in \u20b9.",
    )

    # Projected corpus
    projected_corpus_5y = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
    )
    projected_corpus_10y = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
    )
    projected_corpus_15y = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
    )
    projected_corpus_20y = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
    )

    # Metadata
    sip_returns_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=12,
        help_text="Assumed annual return % for SIP projections.",
    )

    is_saved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        name = self.plan_name or f"Plan {self.id}"
        return f"{name} \u2014 SIP \u20b9{self.total_monthly_sip:,.0f}/mo"


class SIPEntry(models.Model):
    """Individual SIP allocation within a MoneyPlan."""

    plan = models.ForeignKey(
        MoneyPlan,
        on_delete=models.CASCADE,
        related_name="sip_entries",
    )

    category = models.CharField(
        max_length=50,
        help_text="E.g. Large Cap, Mid Cap, Liquid Fund.",
    )

    sub_category = models.CharField(
        max_length=50,
        blank=True,
        help_text="E.g. Index Fund, Corporate Bond.",
    )

    allocation_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="% of total SIP.",
    )

    monthly_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Monthly SIP amount in \u20b9.",
    )

    suggested_return_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=12,
        help_text="Assumed annual return for this category.",
    )

    class Meta:
        ordering = ["-allocation_pct"]

    def __str__(self):
        return f"{self.category} \u2014 \u20b9{self.monthly_amount:,.0f} ({self.allocation_pct}%)"


class GoalProjection(models.Model):
    """Per-goal projection within a MoneyPlan."""

    plan = models.ForeignKey(
        MoneyPlan,
        on_delete=models.CASCADE,
        related_name="goal_projections",
    )

    goal = models.ForeignKey(
        InvestmentGoal,
        on_delete=models.CASCADE,
        related_name="projections",
    )

    monthly_sip_needed = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Monthly SIP needed for this goal.",
    )

    projected_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text="Projected amount at goal deadline.",
    )

    shortfall = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        help_text="Positive = surplus, negative = shortfall.",
    )

    class Meta:
        verbose_name = "Goal Projection"
        verbose_name_plural = "Goal Projections"

    def __str__(self):
        return f"{self.goal} \u2192 \u20b9{self.projected_amount:,.0f}"
