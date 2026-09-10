from django.urls import path

from . import views

app_name = "watchlist"

urlpatterns = [
    path("", views.watchlist_home, name="home"),
    path("add/", views.add_to_watchlist, name="add"),
    path("<int:item_id>/remove/", views.remove_from_watchlist, name="remove"),
    path("alert/<str:symbol>/create/", views.create_alert, name="create_alert"),
    path("alert/<int:alert_id>/toggle/", views.toggle_alert, name="toggle_alert"),
    path("alert/<int:alert_id>/delete/", views.delete_alert, name="delete_alert"),
    path("check-alerts/", views.check_alerts, name="check_alerts"),
]
