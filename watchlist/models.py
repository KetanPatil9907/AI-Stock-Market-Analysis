from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class WatchlistItem(models.Model):
    """A stock saved by a user to their personal watchlist."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="watchlist_items",
    )

    symbol = models.CharField(
        max_length=20,
        db_index=True,
    )

    company_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-added_at"]
        unique_together = ["user", "symbol"]
        verbose_name = "Watchlist Item"
        verbose_name_plural = "Watchlist Items"

    def __str__(self):
        return f"{self.user.username} — {self.symbol}"


class PriceAlert(models.Model):
    """A price threshold alert set by a user on a watchlist stock."""

    class AlertType(models.TextChoices):
        ABOVE = "ABOVE", "Price Goes Above"
        BELOW = "BELOW", "Price Goes Below"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        TRIGGERED = "TRIGGERED", "Triggered"
        DISABLED = "DISABLED", "Disabled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="price_alerts",
    )

    symbol = models.CharField(
        max_length=20,
        db_index=True,
    )

    alert_type = models.CharField(
        max_length=10,
        choices=AlertType.choices,
    )

    target_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )

    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    message = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Optional custom message for this alert.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    triggered_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Price Alert"
        verbose_name_plural = "Price Alerts"

    def __str__(self):
        return (
            f"{self.symbol} "
            f"{self.get_alert_type_display()} "
            f"₹{self.target_price} "
            f"({self.get_status_display()})"
        )
