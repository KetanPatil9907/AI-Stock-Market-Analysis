from django.contrib import admin

from .models import (
    PortfolioHolding,
    PredictionRequest,
    PredictionResult,
    SentimentData,
    TaxHarvestRecord,
)


@admin.register(PortfolioHolding)
class PortfolioHoldingAdmin(admin.ModelAdmin):
    list_display = [
        "user", "symbol", "company_name", "quantity", "buy_price",
        "current_price", "holding_type", "profit_loss", "created_at",
    ]
    list_filter = ["holding_type", "created_at"]
    search_fields = ["symbol", "company_name", "user__username"]
    readonly_fields = ["created_at", "updated_at"]

    def profit_loss(self, obj):
        return f"Rs.{obj.profit_loss:,.2f}"
    profit_loss.short_description = "P&L"


@admin.register(PredictionRequest)
class PredictionRequestAdmin(admin.ModelAdmin):
    list_display = [
        "user", "investment_amount", "risk_level", "market",
        "investment_horizon", "created_at",
    ]
    list_filter = ["risk_level", "market", "created_at"]
    search_fields = ["user__username"]
    readonly_fields = ["created_at"]


@admin.register(PredictionResult)
class PredictionResultAdmin(admin.ModelAdmin):
    list_display = [
        "symbol", "company_name", "asset_type", "current_price",
        "signal", "confidence_score", "expected_return_pct",
        "risk_rating", "created_at",
    ]
    list_filter = ["signal", "asset_type", "risk_rating"]
    search_fields = ["symbol", "company_name"]
    readonly_fields = ["created_at"]


@admin.register(SentimentData)
class SentimentDataAdmin(admin.ModelAdmin):
    list_display = [
        "symbol", "source", "sentiment_label", "sentiment_score",
        "title", "published_at",
    ]
    list_filter = ["source", "sentiment_label"]
    search_fields = ["symbol", "title"]
    readonly_fields = ["fetched_at"]


@admin.register(TaxHarvestRecord)
class TaxHarvestRecordAdmin(admin.ModelAdmin):
    list_display = [
        "user", "symbol", "buy_price", "sell_price", "quantity",
        "gain_loss", "tax_type", "tax_amount", "tax_saved", "sell_date",
    ]
    list_filter = ["tax_type", "sell_date"]
    search_fields = ["symbol", "user__username"]
    readonly_fields = ["created_at"]
