import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils import timezone

from services.market_data_service import MarketDataService, MarketDataServiceError

from .forms import AddToWatchlistForm, PriceAlertForm
from .models import PriceAlert, WatchlistItem

logger = logging.getLogger(__name__)

market_service = MarketDataService()


@login_required
def watchlist_home(request):
    """Display all items in the user's watchlist with live price data."""
    items = WatchlistItem.objects.filter(user=request.user)
    add_form = AddToWatchlistForm()

    watchlist_data = []
    for item in items:
        try:
            quote = market_service.get_stock_quote(item.symbol)
        except MarketDataServiceError:
            quote = {"found": False}

        current_price = quote.get("current_price") if quote.get("found") else None
        previous_close = quote.get("previous_close") if quote.get("found") else None

        change = None
        change_pct = None
        if current_price not in (None, "Data unavailable") and previous_close not in (None, "Data unavailable"):
            try:
                change = round(float(current_price) - float(previous_close), 2)
                change_pct = round((change / float(previous_close)) * 100, 2)
            except (TypeError, ValueError, ZeroDivisionError):
                pass

        alerts = PriceAlert.objects.filter(
            user=request.user,
            symbol=item.symbol,
            status="ACTIVE",
        )

        watchlist_data.append({
            "item": item,
            "current_price": current_price,
            "change": change,
            "change_pct": change_pct,
            "alerts": alerts,
        })

    return render(
        request,
        "watchlist/watchlist_home.html",
        {
            "watchlist_data": watchlist_data,
            "add_form": add_form,
        },
    )


@login_required
@require_POST
def add_to_watchlist(request):
    """Add a stock symbol to the user's watchlist."""
    form = AddToWatchlistForm(request.POST)

    if form.is_valid():
        symbol = form.cleaned_data["symbol"]

        if WatchlistItem.objects.filter(
            user=request.user, symbol=symbol
        ).exists():
            messages.info(request, f"{symbol} is already in your watchlist.")
            return redirect("watchlist:home")

        company_name = ""
        try:
            fundamentals = market_service.get_stock_fundamentals(symbol)
            company_name = fundamentals.get("company_name", "")
        except MarketDataServiceError:
            pass

        WatchlistItem.objects.create(
            user=request.user,
            symbol=symbol,
            company_name=company_name,
        )
        messages.success(request, f"{symbol} added to your watchlist.")

    return redirect("watchlist:home")


@login_required
@require_POST
def remove_from_watchlist(request, item_id):
    """Remove a stock from the user's watchlist."""
    item = get_object_or_404(
        WatchlistItem, id=item_id, user=request.user
    )
    symbol = item.symbol
    item.delete()
    messages.success(request, f"{symbol} removed from your watchlist.")
    return redirect("watchlist:home")


@login_required
def create_alert(request, symbol):
    """Create a price alert for a specific stock."""
    symbol = symbol.strip().upper()

    if request.method == "POST":
        form = PriceAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.user = request.user
            alert.symbol = symbol
            alert.save()
            messages.success(
                request,
                f"Alert set: {symbol} {alert.get_alert_type_display()} ₹{alert.target_price}",
            )
            return redirect("watchlist:home")
    else:
        form = PriceAlertForm(initial={"symbol": symbol})

    return render(
        request,
        "watchlist/create_alert.html",
        {"form": form, "symbol": symbol},
    )


@login_required
@require_POST
def toggle_alert(request, alert_id):
    """Enable or disable a price alert."""
    alert = get_object_or_404(
        PriceAlert, id=alert_id, user=request.user
    )

    if alert.status == "ACTIVE":
        alert.status = "DISABLED"
        messages.info(request, f"Alert for {alert.symbol} disabled.")
    else:
        alert.status = "ACTIVE"
        messages.success(request, f"Alert for {alert.symbol} re-enabled.")

    alert.save(update_fields=["status"])
    return redirect("watchlist:home")


@login_required
@require_POST
def delete_alert(request, alert_id):
    """Permanently delete a price alert."""
    alert = get_object_or_404(
        PriceAlert, id=alert_id, user=request.user
    )
    symbol = alert.symbol
    alert.delete()
    messages.success(request, f"Alert for {symbol} deleted.")
    return redirect("watchlist:home")


@login_required
def check_alerts(request):
    """
    Check all active alerts for the current user against live prices.
    Triggered alerts are marked and a notification is shown.
    """
    active_alerts = PriceAlert.objects.filter(
        user=request.user,
        status="ACTIVE",
    )

    triggered = []

    symbols = set(alert.symbol for alert in active_alerts)

    price_map = {}
    for symbol in symbols:
        try:
            quote = market_service.get_stock_quote(symbol)
            if quote.get("found"):
                price_map[symbol] = float(quote["current_price"])
        except (MarketDataServiceError, TypeError, ValueError):
            continue

    for alert in active_alerts:
        current_price = price_map.get(alert.symbol)
        if current_price is None:
            continue

        should_trigger = False

        if alert.alert_type == "ABOVE" and current_price >= float(alert.target_price):
            should_trigger = True
        elif alert.alert_type == "BELOW" and current_price <= float(alert.target_price):
            should_trigger = True

        if should_trigger:
            alert.status = "TRIGGERED"
            alert.triggered_at = timezone.now()
            alert.save(update_fields=["status", "triggered_at"])
            triggered.append(alert)

    if triggered:
        for alert in triggered:
            messages.warning(
                request,
                f"Alert triggered: {alert.symbol} "
                f"{alert.get_alert_type_display()} ₹{alert.target_price} "
                f"(Current: ₹{price_map.get(alert.symbol, '?')})",
            )
    else:
        messages.info(request, "No alerts triggered right now.")

    return redirect("watchlist:home")
