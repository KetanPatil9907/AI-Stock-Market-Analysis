import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from agents.stock_agent import StockAgent
from services.market_data_service import MarketDataService, MarketDataServiceError

from .forms import StockSearchForm, StockCompareForm
from .models import Stock, StockAnalysis, StockSearch

logger = logging.getLogger(__name__)

market_service = MarketDataService()
stock_agent = StockAgent()


@login_required
def stock_search(request):
    """AI Stock Analysis landing page + search handler."""
    form = StockSearchForm(request.GET or None)
    context = {"form": form}

    if request.GET and form.is_valid():
        symbol = form.cleaned_data["symbol"]
        return redirect("stocks:analysis_detail", symbol=symbol)

    return render(request, "stocks/search.html", context)


@login_required
def analysis_detail(request, symbol):
    """Fetches live data, runs the agent, and displays the analysis."""
    symbol = symbol.strip().upper()
    StockSearch.objects.create(user=request.user, symbol=symbol)

    context = {"symbol": symbol}

    try:
        quote = market_service.get_stock_quote(symbol)
    except MarketDataServiceError:
        context["error"] = "Market data service is currently unavailable."
        return render(request, "stocks/analysis_detail.html", context)

    if not quote.get("found"):
        context["error"] = f"No data found for symbol '{symbol}'. Please check and try again."
        return render(request, "stocks/analysis_detail.html", context)

    try:
        fundamentals = market_service.get_stock_fundamentals(symbol)
    except MarketDataServiceError:
        fundamentals = {"symbol": symbol}
        messages.warning(request, "Some fundamental data could not be loaded.")

    try:
        historical = market_service.get_historical_data(symbol, period="1M")
    except MarketDataServiceError:
        historical = {"labels": [], "prices": [], "volumes": []}

    technical_indicators = {}
    try:
        from services.technical_indicators import compute_all_indicators
        technical_indicators = compute_all_indicators(historical.get("prices", []))
    except Exception as e:
        logger.warning("Technical indicators failed for %s: %s", symbol, e)

    dividend_data = {"dividends": [], "total_dividends": 0, "avg_dividend": 0}
    try:
        dividend_data = market_service.get_dividend_history(symbol)
    except Exception as e:
        logger.warning("Dividend data failed for %s: %s", symbol, e)

    insider_data = {"transactions": [], "summary": {}}
    try:
        insider_data = market_service.get_insider_transactions(symbol)
    except Exception as e:
        logger.warning("Insider data failed for %s: %s", symbol, e)

    peer_data = []
    try:
        sector = fundamentals.get("sector", "")
        industry = fundamentals.get("industry", "")
        peer_data = market_service.get_peer_stocks(sector, industry, symbol)
    except Exception as e:
        logger.warning("Peer data failed for %s: %s", symbol, e)

    analysis = stock_agent.analyze(quote, fundamentals)

    stock_obj, _ = Stock.objects.update_or_create(
        symbol=symbol,
        defaults={
            "company_name": fundamentals.get("company_name") or "",
            "sector": fundamentals.get("sector") or "",
            "industry": fundamentals.get("industry") or "",
            "last_quote": quote,
            "last_fundamentals": fundamentals,
        },
    )

    context.update({
        "quote": quote,
        "fundamentals": fundamentals,
        "historical_json": json.dumps(historical),
        "technical_indicators_json": json.dumps(technical_indicators),
        "analysis": analysis,
        "stock_id": stock_obj.id,
        "technical_indicators": technical_indicators,
        "dividend_data": dividend_data,
        "insider_data": insider_data,
        "peer_data": peer_data,
    })
    return render(request, "stocks/analysis_detail.html", context)


@login_required
@require_POST
def save_analysis(request, symbol):
    """Persists the current analysis as a saved StockAnalysis row."""
    symbol = symbol.strip().upper()
    stock_obj, _ = Stock.objects.get_or_create(symbol=symbol)

    quote = stock_obj.last_quote or {}
    fundamentals = stock_obj.last_fundamentals or {}
    analysis = stock_agent.analyze(quote, fundamentals)

    StockAnalysis.objects.create(
        user=request.user,
        stock=stock_obj,
        company_overview=analysis.get("company_overview", ""),
        fundamental_score=analysis.get("fundamental_score"),
        technical_score=analysis.get("technical_score"),
        growth_score=analysis.get("growth_score"),
        risk_score=analysis.get("risk_score"),
        overall_score=analysis.get("overall_score"),
        strengths=analysis.get("strengths", []),
        weaknesses=analysis.get("weaknesses", []),
        opportunities=analysis.get("opportunities", []),
        risks=analysis.get("risks", []),
        important_factors=analysis.get("important_factors", []),
        conclusion=analysis.get("conclusion", ""),
        classification=analysis.get("classification", "NEUTRAL"),
        source=analysis.get("source", "rule_based"),
        is_saved=True,
    )
    messages.success(request, f"Analysis for {symbol} saved.")
    return redirect("stocks:analysis_detail", symbol=symbol)


@login_required
def compare_stocks(request):
    """Stock Comparison — accepts 2-4 symbols and shows a side-by-side table."""
    form = StockCompareForm(request.GET or None)
    results = []

    if request.GET and form.is_valid():
        for symbol in form.cleaned_data["symbols"]:
            try:
                quote = market_service.get_stock_quote(symbol)
                fundamentals = market_service.get_stock_fundamentals(symbol)
            except MarketDataServiceError:
                results.append({"symbol": symbol, "error": "Data unavailable"})
                continue
            if not quote.get("found"):
                results.append({"symbol": symbol, "error": "Symbol not found"})
                continue
            results.append({**quote, **fundamentals, "error": None})

    return render(request, "stocks/compare.html", {"form": form, "results": results})