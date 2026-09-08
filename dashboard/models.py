from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class AIAnalysisLog(models.Model):
    ACTIVITY_TYPES = [
        ("STOCK_SEARCH", "Stock Search"),
        ("STOCK_ANALYSIS", "Stock Analysis"),
        ("STOCK_COMPARISON", "Stock Comparison"),
        ("IPO_SEARCH", "IPO Search"),
        ("IPO_ANALYSIS", "IPO Analysis"),
        ("INVESTMENT_PLAN", "Investment Plan"),
        ("EDUCATION_VIEW", "Education View"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="analysis_logs",
    )

    activity_type = models.CharField(
        max_length=30,
        choices=ACTIVITY_TYPES,
    )

    title = models.CharField(max_length=255)

    description = models.TextField(
        blank=True,
        default="",
    )

    reference_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional ID of a linked analysis object.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "AI Analysis Log"
        verbose_name_plural = "AI Analysis Logs"

    def __str__(self):
        return f"{self.user.username} - {self.title}"