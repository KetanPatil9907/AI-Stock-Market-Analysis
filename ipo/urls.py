from django.urls import path

from . import views

app_name = "ipo"

urlpatterns = [
    path("", views.ipo_center_view, name="center"),
    path(
        "explain/",
        views.ipo_explain_view,
        name="explain",
    ),
    path(
        "refresh-gmp/",
        views.refresh_gmp_view,
        name="refresh_gmp",
    ),
    path(
        "<slug:slug>/",
        views.ipo_detail_view,
        name="detail",
    ),
    path(
        "analysis/<int:analysis_id>/save/",
        views.save_ipo_analysis_view,
        name="save",
    ),
    path(
        "analysis/<int:analysis_id>/saved/",
        views.saved_ipo_analysis_view,
        name="saved",
    ),
]