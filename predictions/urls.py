from django.urls import path

from . import views

app_name = "predictions"

urlpatterns = [
    path("", views.home, name="home"),
    path("predict/", views.prediction_form_view, name="prediction_form"),
    path("results/<int:pk>/", views.prediction_results_view, name="results"),
    path("stock/<str:symbol>/", views.stock_detail_view, name="stock_detail"),
    path("portfolio/", views.portfolio_home_view, name="portfolio"),
    path("portfolio/add/", views.add_holding_view, name="add_holding"),
    path("portfolio/<int:pk>/edit/", views.edit_holding_view, name="edit_holding"),
    path("portfolio/<int:pk>/delete/", views.delete_holding_view, name="delete_holding"),
    path("portfolio/<int:pk>/chart/", views.portfolio_chart_data_view, name="portfolio_chart"),
    path("tax-harvesting/", views.tax_harvesting_view, name="tax_harvesting"),
    path("tax-harvesting/add/", views.add_tax_record_view, name="add_tax_record"),
    path("tax-harvesting/<int:pk>/delete/", views.delete_tax_record_view, name="delete_tax_record"),
    path("sentiment/<str:symbol>/", views.sentiment_view, name="sentiment"),
    path("market-overview/", views.market_overview_view, name="market_overview"),
    path("compare/", views.compare_stocks_view, name="compare"),
    path("recommend/", views.future_recommendations_view, name="future_recommendations"),
    path("forecast/<str:symbol>/", views.stock_forecast_view, name="stock_forecast"),
]
