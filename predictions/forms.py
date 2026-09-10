from django import forms

from .models import PortfolioHolding, PredictionRequest, TaxHarvestRecord


class PredictionForm(forms.ModelForm):
    investment_amount = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=1000,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Enter amount (e.g., 100000)",
                "id": "investment-amount",
            }
        ),
        help_text="Minimum investment amount: Rs. 1,000",
    )

    RISK_CHOICES = [
        ("", "-- Select Risk Level --"),
        ("CONSERVATIVE", "Conservative - Low Risk (8-10% returns)"),
        ("MODERATE_CONSERVATIVE", "Moderately Conservative (10-12% returns)"),
        ("MODERATE", "Moderate - Medium Risk (12-14% returns)"),
        ("MODERATE_AGGRESSIVE", "Moderately Aggressive (14-16% returns)"),
        ("AGGRESSIVE", "Aggressive - High Risk (16%+ returns)"),
    ]

    risk_level = forms.ChoiceField(
        choices=RISK_CHOICES,
        widget=forms.Select(
            attrs={"class": "form-select form-select-lg", "id": "risk-level"}
        ),
    )

    MARKET_CHOICES = [
        ("NSE", "Indian Market (NSE/BSE)"),
        ("US", "US Market (NASDAQ/NYSE)"),
        ("GLOBAL", "Global Markets"),
    ]

    market = forms.ChoiceField(
        choices=MARKET_CHOICES,
        widget=forms.Select(
            attrs={"class": "form-select form-select-lg", "id": "market-select"}
        ),
    )

    investment_horizon = forms.IntegerField(
        min_value=1,
        max_value=120,
        initial=12,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Investment horizon in months",
            }
        ),
        help_text="How long do you plan to stay invested? (1-120 months)",
    )

    class Meta:
        model = PredictionRequest
        fields = [
            "investment_amount",
            "risk_level",
            "market",
            "investment_horizon",
            "include_stocks",
            "include_mf",
            "include_etf",
        ]
        widgets = {
            "include_stocks": forms.CheckboxInput(
                attrs={"class": "form-check-input", "checked": True}
            ),
            "include_mf": forms.CheckboxInput(
                attrs={"class": "form-check-input", "checked": True}
            ),
            "include_etf": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }


class PortfolioHoldingForm(forms.ModelForm):
    class Meta:
        model = PortfolioHolding
        fields = [
            "symbol",
            "company_name",
            "quantity",
            "buy_price",
            "buy_date",
            "current_price",
            "holding_type",
        ]
        widgets = {
            "symbol": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g., RELIANCE"}
            ),
            "company_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Company name"}
            ),
            "quantity": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Number of shares"}
            ),
            "buy_price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Buy price per share"}
            ),
            "buy_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "current_price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Current market price"}
            ),
            "holding_type": forms.Select(attrs={"class": "form-select"}),
        }


class TaxHarvestForm(forms.Form):
    symbol = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Stock symbol (e.g., RELIANCE)"}
        ),
    )
    buy_price = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Buy price"}
        ),
    )
    sell_price = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Sell price"}
        ),
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Quantity"}
        ),
    )
    buy_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control", "type": "date"}
        ),
    )
    sell_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control", "type": "date"}
        ),
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 3, "placeholder": "Optional notes"}
        ),
    )
