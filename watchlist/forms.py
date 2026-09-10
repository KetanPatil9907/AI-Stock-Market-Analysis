from django import forms

from .models import PriceAlert


class AddToWatchlistForm(forms.Form):
    """Form to add a stock symbol to the watchlist."""

    symbol = forms.CharField(
        max_length=20,
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter NSE symbol e.g. RELIANCE, TCS",
                "autocomplete": "off",
            }
        ),
    )

    def clean_symbol(self):
        return self.cleaned_data["symbol"].strip().upper()


class PriceAlertForm(forms.ModelForm):
    """Form to create or edit a price alert."""

    class Meta:
        model = PriceAlert
        fields = ["symbol", "alert_type", "target_price", "message"]
        widgets = {
            "symbol": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. RELIANCE",
                    "autocomplete": "off",
                }
            ),
            "alert_type": forms.Select(
                attrs={"class": "form-select"}
            ),
            "target_price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 2500.00",
                    "step": "0.01",
                    "min": "0.01",
                }
            ),
            "message": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Optional: e.g. Buy if it drops below this",
                }
            ),
        }

    def clean_target_price(self):
        price = self.cleaned_data["target_price"]
        if price <= 0:
            raise forms.ValidationError("Target price must be greater than zero.")
        return price
