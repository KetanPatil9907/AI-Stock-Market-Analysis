from django.contrib import admin

from .models import IPO, IPOAnalysis


@admin.register(IPO)
class IPOAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "status",
        "industry",
        "price_band_max",
        "open_date",
        "close_date",
        "total_subscription",
        "is_active",
    )

    list_filter = (
        "status",
        "is_active",
        "industry",
    )

    search_fields = (
        "company_name",
        "industry",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("company_name",),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Basic IPO Information",
            {
                "fields": (
                    "company_name",
                    "slug",
                    "status",
                    "industry",
                    "exchange",
                    "is_active",
                )
            },
        ),
        (
            "Issue Details",
            {
                "fields": (
                    "price_band_min",
                    "price_band_max",
                    "issue_size_crore",
                    "lot_size",
                    "open_date",
                    "close_date",
                    "allotment_date",
                    "listing_date",
                )
            },
        ),
        (
            "Demand and Unofficial GMP",
            {
                "fields": (
                    "gmp",
                    "total_subscription",
                    "qib_subscription",
                    "nii_subscription",
                    "retail_subscription",
                ),
                "description": (
                    "GMP is unofficial, may change, and does not guarantee "
                    "listing performance."
                ),
            },
        ),
        (
            "Financial Information",
            {
                "fields": (
                    "revenue_crore",
                    "profit_crore",
                    "debt_crore",
                    "fresh_issue_crore",
                    "offer_for_sale_crore",
                )
            },
        ),
        (
            "Company and Sources",
            {
                "fields": (
                    "promoter_information",
                    "business_summary",
                    "risk_factors",
                    "official_source_url",
                    "source_name",
                )
            },
        ),
        (
            "Record Metadata",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(IPOAnalysis)
class IPOAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        "ipo",
        "user",
        "overall_score",
        "classification",
        "is_saved",
        "created_at",
    )

    list_filter = (
        "classification",
        "is_saved",
        "created_at",
    )

    search_fields = (
        "ipo__company_name",
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "analysis_snapshot",
        "strengths",
        "weaknesses",
        "risks",
        "things_to_check",
    )

    ordering = ("-created_at",)