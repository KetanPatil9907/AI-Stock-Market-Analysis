from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    # Authentication
    path("", include("accounts.urls")),

    # Dashboard
    path("dashboard/", include("dashboard.urls")),

    # Module 3 - AI Stock Analysis
    path("stocks/", include("stocks.urls")),
]