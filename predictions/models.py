from django.conf import settings
from django.db import models


class PortfolioHolding(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="portfolio_holdings",
    )
    symbol = models.CharField(max_length=20)
    company_name = models.CharField(max_length=200, blank=True)
    quantity = models.PositiveIntegerField()
    buy_price = models.DecimalField(max_digits=12, decimal_places=2)
    buy_date = models.DateField()
    current_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    holding_type = models.CharField(
        max_length=10,
        choices=[("EQ", "Equity"), ("MF", "Mutual Fund"), ("ETF", "ETF")],
        default="EQ",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["user", "symbol", "buy_date"]

    def __str__(self):
        return f"{self.user.username} - {self.symbol} ({self.quantity})"

    @property
    def invested_amount(self):
        return float(self.buy_price) * self.quantity

    @property
    def current_value(self):
        if self.current_price:
            return float(self.current_price) * self.quantity
        return self.invested_amount

    @property
    def profit_loss(self):
        return self.current_value - self.invested_amount

    @property
    def profit_loss_pct(self):
        if self.invested_amount:
            return (self.profit_loss / self.invested_amount) * 100
        return 0


class PredictionRequest(models.Model):
    RISK_CHOICES = [
        ("CONSERVATIVE", "Conservative (Low Risk)"),
        ("MODERATE_CONSERVATIVE", "Moderately Conservative"),
        ("MODERATE", "Moderate (Medium Risk)"),
        ("MODERATE_AGGRESSIVE", "Moderately Aggressive"),
        ("AGGRESSIVE", "Aggressive (High Risk)"),
    ]

    MARKET_CHOICES = [
        ("NSE", "Indian (NSE/BSE)"),
        ("US", "US Markets (NASDAQ/NYSE)"),
        ("GLOBAL", "Global Markets"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="prediction_requests",
    )
    investment_amount = models.DecimalField(max_digits=15, decimal_places=2)
    risk_level = models.CharField(max_length=25, choices=RISK_CHOICES)
    market = models.CharField(max_length=10, choices=MARKET_CHOICES, default="NSE")
    investment_horizon = models.PositiveIntegerField(
        help_text="Investment horizon in months", default=12
    )
    include_stocks = models.BooleanField(default=True)
    include_mf = models.BooleanField(default=True)
    include_etf = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.user.username} - Rs.{self.investment_amount} "
            f"({self.risk_level}) - {self.market}"
        )


class PredictionResult(models.Model):
    SIGNAL_CHOICES = [
        ("STRONG_BUY", "Strong Buy"),
        ("BUY", "Buy"),
        ("HOLD", "Hold"),
        ("SELL", "Sell"),
        ("STRONG_SELL", "Strong Sell"),
    ]

    request = models.ForeignKey(
        PredictionRequest,
        on_delete=models.CASCADE,
        related_name="results",
    )
    symbol = models.CharField(max_length=20)
    company_name = models.CharField(max_length=200, blank=True)
    asset_type = models.CharField(
        max_length=10,
        choices=[("EQ", "Equity"), ("MF", "Mutual Fund"), ("ETF", "ETF")],
    )
    current_price = models.DecimalField(max_digits=12, decimal_places=2)
    predicted_price_1m = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    predicted_price_3m = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    predicted_price_6m = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    predicted_price_1y = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    expected_return_pct = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    signal = models.CharField(max_length=20, choices=SIGNAL_CHOICES)
    confidence_score = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="0-100"
    )
    sentiment_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="-100 to +100"
    )
    technical_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="0-100"
    )
    fundamental_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="0-100"
    )
    suggested_allocation_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )
    suggested_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )
    risk_rating = models.CharField(max_length=20, default="MODERATE")
    reasoning = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-confidence_score"]

    def __str__(self):
        return f"{self.symbol} - {self.signal} ({self.confidence_score}%)"


class SentimentData(models.Model):
    SOURCE_CHOICES = [
        ("NEWS", "News Article"),
        ("SOCIAL", "Social Media"),
        ("ANALYST", "Analyst Report"),
        ("FILING", "Company Filing"),
    ]

    symbol = models.CharField(max_length=20, db_index=True)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES)
    title = models.CharField(max_length=500)
    summary = models.TextField(blank=True)
    sentiment_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text="-100 (very bearish) to +100 (very bullish)"
    )
    sentiment_label = models.CharField(
        max_length=15,
        choices=[
            ("VERY_BEARISH", "Very Bearish"),
            ("BEARISH", "Bearish"),
            ("NEUTRAL", "Neutral"),
            ("BULLISH", "Bullish"),
            ("VERY_BULLISH", "Very Bullish"),
        ],
    )
    source_url = models.URLField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return f"{self.symbol} - {self.sentiment_label} ({self.source})"


class TaxHarvestRecord(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tax_harvest_records",
    )
    symbol = models.CharField(max_length=20)
    buy_price = models.DecimalField(max_digits=12, decimal_places=2)
    sell_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()
    buy_date = models.DateField()
    sell_date = models.DateField()
    gain_loss = models.DecimalField(max_digits=15, decimal_places=2)
    tax_type = models.CharField(
        max_length=10,
        choices=[("STCG", "Short Term Capital Gain"), ("LTCG", "Long Term Capital Gain")],
    )
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_saved = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sell_date"]

    def __str__(self):
        return f"{self.symbol} - {self.tax_type} - Rs.{self.gain_loss}"
