# AI Finance Assistant - Architecture Document

## 1. High-Level System Architecture

```
+=====================================================================+
|                          CLIENT (Browser)                            |
|   Bootstrap 5.3.3  --  Bootstrap Icons  --  Custom CSS + JS         |
|   Django Templates (37 HTML files)                                   |
+===============================+=====================================+
                                | HTTP (Templates + JSON APIs)
                                v
+=====================================================================+
|                     DJANGO APPLICATION (WSGI)                        |
|                                                                      |
|   [Middleware Stack]                                                 |
|   Security -> Session -> Common -> CSRF -> Auth -> Messages -> XFrame|
|                                                                      |
|   [URL Router: config/urls.py]                                       |
|   ""            -> accounts.urls   (Auth)                            |
|   "/dashboard/" -> dashboard.urls  (Activity Log)                    |
|   "/stocks/"    -> stocks.urls     (Stock Analysis)                  |
|   "/ipo/"       -> ipo.urls        (IPO Center)                      |
|   "/investments/"->investments.urls(Money Planner)                   |
|   "/admin/"     -> Django Admin                                      |
|                                                                      |
|   [Django Apps]   accounts | dashboard | stocks | ipo | investments  |
|                                                                      |
|   [Agents + Services Layer]                                          |
|   agents/StockAgent  -> services/AIService (Claude API)              |
|   agents/IPOAgent    -> services/MarketDataService (yfinance)        |
|                       -> services/IPODataService (Upstox API)        |
|   investments/services.py (Allocation Engine + Calculators)          |
|                                                                      |
|   [Django ORM - 12 Models]                                           |
|   UserProfile, AIAnalysisLog, Stock, StockSearch, StockAnalysis,     |
|   IPO, IPOAnalysis, InvestorProfile, InvestmentGoal, MoneyPlan,      |
|   SIPEntry, GoalProjection, WatchlistItem, PriceAlert                |
|                                                                      |
|   [Database]  SQLite3 (db.sqlite3)                                   |
+=====================================================================+

External APIs (outbound):
  Anthropic Claude API  <-> AIService (stock analysis)
  Yahoo Finance         <-> MarketDataService (NSE quotes/fundamentals)
  Upstox IPO API        <-> IPODataService (IPO data sync)
  Clerk Auth API        <-> accounts/views.py (SSO login)
```

## 2. Project Directory Structure

```
STOCK/
|-- manage.py                          # Django CLI entry point
|-- db.sqlite3                         # SQLite database
|-- requirements.txt                   # Python dependencies
|-- .env / .env.example                # Environment config
|
|-- config/                            # Django project configuration
|   |-- settings.py                    # Main settings (135 lines)
|   |-- urls.py                        # Root URL routing (14 lines)
|   |-- wsgi.py / asgi.py             # WSGI/ASGI entry points
|   +-- context_processors.py          # Clerk key template context
|
|-- accounts/                          # User authentication app
|   |-- models.py                      # UserProfile (23 lines)
|   |-- views.py                       # Login/Register/Logout/Profile/Clerk (581 lines)
|   |-- urls.py                        # 10 URL patterns
|   |-- forms.py                       # RegisterForm, LoginForm, ProfileUpdateForm
|   |-- backends.py                    # Custom EmailBackend
|   +-- templates/accounts/            # 9 HTML templates
|
|-- dashboard/                         # Dashboard / Activity Log
|   |-- models.py                      # AIAnalysisLog (51 lines)
|   |-- views.py                       # Dashboard home view
|   +-- templates/dashboard/           # 2 HTML templates
|
|-- stocks/                            # Stock Analysis app
|   |-- models.py                      # Stock, StockSearch, StockAnalysis (82 lines)
|   |-- views.py                       # Search/Analysis/Compare/Save (139 lines)
|   |-- urls.py                        # 4 URL patterns
|   +-- templates/stocks/              # 3 HTML templates
|
|-- ipo/                               # IPO Center app
|   |-- models.py                      # IPO, IPOAnalysis (339 lines)
|   |-- views.py                       # IPO Center/Detail/Save (315 lines)
|   |-- services.py                    # IPOAnalysisService wrapper
|   +-- templates/ipo/                 # 5 HTML templates
|
|-- investments/                       # Money Planner app
|   |-- models.py                      # 5 models (343 lines)
|   |-- views.py                       # 15 views (694 lines)
|   |-- services.py                    # Allocation engine + calculators (499 lines)
|   |-- funds_data.py                  # MF categories data (457 lines)
|   +-- templates/investments/         # 11 HTML templates
|
|-- watchlist/                         # Watchlist app (NOT WIRED yet)
|   |-- models.py                      # WatchlistItem, PriceAlert (103 lines)
|   |-- views.py                       # 7 views (225 lines)
|   +-- templates/watchlist/           # 2 HTML templates
|
|-- education/                         # Empty placeholder app
|
|-- agents/                            # AI Analysis Agents
|   |-- stock_agent.py                 # StockAgent (130 lines)
|   +-- ipo_agent.py                   # IPOAgent (390 lines)
|
|-- services/                          # External Service Wrappers
|   |-- ai_service.py                  # AIService - Claude wrapper (81 lines)
|   |-- market_data_service.py         # MarketDataService - yfinance (133 lines)
|   +-- ipo_data_service.py            # IPODataService - Upstox (619 lines)
|
|-- templates/                         # Project-level templates
|   |-- base.html                      # Base layout (Bootstrap 5)
|   |-- navbar.html                    # Navigation bar
|   +-- footer.html                    # Footer with disclaimer
|
+-- static/
    |-- css/style.css                  # Custom CSS (619 lines)
    +-- js/main.js                     # Auto-dismiss alerts
```

## 3. Data Flow Diagrams

### 3A. Stock Analysis Flow

```
User (Browser)
    |
    |  GET /stocks/ (search form)
    v
stocks.views.stock_search()
    |
    |  Redirect to /stocks/<symbol>/
    v
stocks.views.analysis_detail(symbol)
    |
    +-->> MarketDataService.get_stock_quote(symbol)
    |       |
    |       +-->> yfinance.Ticker("{SYMBOL}.NS").fast_info
    |              (current_price, day_high, day_low, volume, market_cap)
    |
    +-->> MarketDataService.get_stock_fundamentals(symbol)
    |       |
    |       +-->> yfinance.Ticker("{SYMBOL}.NS").info
    |              (pe_ratio, eps, roe, debt_to_equity, dividend_yield)
    |
    +-->> MarketDataService.get_historical_data(symbol, "1M")
    |       |
    |       +-->> yfinance.Ticker("{SYMBOL}.NS").history(period, interval)
    |              (labels[], prices[], volumes[])
    |
    +-->> StockAgent.analyze(quote, fundamentals)
    |       |
    |       +-- [If AI_API_KEY set] --> AIService.analyze_stock(data)
    |       |       |
    |       |       +-->> Anthropic Claude API
    |       |              (system prompt + stock data -> JSON response)
    |       |
    |       +-- [Else / Fallback] --> StockAgent._rule_based_analysis(data)
    |               (P/E, ROE, debt scoring -> scores + classification)
    |
    +-->> Stock.objects.update_or_create(symbol)  [cache snapshot]
    |
    +-->> Render "stocks/analysis_detail.html"
            (quote, fundamentals, historical_json, analysis)
```

### 3B. IPO Center Flow

```
User (Browser)
    |
    |  GET /ipo/
    v
ipo.views.ipo_center_view()
    |
    +-->> IPO.objects.filter(status="OPEN")  [DB query]
    |
    |    Classify: lot_size x price_band_max
    |       > Rs.15,000 -> SME
    |       <= Rs.15,000 -> Mainboard
    |
    +-->> IPOAnalysisService.get_ranked_ipos(sme_ipos)
    |       |
    |       +-->> IPOAgent.build_ranking_analysis(ipo_data)
    |               |
    |               +-- _fundamental_score()  (revenue, profit, debt)
    |               +-- _gmp_score()          (GMP vs price band)
    |               +-- _subscription_score() (total subscription times)
    |               +-- _valuation_score()    (price vs revenue/profit)
    |               +-- _risk_score()         (profit, debt, subscription)
    |               +-- weighted overall_score -> classification
    |
    +-->> Same for upcoming_ipos, recently_listed_ipos
    |
    +-->> Render "ipo/ipo_center.html"

User clicks IPO detail
    |
    |  GET /ipo/<slug>/
    v
ipo.views.ipo_detail_view(slug)
    |
    +-->> IPO.objects.get(slug=slug)
    +-->> IPOAnalysisService.analyze_ipo(ipo)
    |       +-->> IPOAgent.analyze(ipo_data)
    +-->> IPOAnalysis.objects.create(...)      [persist result]
    +-->> AIAnalysisLog.objects.create(...)    [log activity]
    +-->> Render "ipo/ipo_detail.html"
```

### 3C. Money Planner Flow

```
User (Browser)
    |
    |  GET /investments/
    v
investments.views.home()
    +-->> InvestorProfile, InvestmentGoal, MoneyPlan [DB queries]

Risk Assessment:
    |  POST /investments/risk-assessment/
    v
investments.views.risk_assessment()
    +-->> RiskQuestionnaireForm (8 questions)
    +-->> calculate_risk_score(answers)  -> score (0-100)
    +-->> risk_score_to_level(score)     -> "CONSERVATIVE" .. "AGGRESSIVE"
    +-->> InvestorProfile.objects.update(risk_tolerance, risk_score)

Plan Generation:
    |  POST /investments/generate-plan/
    v
investments.views.generate_plan_view()
    |
    +-->> generate_plan(profile, goals)
    |       |
    |       +-->> get_allocation_profile(risk_level)
    |       |       (equity%, debt%, gold%, cash%, expected_return%)
    |       |
    |       +-->> build_sip_breakdown(equity, debt, gold, cash, total_sip)
    |       |       (Nifty 50 Index, Flexi Cap, Mid Cap, etc.)
    |       |
    |       +-->> calculate_sip_for_goal(target, return%, years) [per goal]
    |       +-->> calculate_sip_fv(sip, return%, years)           [corpus]
    |       +-->> build_projection_table(sip, return%)            [20yr]
    |
    +-->> MoneyPlan.objects.create(...)
    +-->> SIPEntry.objects.create(...)        [per category]
    +-->> GoalProjection.objects.create(...)  [per goal]
    +-->> redirect -> /investments/plan/<id>/
```

### 3D. Watchlist Flow (NOT WIRED)

```
User (Browser)
    |
    |  GET /watchlist/  (app not in INSTALLED_APPS)
    v
watchlist.views.watchlist_home()
    |
    +-->> WatchlistItem.objects.filter(user)
    +-->> For each item:
    |       MarketDataService.get_stock_quote(symbol)
    |       Calculate change, change_pct
    |       PriceAlert.objects.filter(user, symbol, ACTIVE)
    |
    +-->> Render "watchlist/watchlist_home.html"

Price Alerts:
    +-->> PriceAlert (symbol, alert_type, target_price)
    +-->> check_alerts() -> compare live prices -> mark TRIGGERED
```

## 4. Database Schema (Entity Relationships)

```
+-------------------+       +------------------------+
|   auth.User       |       |  accounts.UserProfile   |
|-------------------|       |------------------------|
| id (PK)           |<-1:1->| user_id (FK -> User)   |
| username          |       | full_name              |
| email             |       | age                    |
| password          |       | created_at / updated_at|
+--------+----------+       +------------------------+
         |
         | 1:N (multiple models reference User)
         |
         +------+--------+--------+--------+--------+
         |      |        |        |        |        |
         v      v        v        v        v        v
    AIAnalysis  Stock  Stock   IPO     Investor  Watchlist
    Log         Search AnalysisAnalysis Profile  Item
```

### Models by App:

**accounts** (2 models):
- `UserProfile` -- OneToOne to User: full_name, age

**dashboard** (1 model):
- `AIAnalysisLog` -- FK to User: activity_type, title, description, reference_id

**stocks** (3 models):
- `Stock` -- symbol (unique), company_name, sector, industry, last_quote (JSON), last_fundamentals (JSON)
- `StockSearch` -- FK to User: symbol, created_at
- `StockAnalysis` -- FK to User + Stock: scores (fundamental/technical/growth/risk/overall 0-100), strengths/weaknesses/opportunities/risks (JSON[]), classification, source (ai/rule_based)

**ipo** (2 models):
- `IPO` -- company_name, slug (unique), status, industry, price_band, dates, gmp, subscription, financials, official_source_url
- `IPOAnalysis` -- FK to User + IPO: scores (fundamental/gmp/subscription/valuation/risk/overall 0-100), classification, assessment, strengths/weaknesses/risks (JSON[])

**investments** (5 models):
- `InvestorProfile` -- OneToOne to User: age, income, expenses, risk_tolerance (5 levels), risk_score
- `InvestmentGoal` -- FK to User: goal_type (9 choices), target_amount, target_years, priority
- `MoneyPlan` -- FK to User + InvestorProfile: allocation %, total_monthly_sip, projected_corpus (5/10/15/20y)
- `SIPEntry` -- FK to MoneyPlan: category, allocation_pct, monthly_amount, suggested_return_pct
- `GoalProjection` -- FK to MoneyPlan + InvestmentGoal: monthly_sip_needed, projected_amount, shortfall

**watchlist** (2 models):
- `WatchlistItem` -- FK to User: symbol, company_name, UNIQUE(user, symbol)
- `PriceAlert` -- FK to User: symbol, alert_type (ABOVE/BELOW), target_price, status

## 5. Authentication Architecture

```
+--------------------------------------------------+
|              AUTHENTICATION SYSTEM                 |
|                                                    |
|  Dual Authentication Backend:                      |
|  1. accounts.backends.EmailBackend                |
|     (email-based Django auth -- primary)           |
|  2. django.contrib.auth.backends.ModelBackend      |
|     (standard username auth -- fallback)           |
|                                                    |
|  Clerk SSO Integration (Additional):               |
|  POST /clerk-login/                                |
|  |-- Verify Clerk session token                    |
|  |-- Fetch Clerk user profile                      |
|  |-- Find/create Django user by email              |
|  +-- login() -> Django session                     |
|                                                    |
|  Security Controls:                                |
|  * CSRF protection on all forms                    |
|  * Session cookie HttpOnly                         |
|  * CSRF cookie HttpOnly                            |
|  * X-Frame-Options: DENY                           |
|  * All views @login_required (except auth)         |
|  * Password validators (min, common, numeric)      |
|  * Remember me: 30-day session                     |
|  * No remember me: session expires on browser close|
+--------------------------------------------------+
```

## 6. Agent-Service Architecture Pattern

```
+==================================================+
|                   AGENT LAYER                     |
|                                                   |
|  StockAgent (agents/stock_agent.py)              |
|  |-- analyze(quote, fundamentals) -> dict        |
|  |-- Tries AIService first (if configured)       |
|  |-- Falls back to _rule_based_analysis()        |
|  +-- Returns: scores, strengths, weaknesses,     |
|               classification                     |
|                                                   |
|  IPOAgent (agents/ipo_agent.py)                  |
|  |-- analyze(ipo_data) -> dict                   |
|  |-- Pure rule-based (no AI dependency)          |
|  |-- Scores: fundamental, gmp, subscription,     |
|  |           valuation, risk                     |
|  +-- Returns: scores, strengths, weaknesses,     |
|               classification                     |
+==================================================+
|                  SERVICE LAYER                    |
|                                                   |
|  AIService (services/ai_service.py)              |
|  |-- Wraps Anthropic Claude API                  |
|  |-- generate_json(system_prompt, user_prompt)   |
|  |-- analyze_stock(stock_data) -> dict           |
|  +-- is_configured: bool (AI_API_KEY present)    |
|                                                   |
|  MarketDataService (services/market_data_service)|
|  |-- Wraps yfinance (NSE stocks: SYMBOL.NS)      |
|  |-- search_stock(query) -> dict                 |
|  |-- get_stock_quote(symbol) -> dict             |
|  |-- get_stock_fundamentals(symbol) -> dict      |
|  +-- get_historical_data(symbol, period) -> dict |
|                                                   |
|  IPODataService (services/ipo_data_service.py)   |
|  |-- Wraps Upstox IPO API                        |
|  |-- get_all_ipos() / get_open_ipos() / etc.     |
|  |-- sync_ipos_to_database() -> int              |
|  +-- Maps Upstox JSON -> Django IPO model        |
|                                                   |
|  investments/services.py                         |
|  |-- Allocation engine (5 risk profiles)         |
|  |-- SIP sub-allocation rules                    |
|  |-- Risk questionnaire scoring (8 questions)    |
|  |-- SIP/Lumpsum calculators                     |
|  +-- Full plan generator                         |
+==================================================+
```

## 7. URL Routing Summary

| URL Pattern | App | View | Method | Description |
|---|---|---|---|---|
| `/` | accounts | login_view | GET/POST | Login page |
| `/register/` | accounts | register_view | GET/POST | Registration |
| `/logout/` | accounts | logout_view | POST | Logout |
| `/profile/` | accounts | profile_view | GET/POST | Profile management |
| `/password-change/` | accounts | PasswordChangeView | GET/POST | Change password |
| `/password-reset/` | accounts | PasswordResetView | GET/POST | Reset password |
| `/clerk-login/` | accounts | clerk_login_view | POST | Clerk SSO login |
| `/dashboard/` | dashboard | home | GET | Dashboard home |
| `/stocks/` | stocks | stock_search | GET | Stock search |
| `/stocks/<symbol>/` | stocks | analysis_detail | GET | Stock analysis |
| `/stocks/<symbol>/save/` | stocks | save_analysis | POST | Save analysis |
| `/stocks/compare/` | stocks | compare_stocks | GET | Stock comparison |
| `/ipo/` | ipo | ipo_center_view | GET | IPO center |
| `/ipo/<slug>/` | ipo | ipo_detail_view | GET | IPO detail |
| `/ipo/<id>/save/` | ipo | save_ipo_analysis | POST | Save IPO analysis |
| `/ipo/<id>/saved/` | ipo | saved_ipo_analysis | GET | Saved IPO analysis |
| `/investments/` | investments | home | GET | Money Planner home |
| `/investments/risk-assessment/` | investments | risk_assessment | GET/POST | Risk questionnaire |
| `/investments/profile-setup/` | investments | profile_setup | GET/POST | Financial profile |
| `/investments/goals/` | investments | goals | GET/POST | Investment goals |
| `/investments/goals/<id>/edit/` | investments | goal_edit | GET/POST | Edit goal |
| `/investments/goals/<id>/delete/` | investments | goal_delete | POST | Delete goal |
| `/investments/generate-plan/` | investments | generate_plan | POST | Generate plan |
| `/investments/plan/<id>/` | investments | plan_result | GET | View plan |
| `/investments/plan/<id>/save/` | investments | save_plan | POST | Save plan |
| `/investments/saved-plans/` | investments | saved_plans | GET | Saved plans |
| `/investments/sip-calculator/` | investments | sip_calculator | GET/POST | SIP calculator |
| `/investments/lumpsum-calculator/` | investments | lumpsum_calculator | GET/POST | Lumpsum calculator |
| `/investments/mf-vs-fd/` | investments | mf_vs_fd | GET | MF vs FD education |
| `/investments/funds/` | investments | funds_explore | GET | Fund explorer |
| `/investments/funds/compare/` | investments | funds_compare | GET/POST | Fund comparison |
| `/investments/chart/<id>/` | investments | plan_chart_data | GET | Chart data API |

## 8. External Integrations

```
+==========================================================+
|              EXTERNAL API INTEGRATIONS                     |
|                                                            |
|  1. ANTHROPIC CLAUDE API                                   |
|     Env: AI_API_KEY                                        |
|     Model: claude-sonnet-4-6 (default)                     |
|     Used by: AIService -> StockAgent                       |
|     Purpose: AI-powered stock analysis                     |
|     Output: JSON with scores, strengths, weaknesses        |
|     Fallback: Rule-based analysis in StockAgent            |
|                                                            |
|  2. YAHOO FINANCE (yfinance)                               |
|     Env: None (free, no API key needed)                    |
|     Used by: MarketDataService                             |
|     Purpose: NSE stock quotes, fundamentals, history       |
|     Stocks: {SYMBOL}.NS (NSE suffix)                       |
|                                                            |
|  3. UPSTOX IPO API                                         |
|     Env: IPO_API_KEY                                       |
|     Used by: IPODataService                                |
|     Purpose: IPO data synchronization                      |
|     Endpoints: /v2/ipos (list + detail)                    |
|     Sync: upcoming, open, closed, listed statuses          |
|                                                            |
|  4. CLERK AUTH API                                         |
|     Env: CLERK_SECRET_KEY, CLERK_PUBLISHABLE_KEY           |
|     Used by: accounts/views.py (clerk_login_view)          |
|     Purpose: SSO/social login (additional auth method)     |
|     Flow: Verify token -> get user -> create/login Django  |
+==========================================================+
```

## 9. Configuration Architecture

```
+==========================================================+
|              ENVIRONMENT CONFIGURATION                     |
|                                                            |
|  .env file:                                                |
|    SECRET_KEY        -> Django secret key                  |
|    DEBUG             -> True/False                         |
|    ALLOWED_HOSTS     -> 127.0.0.1,localhost                |
|    AI_API_KEY        -> Anthropic Claude (optional)        |
|    AI_MODEL          -> claude-sonnet-4-6 (default)        |
|    MARKET_API_KEY    -> Reserved for future use            |
|    IPO_API_KEY       -> Upstox API token                   |
|    IPO_API_URL       -> Upstox API endpoint                |
|    CLERK_SECRET_KEY  -> Clerk auth (optional)              |
|    CLERK_PUBLISHABLE_KEY -> Clerk auth (optional)          |
|    DATABASE_URL      -> Production DB (optional)           |
|                                                            |
|  Key Settings (config/settings.py):                        |
|    TIMEZONE: Asia/Kolkata                                  |
|    DATABASE: SQLite3 (dev)                                 |
|    AUTH_BACKENDS: EmailBackend + ModelBackend              |
|    EMAIL_BACKEND: console (dev)                            |
|    STATIC_URL: static/                                     |
|    LOGIN_URL: accounts:login                               |
|    LOGIN_REDIRECT_URL: dashboard:home                      |
+==========================================================+
```

## 10. Key Architectural Patterns

### Pattern 1: Agent-Service Separation
Analysis logic is separated into `agents/` (business logic) and `services/` (API communication). Agents never call external APIs directly.

### Pattern 2: Dual-Mode AI with Graceful Fallback
StockAgent tries AI analysis first, then falls back to rule-based scoring. IPOAgent is purely rule-based. Both produce the same output schema.

### Pattern 3: Educational Framing
Every analysis, score, and recommendation includes disclaimers. No output is presented as financial advice.

### Pattern 4: Activity Logging
AIAnalysisLog tracks all significant user actions (stock analysis, IPO analysis, investment plans, education views) for the dashboard.

### Pattern 5: Cached Stock Snapshots
Stock model caches last_quote and last_fundamentals as JSON fields to avoid repeated API calls.

### Pattern 6: Risk-Based Asset Allocation
5 risk profiles (Conservative to Aggressive) map to asset allocation percentages, which then break down into SIP sub-categories.

## 11. Issues and Gaps

1. **watchlist app not wired** -- Has full code but NOT in INSTALLED_APPS or config/urls.py
2. **education app is empty** -- Placeholder with no models/views
3. **No tests** -- tests/ directory exists but is empty
4. **No deployment config** -- No Docker, CI/CD, or production setup
5. **No caching layer** -- No Redis/cache for market data or API responses
6. **No background tasks** -- IPO sync and alert checking are synchronous
7. **No rate limiting** -- yfinance and Upstox API calls have no throttling
8. **SQLite only** -- No production database configuration
9. **Unused env vars** -- VIDEO_API_KEY, MARKET_API_KEY reserved but unused

## 12. Technology Stack Summary

| Layer | Technology | Version |
|---|---|---|
| Language | Python | 3.14 |
| Framework | Django | 5.0.6 |
| REST API | Django REST Framework | 3.15.1 |
| Database | SQLite3 | (dev) |
| AI | Anthropic Claude | 1.4.0 |
| Market Data | yfinance | 1.7.0 |
| IPO Data | Upstox API + requests | 2.32.3 |
| HTML Parsing | beautifulsoup4 + lxml | 4.15.0 / 6.1.3 |
| Auth | Django Auth + Clerk | 7.0.0 |
| Frontend CSS | Bootstrap | 5.3.3 |
| Frontend Icons | Bootstrap Icons | 1.11.3 |
| Data Validation | Pydantic | 2.13.5 |
| HTTP Client | httpx | 0.28.1 |
| JWT | PyJWT | 2.13.0 |
| Crypto | cryptography | 50.0.1 |
