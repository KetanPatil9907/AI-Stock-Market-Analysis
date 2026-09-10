from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PortfolioHoldingForm, PredictionForm, TaxHarvestForm
from .ml_service import MLPredictionService
from .models import (
    PortfolioHolding,
    PredictionRequest,
    PredictionResult,
    TaxHarvestRecord,
)
from .recommendation_engine import RecommendationEngine
from .sentiment_service import SentimentAnalysisService
from .tax_service import TaxHarvestingService
from .future_predictor import (
    get_top_recommendations,
    get_single_stock_forecast,
    NSE_UNIVERSE,
)


@login_required
def home(request):
    user = request.user
    recent_predictions = PredictionRequest.objects.filter(user=user)[:5]
    portfolio_holdings = PortfolioHolding.objects.filter(user=user)
    tax_records = TaxHarvestRecord.objects.filter(user=user)[:10]

    total_invested = sum(h.invested_amount for h in portfolio_holdings)
    total_current = sum(h.current_value for h in portfolio_holdings)
    total_pnl = total_current - total_invested

    context = {
        "recent_predictions": recent_predictions,
        "portfolio_holdings": portfolio_holdings,
        "tax_records": tax_records,
        "total_invested": total_invested,
        "total_current": total_current,
        "total_pnl": total_pnl,
        "holdings_count": portfolio_holdings.count(),
    }
    return render(request, "predictions/home.html", context)


@login_required
def prediction_form_view(request):
    if request.method == "POST":
        form = PredictionForm(request.POST)
        if form.is_valid():
            prediction_request = form.save(commit=False)
            prediction_request.user = request.user
            prediction_request.save()

            recommendations = RecommendationEngine.get_recommendations(
                risk_level=prediction_request.risk_level,
                amount=float(prediction_request.investment_amount),
                market=prediction_request.market,
                include_stocks=prediction_request.include_stocks,
                include_mf=prediction_request.include_mf,
            )

            for rec in recommendations:
                PredictionResult.objects.create(
                    request=prediction_request,
                    symbol=rec["symbol"],
                    company_name=rec["company_name"],
                    asset_type=rec["asset_type"],
                    current_price=rec["current_price"],
                    predicted_price_1m=rec.get("predicted_price_1m"),
                    predicted_price_3m=rec.get("predicted_price_3m"),
                    predicted_price_6m=rec.get("predicted_price_6m"),
                    predicted_price_1y=rec.get("predicted_price_1y"),
                    expected_return_pct=rec.get("expected_return_pct"),
                    signal=rec["signal"],
                    confidence_score=rec["confidence_score"],
                    sentiment_score=rec.get("sentiment_score", 0),
                    technical_score=rec.get("technical_score", 0),
                    suggested_allocation_pct=0,
                    suggested_amount=rec.get("suggested_amount", 0),
                    risk_rating=rec.get("risk_rating", "MODERATE"),
                    reasoning=rec.get("reasoning", ""),
                )

            return redirect("predictions:results", pk=prediction_request.pk)
    else:
        form = PredictionForm()

    return render(request, "predictions/prediction_form.html", {"form": form})


@login_required
def prediction_results_view(request, pk):
    prediction_request = get_object_or_404(
        PredictionRequest, pk=pk, user=request.user
    )
    results = PredictionResult.objects.filter(request=prediction_request)

    strong_buys = results.filter(signal="STRONG_BUY")
    buys = results.filter(signal="BUY")
    holds = results.filter(signal="HOLD")
    sells = results.filter(signal__in=["SELL", "STRONG_SELL"])

    profile = RecommendationEngine.RISK_PROFILES.get(
        prediction_request.risk_level, {}
    )

    context = {
        "prediction_request": prediction_request,
        "results": results,
        "strong_buys": strong_buys,
        "buys": buys,
        "holds": holds,
        "sells": sells,
        "profile": profile,
        "total_suggested": sum(r.suggested_amount for r in results),
    }
    return render(request, "predictions/results.html", context)


@login_required
def stock_detail_view(request, symbol):
    prediction = MLPredictionService.predict_stock(symbol)
    sentiment = SentimentAnalysisService.get_comprehensive_sentiment(symbol)

    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "prediction": prediction,
            "sentiment": sentiment,
        })

    context = {
        "symbol": symbol,
        "prediction": prediction,
        "sentiment": sentiment,
    }
    return render(request, "predictions/stock_detail.html", context)


@login_required
def portfolio_home_view(request):
    holdings = PortfolioHolding.objects.filter(user=request.user)
    form = PortfolioHoldingForm()

    total_invested = sum(h.invested_amount for h in holdings)
    total_current = sum(h.current_value for h in holdings)
    total_pnl = total_current - total_invested
    pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0

    context = {
        "holdings": holdings,
        "form": form,
        "total_invested": total_invested,
        "total_current": total_current,
        "total_pnl": total_pnl,
        "pnl_pct": pnl_pct,
    }
    return render(request, "predictions/portfolio.html", context)


@login_required
def add_holding_view(request):
    if request.method == "POST":
        form = PortfolioHoldingForm(request.POST)
        if form.is_valid():
            holding = form.save(commit=False)
            holding.user = request.user
            if not holding.current_price:
                holding.current_price = holding.buy_price
            holding.save()
            messages.success(request, f"Added {holding.symbol} to your portfolio.")
            return redirect("predictions:portfolio")
    return redirect("predictions:portfolio")


@login_required
def edit_holding_view(request, pk):
    holding = get_object_or_404(PortfolioHolding, pk=pk, user=request.user)
    if request.method == "POST":
        form = PortfolioHoldingForm(request.POST, instance=holding)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated {holding.symbol}.")
            return redirect("predictions:portfolio")
    else:
        form = PortfolioHoldingForm(instance=holding)
    return render(request, "predictions/edit_holding.html", {"form": form, "holding": holding})


@login_required
def delete_holding_view(request, pk):
    holding = get_object_or_404(PortfolioHolding, pk=pk, user=request.user)
    if request.method == "POST":
        symbol = holding.symbol
        holding.delete()
        messages.success(request, f"Removed {symbol} from your portfolio.")
    return redirect("predictions:portfolio")


@login_required
def tax_harvesting_view(request):
    holdings = PortfolioHolding.objects.filter(user=request.user)
    tax_records = TaxHarvestRecord.objects.filter(user=request.user)

    harvest_analysis = TaxHarvestingService.analyze_portfolio_for_harvesting(holdings)
    tax_report = TaxHarvestingService.generate_tax_report(holdings)

    form = TaxHarvestForm()

    context = {
        "holdings": holdings,
        "tax_records": tax_records,
        "harvest_analysis": harvest_analysis,
        "tax_report": tax_report,
        "form": form,
    }
    return render(request, "predictions/tax_harvesting.html", context)


@login_required
def add_tax_record_view(request):
    if request.method == "POST":
        form = TaxHarvestForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user

            gain_loss = (record.sell_price - record.buy_price) * record.quantity
            holding_period = (record.sell_date - record.buy_date).days

            tax_info = TaxHarvestingService.calculate_tax(gain_loss, holding_period)
            record.gain_loss = gain_loss
            record.tax_type = tax_info["tax_type"]
            record.tax_amount = tax_info["tax_amount"]
            record.tax_saved = 0

            if gain_loss < 0:
                record.tax_saved = abs(gain_loss) * (
                    TaxHarvestingService.LTCG_RATE / 100
                    if holding_period > 365
                    else TaxHarvestingService.STCG_RATE / 100
                )

            record.save()
            messages.success(request, f"Tax record added for {record.symbol}.")
            return redirect("predictions:tax_harvesting")
    return redirect("predictions:tax_harvesting")


@login_required
def delete_tax_record_view(request, pk):
    record = get_object_or_404(TaxHarvestRecord, pk=pk, user=request.user)
    if request.method == "POST":
        record.delete()
        messages.success(request, "Tax record deleted.")
    return redirect("predictions:tax_harvesting")


@login_required
def sentiment_view(request, symbol):
    sentiment = SentimentAnalysisService.get_comprehensive_sentiment(symbol)
    return render(request, "predictions/sentiment.html", {
        "symbol": symbol,
        "sentiment": sentiment,
    })


@login_required
def market_overview_view(request):
    top_stocks = RecommendationEngine.NSE_BLUE_CHIPS[:10]
    stock_data = []

    for stock in top_stocks:
        prediction = MLPredictionService.predict_stock(stock["symbol"])
        if prediction:
            stock_data.append({
                "symbol": stock["symbol"],
                "name": stock["name"],
                "sector": stock["sector"],
                "current_price": prediction["current_price"],
                "expected_return": prediction["expected_return_pct"],
                "signal": prediction["signal"],
                "technical_score": prediction["technical_score"],
                "risk_rating": prediction["risk_rating"],
            })

    return render(request, "predictions/market_overview.html", {"stocks": stock_data})


@login_required
def compare_stocks_view(request):
    symbols = request.GET.get("symbols", "").split(",")
    symbols = [s.strip() for s in symbols if s.strip()]

    predictions = []
    for symbol in symbols[:5]:
        pred = MLPredictionService.predict_stock(symbol)
        sentiment = SentimentAnalysisService.get_comprehensive_sentiment(symbol)
        if pred:
            pred["sentiment"] = sentiment
            predictions.append(pred)

    return render(request, "predictions/compare.html", {"predictions": predictions, "symbols": symbols})


@login_required
def portfolio_chart_data_view(request, pk):
    holding = get_object_or_404(PortfolioHolding, pk=pk, user=request.user)
    return JsonResponse({
        "labels": ["Invested", "Current"],
        "data": [float(holding.invested_amount), float(holding.current_value)],
    })


SECTOR_CHOICES = sorted({s["sector"] for s in NSE_UNIVERSE})


@login_required
def future_recommendations_view(request):
    sector = request.GET.get("sector", "")
    min_return = request.GET.get("min_return", "0")
    try:
        min_return = float(min_return)
    except ValueError:
        min_return = 0.0

    recommendations = get_top_recommendations(
        min_score=48, max_results=40, sector_filter=sector or None
    )

    if min_return > 0:
        recommendations = [
            r for r in recommendations
            if r.get("return_3m_pct", 0) >= min_return
            or r.get("return_6m_pct", 0) >= min_return
        ]

    strong_buys = [r for r in recommendations if r["signal"] == "STRONG_BUY"]
    buys = [r for r in recommendations if r["signal"] == "BUY"]
    holds = [r for r in recommendations if r["signal"] == "HOLD"]
    avg_return_3m = (
        sum(r["return_3m_pct"] for r in recommendations) / len(recommendations)
        if recommendations else 0
    )
    avg_return_6m = (
        sum(r["return_6m_pct"] for r in recommendations) / len(recommendations)
        if recommendations else 0
    )

    context = {
        "recommendations": recommendations,
        "strong_buys": strong_buys,
        "buys": buys,
        "holds": holds,
        "total_count": len(recommendations),
        "avg_return_3m": round(avg_return_3m, 2),
        "avg_return_6m": round(avg_return_6m, 2),
        "sector_choices": SECTOR_CHOICES,
        "selected_sector": sector,
        "selected_min_return": min_return,
    }
    return render(request, "predictions/future_recommendations.html", context)


@login_required
def stock_forecast_view(request, symbol):
    symbol = symbol.upper().strip()
    forecast = get_single_stock_forecast(symbol)
    if forecast is None:
        messages.error(
            request,
            f"Unable to generate forecast for {symbol}. Please check the symbol and try again.",
        )
        return redirect("predictions:future_recommendations")
    return render(
        request, "predictions/stock_forecast.html", {"forecast": forecast}
    )
