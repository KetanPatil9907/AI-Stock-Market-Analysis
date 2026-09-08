from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "user",
        "age",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = (
        "full_name",
        "user__username",
        "user__email",
    )
    readonly_fields = ("created_at", "updated_at")