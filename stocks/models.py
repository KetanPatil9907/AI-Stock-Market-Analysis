from django.conf import settings
from django.db import models


class Stock(models.Model):
    """Cached snapshot of a stock so we don't hit the market API on every view."""
    symbol = models.CharField(max_length=20, unique=True, db_index=True)
    company_name = models.CharField(max_length=255, blank=True)
    sector = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    last_quote = models.JSONField(default=dict, blank=True)
    last_fundamentals = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.symbol


class StockSearch(models.Model):
    """Log of every search, for dashboard 'recent activity' + admin stats."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="stock_searches", null=True, blank=True
    )
    symbol = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.symbol} ({self.created_at:%Y-%m-%d})"


class StockAnalysis(models.Model):
    """A full AI (or rule-based) analysis result, savable by the user."""

    class Classification(models.TextChoices):
        STRONG = "STRONG", "Strong"
        POSITIVE = "POSITIVE", "Positive"
        NEUTRAL = "NEUTRAL", "Neutral"
        CAUTION = "CAUTION", "Caution"
        HIGH_RISK = "HIGH RISK", "High Risk"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="stock_analyses", null=True, blank=True
    )
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="analyses")

    company_overview = models.TextField(blank=True)
    fundamental_score = models.IntegerField(null=True, blank=True)
    technical_score = models.IntegerField(null=True, blank=True)
    growth_score = models.IntegerField(null=True, blank=True)
    risk_score = models.IntegerField(null=True, blank=True)
    overall_score = models.IntegerField(null=True, blank=True)

    strengths = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    opportunities = models.JSONField(default=list, blank=True)
    risks = models.JSONField(default=list, blank=True)
    important_factors = models.JSONField(default=list, blank=True)
    conclusion = models.TextField(blank=True)

    classification = models.CharField(
        max_length=20, choices=Classification.choices, default=Classification.NEUTRAL
    )
    source = models.CharField(
        max_length=20, default="rule_based",
        help_text="'ai' or 'rule_based' — which engine produced this analysis."
    )
    is_saved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Stock analyses"

    def __str__(self):
        return f"{self.stock.symbol} — {self.overall_score}/100 ({self.classification})"