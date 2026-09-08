from django.urls import path
from . import views

app_name = "investments"

urlpatterns = [
    path("", views.money_planner, name="home"),
]