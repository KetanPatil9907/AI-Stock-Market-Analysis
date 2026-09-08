from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import UserProfile


class RegisterForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        label="Full Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your full name",
                "autocomplete": "name",
            }
        ),
    )

    age = forms.IntegerField(
        min_value=18,
        max_value=120,
        label="Age",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "18",
                "min": 18,
                "max": 120,
            }
        ),
    )

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "name@example.com",
                "autocomplete": "email",
            }
        ),
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Create a secure password",
                "autocomplete": "new-password",
            }
        ),
    )

    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Repeat your password",
                "autocomplete": "new-password",
            }
        ),
    )

    def clean_full_name(self):
        full_name = self.cleaned_data["full_name"].strip()

        if len(full_name) < 2:
            raise forms.ValidationError(
                "Please enter a valid full name."
            )

        return full_name

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account already exists with this email address."
            )

        return email

    def clean_password(self):
        password = self.cleaned_data["password"]

        try:
            validate_password(password)
        except ValidationError as error:
            raise forms.ValidationError(error.messages)

        return password

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error(
                "confirm_password",
                "Password confirmation does not match.",
            )

        return cleaned_data

    def save(self):
        full_name = self.cleaned_data["full_name"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password"]

        username_base = email.split("@")[0]
        username = username_base
        counter = 1

        while User.objects.filter(username=username).exists():
            username = f"{username_base}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name,
        )

        UserProfile.objects.create(
            user=user,
            full_name=full_name,
            age=self.cleaned_data["age"],
        )

        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "name@example.com",
                "autocomplete": "email",
            }
        ),
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
            }
        ),
    )

    remember_me = forms.BooleanField(
        required=False,
        label="Remember me",
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input"}
        ),
    )


class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "autocomplete": "email",
            }
        ),
    )

    class Meta:
        model = UserProfile
        fields = ["full_name", "age"]
        widgets = {
            "full_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "name",
                }
            ),
            "age": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 18,
                    "max": 120,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields["email"].initial = self.user.email

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()

        if (
            User.objects.filter(email__iexact=email)
            .exclude(pk=self.user.pk)
            .exists()
        ):
            raise forms.ValidationError(
                "Another account already uses this email address."
            )

        return email

    def save(self, commit=True):
        profile = super().save(commit=False)

        if self.user:
            self.user.email = self.cleaned_data["email"]
            self.user.first_name = profile.full_name

            if commit:
                self.user.save()

        if commit:
            profile.save()

        return profile