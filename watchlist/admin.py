from django.contrib import admin

from .models import PriceAlert, WatchlistItem


@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "symbol",
        "company_name",
        "added_at",
    ]
    list_filter = ["added_at"]
    search_fields = ["symbol", "company_name", "user__username"]
    readonly_fields = ["added_at"]


@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "symbol",
        "alert_type",
        "target_price",
        "status",
        "created_at",
        "triggered_at",
    ]
    list_filter = ["status", "alert_type", "created_at"]
    search_fields = ["symbol", "user__username"]
    readonly_fields = ["created_at", "triggered_at"]
