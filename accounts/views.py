
import os

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt

from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions

from .forms import LoginForm, ProfileUpdateForm, RegisterForm


# =========================
# REGISTER
# =========================

def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            authenticated_user = authenticate(
                request,
                username=user.email,
                password=form.cleaned_data["password"],
            )

            if authenticated_user is not None:
                login(request, authenticated_user)

                messages.success(
                    request,
                    "Registration successful. Welcome to AI Finance Assistant!",
                )

                return redirect("dashboard:home")

            messages.error(
                request,
                "Registration successful, but automatic login failed. Please login manually.",
            )

            return redirect("accounts:login")

    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form},
    )


# =========================
# LOGIN
# =========================

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"].strip()
            password = form.cleaned_data["password"]

            user = authenticate(
                request,
                username=email,
                password=password,
            )

            if user is not None:
                login(request, user)

                # Remember me
                if form.cleaned_data.get("remember_me"):
                    request.session.set_expiry(60 * 60 * 24 * 30)
                else:
                    request.session.set_expiry(0)

                # Get user's name safely
                try:
                    welcome_name = user.profile.full_name
                except Exception:
                    welcome_name = (
                        user.first_name
                        or user.username
                        or user.email
                    )

                messages.success(
                    request,
                    f"Welcome back, {welcome_name}!",
                )

                return redirect("dashboard:home")

            messages.error(
                request,
                "Invalid email address or password.",
            )

    else:
        form = LoginForm()

    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
            "next": next_url,
        },
    )


# =========================
# LOGOUT
# =========================

@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)

        messages.success(
            request,
            "You have been logged out successfully.",
        )

    return redirect("accounts:login")


# =========================
# PROFILE
# =========================

@login_required
def profile_view(request):
    try:
        profile = request.user.profile
    except request.user.profile.RelatedObjectDoesNotExist:
        messages.error(
            request,
            "Your profile does not exist. Please contact the administrator.",
        )
        return redirect("dashboard:home")

    if request.method == "POST":
        form = ProfileUpdateForm(
            request.POST,
            instance=profile,
            user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Your profile was updated successfully.",
            )

            return redirect("accounts:profile")

    else:
        form = ProfileUpdateForm(
            instance=profile,
            user=request.user,
        )

    return render(
        request,
        "accounts/profile.html",
        {"form": form},
    )


# =========================
# CHANGE PASSWORD
# =========================

class UserPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_change.html"

    success_url = reverse_lazy(
        "accounts:password_change_done"
    )

    def form_valid(self, form):
        messages.success(
            self.request,
            "Your password has been changed successfully.",
        )

        return super().form_valid(form)


class UserPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "accounts/password_change_done.html"


# =========================
# PASSWORD RESET
# =========================

class UserPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset_form.html"

    email_template_name = (
        "accounts/password_reset_email.html"
    )

    subject_template_name = (
        "accounts/password_reset_subject.txt"
    )

    success_url = reverse_lazy(
        "accounts:password_reset_done"
    )

    def form_valid(self, form):
        messages.success(
            self.request,
            "If an account exists with that email, a password reset link has been generated.",
        )

        return super().form_valid(form)


class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class UserPasswordResetConfirmView(
    PasswordResetConfirmView
):
    template_name = (
        "accounts/password_reset_confirm.html"
    )

    success_url = reverse_lazy(
        "accounts:password_reset_complete"
    )


class UserPasswordResetCompleteView(
    PasswordResetCompleteView
):
    template_name = (
        "accounts/password_reset_complete.html"
    )


# ============================================================
# CLERK AUTHENTICATION
# ============================================================
#
# This is ADDITIONAL authentication.
#
# Your existing Django login/register/logout/password-reset
# functionality above remains unchanged.
#
# ============================================================


def _get_clerk_client():
    """
    Create and return a Clerk client.
    """

    secret_key = os.getenv("CLERK_SECRET_KEY")
    publishable_key = os.getenv("CLERK_PUBLISHABLE_KEY")

    if not secret_key:
        raise ValueError(
            "CLERK_SECRET_KEY is not configured."
        )

    if not publishable_key:
        raise ValueError(
            "CLERK_PUBLISHABLE_KEY is not configured."
        )

    return Clerk(
        bearer_auth=secret_key,
    )


def _authenticate_clerk_request(request):
    """
    Verify the Clerk session token from the request.

    Returns:
        (clerk_user_id, error_message)
    """

    try:
        secret_key = os.getenv("CLERK_SECRET_KEY")
        publishable_key = os.getenv(
            "CLERK_PUBLISHABLE_KEY"
        )

        if not secret_key:
            return (
                None,
                "CLERK_SECRET_KEY is not configured.",
            )

        if not publishable_key:
            return (
                None,
                "CLERK_PUBLISHABLE_KEY is not configured.",
            )

        clerk = Clerk(
            bearer_auth=secret_key,
        )

        request_state = clerk.authenticate_request(
            request,
            AuthenticateRequestOptions(
                authorized_parties=[
                    "http://127.0.0.1:8000",
                    "http://localhost:8000",
                ],
                accepts_token="session_token",
            ),
        )

        if not request_state.is_authenticated:
            return (
                None,
                "Clerk session is not authenticated.",
            )

        payload = request_state.payload

        if not payload:
            return (
                None,
                "Clerk authentication payload is missing.",
            )

        clerk_user_id = payload.get("sub")

        if not clerk_user_id:
            return (
                None,
                "Clerk user ID was not found.",
            )

        return clerk_user_id, None

    except Exception as e:
        print(
            "Clerk authentication error:",
            str(e),
        )

        return (
            None,
            "Unable to verify Clerk authentication.",
        )


@csrf_exempt
def clerk_login_view(request):
    """
    Login using an authenticated Clerk session.

    This converts the verified Clerk user into a normal
    Django session so request.user continues to work
    throughout the existing Django application.
    """

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "Only POST requests are allowed.",
            },
            status=405,
        )

    # --------------------------------------------------------
    # Verify Clerk session
    # --------------------------------------------------------

    clerk_user_id, error = (
        _authenticate_clerk_request(request)
    )

    if error:
        return JsonResponse(
            {
                "success": False,
                "message": error,
            },
            status=401,
        )

    try:
        # ----------------------------------------------------
        # Get Clerk user
        # ----------------------------------------------------

        clerk = _get_clerk_client()

        clerk_user = clerk.users.get(
            user_id=clerk_user_id
        )

        # ----------------------------------------------------
        # Get email
        # ----------------------------------------------------

        email = None

        email_addresses = (
            clerk_user.email_addresses or []
        )

        primary_email_id = getattr(
            clerk_user,
            "primary_email_address_id",
            None,
        )

        # First try primary email
        for email_address in email_addresses:

            if (
                getattr(
                    email_address,
                    "id",
                    None,
                )
                == primary_email_id
            ):
                email = (
                    email_address.email_address
                )
                break

        # Fallback to first email
        if not email and email_addresses:
            email = (
                email_addresses[0].email_address
            )

        if not email:
            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        "No email address was found "
                        "for this Clerk account."
                    ),
                },
                status=400,
            )

        email = email.strip().lower()

        # ----------------------------------------------------
        # Find existing Django user
        # ----------------------------------------------------

        from django.contrib.auth import get_user_model

        User = get_user_model()

        user = User.objects.filter(
            email__iexact=email
        ).first()

        # ----------------------------------------------------
        # Create Django user if needed
        # ----------------------------------------------------

        if user is None:

            username_base = email.split("@")[0]

            username = username_base
            counter = 1

            while User.objects.filter(
                username=username
            ).exists():

                username = (
                    f"{username_base}{counter}"
                )

                counter += 1

            user = User.objects.create_user(
                username=username,
                email=email,
            )

        # ----------------------------------------------------
        # Login to Django
        # ----------------------------------------------------

        login(
            request,
            user,
            backend=(
                "django.contrib.auth.backends."
                "ModelBackend"
            ),
        )

        # ----------------------------------------------------
        # Django session
        # ----------------------------------------------------

        request.session.set_expiry(
            60 * 60 * 24 * 30
        )

        # ----------------------------------------------------
        # Success
        # ----------------------------------------------------

        messages.success(
            request,
            f"Welcome back, {user.email}!",
        )

        return JsonResponse(
            {
                "success": True,
                "message": "Clerk login successful.",
                "redirect_url": "/dashboard/",
                "email": email,
            }
        )

    except Exception as e:

        print(
            "Clerk login error:",
            str(e),
        )

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Unable to complete Clerk login."
                ),
            },
            status=500,
        )
