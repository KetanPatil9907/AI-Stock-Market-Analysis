from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("accounts.urls")),

    path("dashboard/", include("dashboard.urls")),

    path("stocks/", include("stocks.urls")),
    path("ipo/", include("ipo.urls")),
    path("investments/", include("investments.urls")),
]