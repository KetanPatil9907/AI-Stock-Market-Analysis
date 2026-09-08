from django.contrib import admin

from .models import Stock, StockAnalysis, StockSearch


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("symbol", "company_name", "sector", "updated_at")
    search_fields = ("symbol", "company_name")
    list_filter = ("sector",)


@admin.register(StockSearch)
class StockSearchAdmin(admin.ModelAdmin):
    list_display = ("symbol", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("symbol", "user__username")


@admin.register(StockAnalysis)
class StockAnalysisAdmin(admin.ModelAdmin):
    list_display = ("stock", "user", "overall_score", "classification", "source", "created_at")
    list_filter = ("classification", "source", "created_at")
    search_fields = ("stock__symbol", "user__username")