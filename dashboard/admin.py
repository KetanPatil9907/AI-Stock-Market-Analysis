from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import AIAnalysisLog


@admin.register(AIAnalysisLog)
class AIAnalysisLogAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "activity_type",
        "created_at",
    )

    list_filter = (
        "activity_type",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "user__username",
        "user__email",
    )

    readonly_fields = ("created_at",)

    ordering = ("-created_at",)