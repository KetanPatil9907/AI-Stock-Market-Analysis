from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),

    path(
        "password-change/",
        views.UserPasswordChangeView.as_view(),
        name="password_change",
    ),

    path(
        "password-change/done/",
        views.UserPasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),

    path(
        "password-reset/",
        views.UserPasswordResetView.as_view(),
        name="password_reset",
    ),

    path(
        "password-reset/done/",
        views.UserPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),

    path(
        "password-reset/<uidb64>/<token>/",
        views.UserPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),

    path(
        "password-reset/complete/",
        views.UserPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]