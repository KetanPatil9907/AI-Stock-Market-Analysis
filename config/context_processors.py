def clerk_settings(request):
    from django.conf import settings

    return {
        "CLERK_PUBLISHABLE_KEY":
            settings.CLERK_PUBLISHABLE_KEY,
    }