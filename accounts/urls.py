from django.urls import path

from . import views


app_name = "accounts"


urlpatterns = [
    # Login / Register
    path(
        "",
        views.login_view,
        name="login",
    ),

    path(
        "register/",
        views.register_view,
        name="register",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    # Profile
    path(
        "profile/",
        views.profile_view,
        name="profile",
    ),

    # Change Password
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

    # ========================================================
    # FORGOT PASSWORD / PASSWORD RESET
    # ========================================================

    path(
        "forgot-password/",
        views.UserPasswordResetView.as_view(),
        name="password_reset",
    ),

    path(
        "forgot-password/done/",
        views.UserPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        views.UserPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),

    path(
        "reset/complete/",
        views.UserPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]