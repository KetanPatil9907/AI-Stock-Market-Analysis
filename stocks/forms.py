from django import forms


class StockSearchForm(forms.Form):
    symbol = forms.CharField(
        max_length=20,
        label="",
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "Enter NSE symbol e.g. RELIANCE, TCS, INFY",
            "autocomplete": "off",
        }),
    )

    def clean_symbol(self):
        symbol = self.cleaned_data["symbol"].strip().upper()
        if not symbol.replace("&", "").replace("-", "").isalnum():
            raise forms.ValidationError("Enter a valid stock symbol.")
        return symbol


class StockCompareForm(forms.Form):
    symbols = forms.CharField(
        max_length=100,
        label="",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. RELIANCE, TCS, INFY (2-4 symbols, comma separated)",
        }),
    )

    def clean_symbols(self):
        raw = self.cleaned_data["symbols"]
        symbols = [s.strip().upper() for s in raw.split(",") if s.strip()]
        if not (2 <= len(symbols) <= 4):
            raise forms.ValidationError("Enter between 2 and 4 symbols.")
        return symbols