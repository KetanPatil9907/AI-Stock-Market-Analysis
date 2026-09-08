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
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

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

    email_template_name = "accounts/password_reset_email.html"

    subject_template_name = "accounts/password_reset_subject.txt"

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


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"

    success_url = reverse_lazy(
        "accounts:password_reset_complete"
    )


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"