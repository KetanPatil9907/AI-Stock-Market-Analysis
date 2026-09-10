
from django.urls import path

from . import views


app_name = "accounts"


urlpatterns = [

    # ==================================================
    # EXISTING DJANGO AUTHENTICATION
    # ==================================================

    path(
        "",
        views.login_view,
        name="login",
    ),
    path(
    "clerk-login/",
    views.clerk_login_view,
    name="clerk_login",
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

    path(
        "profile/",
        views.profile_view,
        name="profile",
    ),


    # ==================================================
    # PASSWORD CHANGE
    # ==================================================

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


    # ==================================================
    # PASSWORD RESET
    # ==================================================

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


    # ==================================================
    # CLERK LOGIN
    # ==================================================

    path(
        "clerk-login/",
        views.clerk_login_view,
        name="clerk_login",
    ),
]
