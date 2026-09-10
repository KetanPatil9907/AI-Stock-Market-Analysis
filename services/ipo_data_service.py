import os
import requests

from datetime import datetime
from decimal import Decimal, InvalidOperation

from dotenv import load_dotenv
from django.utils.text import slugify

from ipo.models import IPO


load_dotenv()


class IPODataService:

    BASE_URL = os.getenv(
        "IPO_API_URL",
        "https://api.upstox.com/v2/ipos"
    )

    @staticmethod
    def _headers():
        token = os.getenv("IPO_API_KEY")

        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        }

    # =========================================================
    # GET IPO LIST
    # =========================================================

    @classmethod
    def _get_ipo_list(cls, status=None):

        params = {
            "page_number": 1,
            "records": 30,
        }

        if status:
            params["status"] = status

        try:

            response = requests.get(
                cls.BASE_URL,
                headers=cls._headers(),
                params=params,
                timeout=20,
            )

            response.raise_for_status()

            result = response.json()

            if result.get("status") == "success":

                return result.get("data", [])

            print("Upstox API Error:", result)

            return []

        except requests.RequestException as e:

            print("Upstox Request Error:", e)

            return []

        except ValueError as e:

            print("Upstox JSON Error:", e)

            return []

    # =========================================================
    # GET IPO DETAILS
    # =========================================================

    @classmethod
    def _get_ipo_details(cls, ipo_id):

        url = f"{cls.BASE_URL}/{ipo_id}"

        try:

            response = requests.get(
                url,
                headers=cls._headers(),
                timeout=20,
            )

            response.raise_for_status()

            result = response.json()

            if result.get("status") == "success":

                return result.get("data")

            print(
                f"Upstox detail error for {ipo_id}:",
                result
            )

            return None

        except requests.RequestException as e:

            print(
                f"Upstox detail request error for {ipo_id}:",
                e
            )

            return None

        except ValueError as e:

            print(
                f"Upstox detail JSON error for {ipo_id}:",
                e
            )

            return None

    # =========================================================
    # GET ALL IPOs
    # =========================================================

    @classmethod
    def get_all_ipos(cls):

        all_ipos = {}

        statuses = [
            "upcoming",
            "open",
            "closed",
            "listed",
        ]

        for status in statuses:

            ipo_list = cls._get_ipo_list(status)

            for ipo in ipo_list:

                ipo_id = ipo.get("id")

                if ipo_id:
                    all_ipos[ipo_id] = ipo

        return list(all_ipos.values())

    # =========================================================
    # GET OPEN IPOs
    # =========================================================

    @classmethod
    def get_open_ipos(cls):

        return cls._get_ipo_list("open")

    # =========================================================
    # GET UPCOMING IPOs
    # =========================================================

    @classmethod
    def get_upcoming_ipos(cls):

        return cls._get_ipo_list("upcoming")

    # =========================================================
    # GET CLOSED IPOs
    # =========================================================

    @classmethod
    def get_closed_ipos(cls):

        return cls._get_ipo_list("closed")

    # =========================================================
    # GET LISTED IPOs
    # =========================================================

    @classmethod
    def get_listed_ipos(cls):

        return cls._get_ipo_list("listed")

    # =========================================================
    # GET RECENT IPOs
    # =========================================================

    @classmethod
    def get_recent_ipos(cls):

        return cls.get_listed_ipos()

    # =========================================================
    # GET IPO BY SYMBOL
    # =========================================================

    @classmethod
    def get_ipo_details(cls, symbol):

        ipos = cls.get_all_ipos()

        for ipo in ipos:

            if str(
                ipo.get("symbol", "")
            ).upper() == symbol.upper():

                ipo_id = ipo.get("id")

                if ipo_id:

                    return cls._get_ipo_details(
                        ipo_id
                    )

                return ipo

        return None

    # =========================================================
    # DATE CONVERSION
    # =========================================================

    @staticmethod
    def _parse_date(value):

        if not value:
            return None

        try:

            return datetime.strptime(
                value,
                "%Y-%m-%d"
            ).date()

        except (ValueError, TypeError):

            return None

    # =========================================================
    # DECIMAL CONVERSION
    # =========================================================

    @staticmethod
    def _decimal(value):

        if value is None:
            return None

        try:

            return Decimal(str(value))

        except (
            InvalidOperation,
            ValueError,
            TypeError,
        ):

            return None

    # =========================================================
    # STATUS MAPPING
    # =========================================================

    @staticmethod
    def _map_status(status):

        mapping = {
            "upcoming": "UPCOMING",
            "open": "OPEN",
            "closed": "CLOSED",
            "listed": "LISTED",
        }

        return mapping.get(
            str(status).lower(),
            "UPCOMING",
        )

    # =========================================================
    # SYNC UPSTOX → DJANGO DATABASE
    # =========================================================

    @classmethod
    def sync_ipos_to_database(cls):

        print("Starting Upstox IPO synchronization...")

        all_ipos = cls.get_all_ipos()

        print(
            f"Found {len(all_ipos)} IPOs from Upstox."
        )

        synchronized = 0

        for index, basic_ipo in enumerate(
            all_ipos,
            start=1
        ):

            ipo_id = basic_ipo.get("id")

            if not ipo_id:
                continue

            print(
                f"[{index}/{len(all_ipos)}] "
                f"Fetching: "
                f"{basic_ipo.get('name')}"
            )

            # Get detailed IPO information
            detail = cls._get_ipo_details(
                ipo_id
            )

            if not detail:

                # Use list response if details fail
                detail = basic_ipo

            company_name = (
                detail.get("name")
                or basic_ipo.get("name")
                or detail.get("symbol")
                or "Unknown IPO"
            )

            symbol = (
                detail.get("symbol")
                or basic_ipo.get("symbol")
                or ""
            )

            # =================================================
            # PRICE
            # =================================================

            price_min = cls._decimal(
                detail.get("minimum_price")
            )

            price_max = cls._decimal(
                detail.get("maximum_price")
            )

            # =================================================
            # DATES
            # =================================================

            open_date = cls._parse_date(
                detail.get("bidding_start_date")
            )

            close_date = cls._parse_date(
                detail.get("bidding_end_date")
            )

            timeline = detail.get(
                "timeline",
                {}
            )

            allotment_date = cls._parse_date(
                timeline.get("allotment_date")
            )

            listing_date = cls._parse_date(
                timeline.get("listing_date")
            )

            # =================================================
            # REGISTRAR
            # =================================================

            registrar_info = detail.get(
                "registrar_info",
                {}
            )

            registrar_name = registrar_info.get(
                "name",
                ""
            )

            # =================================================
            # RHP / DRHP
            # =================================================

            rhp_url = (
                detail.get("rhp_url")
                or detail.get("drhp_url")
                or ""
            )

            # =================================================
            # SOURCE URL
            # =================================================

            official_source_url = (
    rhp_url
    or registrar_info.get("website")
    or "https://upstox.com/"
)

            # =================================================
            # ISSUE TYPE
            # =================================================

            issue_type = str(
                detail.get(
                    "issue_type",
                    ""
                )
            ).lower()

            # Upstox:
            # regular = Mainboard
            # sme = SME
            if issue_type == "sme":

                industry = (
                    detail.get("industry")
                    or ""
                )

            else:

                industry = (
                    detail.get("industry")
                    or ""
                )

            # =================================================
            # SUBSCRIPTION
            # =================================================

            total_subscription = cls._decimal(
                detail.get(
                    "total_subscription"
                )
            )

            # =================================================
            # LOT SIZE
            # =================================================

            lot_size = detail.get(
                "lot_size"
            )

            try:

                if lot_size is not None:

                    lot_size = int(
                        lot_size
                    )

            except (
                ValueError,
                TypeError,
            ):

                lot_size = None

            # =================================================
            # CREATE SLUG
            # =================================================

            slug = slugify(
                f"{company_name}-{symbol}"
            )

            if not slug:

                slug = slugify(
                    company_name
                )

            # =================================================
            # DATABASE UPDATE
            # =================================================

            defaults = {

                "company_name":
                    company_name,

                "status":
                    cls._map_status(
                        detail.get("status")
                    ),

                "industry":
                    industry,

                "exchange":
                    detail.get(
                        "listing_exchange"
                    )
                    or "NSE / BSE",

                "price_band_min":
                    price_min,

                "price_band_max":
                    price_max,

                "issue_size_crore":
                    cls._decimal(
                        detail.get(
                            "issue_size"
                        )
                    ),

                "lot_size":
                    lot_size,

                "open_date":
                    open_date,

                "close_date":
                    close_date,

                "allotment_date":
                    allotment_date,

                "listing_date":
                    listing_date,

                # GMP will come from API 2 later
                "gmp":
                    None,

                "total_subscription":
                    total_subscription,

                # These will come from API 2 later
                "qib_subscription":
                    None,

                "nii_subscription":
                    None,

                "retail_subscription":
                    None,

                # Not provided by Upstox IPO API
                "revenue_crore":
                    None,

                "profit_crore":
                    None,

                "debt_crore":
                    None,

                "fresh_issue_crore":
                    None,

                "offer_for_sale_crore":
                    None,

                "promoter_information":
                    "",

                "business_summary":
                    "",

                "risk_factors":
                    "",

                "official_source_url":
                    official_source_url,

                "source_name":
                    "Upstox",

                "is_active":
                    True,
            }

            # =================================================
            # UPDATE / CREATE
            # =================================================

            ipo, created = (
                IPO.objects.update_or_create(
                    company_name=company_name,
                    defaults={
                        **defaults,
                        "slug": slug,
                    },
                )
            )

            synchronized += 1

        print(
            f"Upstox IPO sync completed: "
            f"{synchronized} IPOs synchronized."
        )

        return synchronized