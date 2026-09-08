from django.urls import path

from . import views

app_name = "stocks"

urlpatterns = [
    path("", views.stock_search, name="search"),
    path("compare/", views.compare_stocks, name="compare"),
    path("<str:symbol>/", views.analysis_detail, name="analysis_detail"),
    path("<str:symbol>/save/", views.save_analysis, name="save_analysis"),
]