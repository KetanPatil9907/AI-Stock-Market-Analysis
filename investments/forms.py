from django import forms

from .models import InvestmentGoal, InvestorProfile


class InvestorProfileForm(forms.ModelForm):
    """Form for creating / updating the investor financial profile."""

    class Meta:
        model = InvestorProfile
        fields = [
            "age",
            "monthly_income",
            "monthly_expenses",
            "existing_investments",
            "emergency_fund",
            "income_range",
            "experience",
        ]
        widgets = {
            "age": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 18,
                "max": 70,
                "placeholder": "e.g. 30",
            }),
            "monthly_income": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. 75000",
            }),
            "monthly_expenses": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. 45000",
            }),
            "existing_investments": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. 500000",
            }),
            "emergency_fund": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. 200000",
            }),
            "income_range": forms.Select(attrs={
                "class": "form-select",
            }),
            "experience": forms.Select(attrs={
                "class": "form-select",
            }),
        }


class RiskQuestionnaireForm(forms.Form):
    """
    Dynamic risk assessment questionnaire.
    Questions are rendered from the services module.
    """

    def __init__(self, *args, questions=None, **kwargs):
        super().__init__(*args, **kwargs)

        if questions:
            for q in questions:
                choices = [
                    (i, opt["label"])
                    for i, opt in enumerate(q["options"])
                ]
                self.fields[q["id"]] = forms.TypedChoiceField(
                    choices=choices,
                    coerce=int,
                    label=q["question"],
                    widget=forms.RadioSelect(attrs={
                        "class": "risk-radio",
                    }),
                    required=True,
                )


class InvestmentGoalForm(forms.ModelForm):
    """Form for creating / editing an investment goal."""

    class Meta:
        model = InvestmentGoal
        fields = [
            "goal_type",
            "custom_name",
            "target_amount",
            "target_years",
            "priority",
        ]
        widgets = {
            "goal_type": forms.Select(attrs={
                "class": "form-select",
            }),
            "custom_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Dream Home Fund",
            }),
            "target_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. 5000000",
            }),
            "target_years": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 40,
                "placeholder": "e.g. 10",
            }),
            "priority": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 10,
                "placeholder": "1 = highest",
            }),
        }


class SIPCalculatorForm(forms.Form):
    """Standalone SIP calculator form."""

    monthly_amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        label="Monthly SIP Amount (\u20b9)",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. 10000",
        }),
    )

    annual_return = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        initial=12,
        label="Expected Annual Return (%)",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. 12",
        }),
    )

    years = forms.IntegerField(
        min_value=1,
        max_value=50,
        initial=10,
        label="Investment Duration (Years)",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. 10",
        }),
    )


class LumpsumCalculatorForm(forms.Form):
    """Standalone lump-sum calculator form."""

    principal = forms.DecimalField(
        max_digits=16,
        decimal_places=2,
        label="Lump Sum Amount (₹)",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. 500000",
        }),
    )

    annual_return = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        initial=12,
        label="Expected Annual Return (%)",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. 12",
        }),
    )

    years = forms.IntegerField(
        min_value=1,
        max_value=50,
        initial=10,
        label="Investment Duration (Years)",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. 10",
        }),
    )


class FundComparisonForm(forms.Form):
    """Form to select mutual fund categories for comparison."""

    fund_a = forms.ChoiceField(
        label="Fund 1",
        widget=forms.Select(attrs={
            "class": "form-select",
        }),
    )

    fund_b = forms.ChoiceField(
        label="Fund 2",
        widget=forms.Select(attrs={
            "class": "form-select",
        }),
    )

    fund_c = forms.ChoiceField(
        label="Fund 3 (optional)",
        required=False,
        widget=forms.Select(attrs={
            "class": "form-select",
        }),
    )

    fund_d = forms.ChoiceField(
        label="Fund 4 (optional)",
        required=False,
        widget=forms.Select(attrs={
            "class": "form-select",
        }),
    )

    def __init__(self, *args, **kwargs):
        fund_choices = kwargs.pop("fund_choices", [])
        super().__init__(*args, **kwargs)

        choices = [("", "--- Select a fund ---")] + fund_choices

        self.fields["fund_a"].choices = choices
        self.fields["fund_b"].choices = choices
        self.fields["fund_c"].choices = choices
        self.fields["fund_d"].choices = choices
