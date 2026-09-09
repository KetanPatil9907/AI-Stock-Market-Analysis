from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class IPO(models.Model):
    STATUS_CHOICES = [
        ("UPCOMING", "Upcoming"),
        ("OPEN", "Open"),
        ("CLOSED", "Closed"),
        ("LISTED", "Recently Listed"),
    ]

    company_name = models.CharField(max_length=255)

    slug = models.SlugField(
        max_length=280,
        unique=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="UPCOMING",
    )

    industry = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    exchange = models.CharField(
        max_length=50,
        blank=True,
        default="NSE / BSE",
    )

    price_band_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    price_band_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    issue_size_crore = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Issue size in ₹ crore, if available.",
    )

    lot_size = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    open_date = models.DateField(
        null=True,
        blank=True,
    )

    close_date = models.DateField(
        null=True,
        blank=True,
    )

    allotment_date = models.DateField(
        null=True,
        blank=True,
    )

    listing_date = models.DateField(
        null=True,
        blank=True,
    )

    gmp = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            "Unofficial Grey Market Premium. It may change and does not "
            "guarantee listing performance."
        ),
    )

    total_subscription = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Overall subscription in times, for example 2.50.",
    )

    qib_subscription = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    nii_subscription = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    retail_subscription = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    revenue_crore = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Latest available annual revenue in ₹ crore.",
    )

    profit_crore = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Latest available annual profit in ₹ crore.",
    )

    debt_crore = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Latest available debt in ₹ crore.",
    )

    fresh_issue_crore = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
    )

    offer_for_sale_crore = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
    )

    promoter_information = models.TextField(
        blank=True,
        default="",
    )

    business_summary = models.TextField(
        blank=True,
        default="",
    )

    risk_factors = models.TextField(
        blank=True,
        default="",
        help_text="Important risks from official documents, if available.",
    )

    official_source_url = models.URLField(
        blank=True,
        default="",
        help_text="Official exchange, registrar, or offer-document URL.",
    )

    source_name = models.CharField(
        max_length=150,
        blank=True,
        default="",
        help_text="Example: NSE, BSE, registrar, or authorized provider.",
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this IPO from normal users.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            "status",
            "open_date",
            "-created_at",
        ]
        verbose_name = "IPO"
        verbose_name_plural = "IPOs"

    def __str__(self):
        return self.company_name

    @property
    def price_band_display(self):
        if self.price_band_min is None and self.price_band_max is None:
            return "Data unavailable"

        if self.price_band_min == self.price_band_max:
            return f"₹{self.price_band_min}"

        if self.price_band_min is not None and self.price_band_max is not None:
            return f"₹{self.price_band_min} – ₹{self.price_band_max}"

        if self.price_band_min is not None:
            return f"From ₹{self.price_band_min}"

        return f"Up to ₹{self.price_band_max}"


class IPOAnalysis(models.Model):
    CLASSIFICATION_CHOICES = [
        ("POSITIVE", "Positive"),
        ("NEUTRAL", "Neutral"),
        ("HIGH_RISK", "High Risk"),
        ("NEEDS_MORE_RESEARCH", "Needs More Research"),
        ("INSUFFICIENT_DATA", "Insufficient Data"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ipo_analyses",
    )

    ipo = models.ForeignKey(
        IPO,
        on_delete=models.CASCADE,
        related_name="analyses",
    )

    fundamental_score = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    gmp_score = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    subscription_score = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    valuation_score = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    risk_score = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        help_text=(
            "Higher score means lower relative risk in this educational model."
        ),
    )

    overall_score = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    classification = models.CharField(
        max_length=30,
        choices=CLASSIFICATION_CHOICES,
        default="INSUFFICIENT_DATA",
    )

    assessment = models.TextField(blank=True, default="")

    strengths = models.JSONField(default=list)

    weaknesses = models.JSONField(default=list)

    risks = models.JSONField(default=list)

    things_to_check = models.JSONField(default=list)

    analysis_snapshot = models.JSONField(
        default=dict,
        help_text="IPO data supplied to the educational agent.",
    )

    is_saved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "IPO Analysis"
        verbose_name_plural = "IPO Analyses"

    def __str__(self):
        return (
            f"{self.ipo.company_name} - {self.user.username} "
            f"({self.overall_score}/100)"
        )