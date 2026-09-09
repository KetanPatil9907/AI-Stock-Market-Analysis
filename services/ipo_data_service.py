import os
import requests
from datetime import datetime
from decimal import Decimal, InvalidOperation

from dotenv import load_dotenv
from django.utils.text import slugify

from ipo.models import IPO

load_dotenv()


class IPODataService:

    @staticmethod
    def _request():
        api_key = os.getenv("IPO_API_KEY")
        api_url = os.getenv("IPO_API_URL")

        if not api_key:
            print("IPO API key is missing.")
            return []

        if not api_url:
            print("IPO API URL is missing.")
            return []

        headers = {
            "X-API-Key": api_key
        }

        try:
            response = requests.get(
                api_url,
                headers=headers,
                timeout=20
            )

            response.raise_for_status()

            result = response.json()

            if isinstance(result, dict):
                data = result.get("data", [])

                if isinstance(data, list):
                    return data

            if isinstance(result, list):
                return result

            return []

        except requests.RequestException as e:
            print("IPO API Error:", e)
            return []

        except ValueError as e:
            print("IPO JSON Error:", e)
            return []

    @classmethod
    def get_all_ipos(cls):
        return cls._request()
    
    @classmethod
    def sync_ipos_to_database(cls):
        """
        Fetch IPOs from FinAPI and synchronize them
        with the Django IPO database.
        """

        ipos = cls.get_all_ipos()

        if not ipos:
            print("No IPO data received from FinAPI.")
            return 0

        synced_count = 0

        for item in ipos:
            try:
                company_name = item.get("name", "").strip()

                if not company_name:
                    continue

                symbol = item.get("symbol", "").strip()

                # Convert FinAPI status to Django model status
                api_status = str(
                    item.get("status", "")
                ).upper()

                status_map = {
                    "LIVE": "OPEN",
                    "OPEN": "OPEN",
                    "UPCOMING": "UPCOMING",
                    "CLOSED": "CLOSED",
                    "LISTED": "LISTED",
                }

                status = status_map.get(
                    api_status,
                    "UPCOMING",
                )

                # Price range
                price_min = None
                price_max = None

                price_range = item.get("priceRange", "")

                if price_range:
                    try:
                        clean_price = (
                            price_range
                            .replace("₹", "")
                            .replace(",", "")
                            .strip()
                        )

                        if "–" in clean_price:
                            parts = clean_price.split("–")
                        elif "-" in clean_price:
                            parts = clean_price.split("-")
                        else:
                            parts = [clean_price]

                        price_min = Decimal(
                            parts[0].strip()
                        )

                        if len(parts) > 1:
                            price_max = Decimal(
                                parts[1].strip()
                            )
                        else:
                            price_max = price_min

                    except (ValueError, InvalidOperation):
                        pass

                # Schedule
                schedule = item.get("schedule", {}) or {}

                def parse_date(value):
                    if not value:
                        return None

                    try:
                        return datetime.strptime(
                            value,
                            "%Y-%m-%d"
                        ).date()
                    except (ValueError, TypeError):
                        return None

                open_date = parse_date(
                    schedule.get("startDate")
                )

                close_date = parse_date(
                    schedule.get("endDate")
                )

                allotment_date = parse_date(
                    schedule.get("allotmentFinalization")
                )

                listing_date = parse_date(
                    schedule.get("listingDate")
                )

                lot_size = None

                try:
                    if item.get("lotSize"):
                        lot_size = int(
                            str(item.get("lotSize")).replace(
                                ",", ""
                            )
                        )
                except (ValueError, TypeError):
                    pass

                # Create a stable slug using symbol where possible
                slug_base = symbol or company_name
                base_slug = slugify(slug_base)

                if not base_slug:
                    base_slug = slugify(company_name)

                slug = base_slug

                # Prevent duplicate slug conflicts
                existing = IPO.objects.filter(
                    slug=slug
                ).first()

                if existing and existing.company_name != company_name:
                    slug = slugify(
                        f"{slug_base}-{company_name}"
                    )

                ipo, created = IPO.objects.update_or_create(
                    company_name=company_name,
                    defaults={
                        "slug": slug,
                        "status": status,
                        "price_band_min": price_min,
                        "price_band_max": price_max,
                        "lot_size": lot_size,
                        "open_date": open_date,
                        "close_date": close_date,
                        "allotment_date": allotment_date,
                        "listing_date": listing_date,
                        "exchange": "NSE / BSE",
                        "source_name": "FinAPI",
                        "is_active": True,
                    },
                )

                synced_count += 1

            except Exception as e:
                print(
                    f"Error syncing IPO "
                    f"{item.get('name', 'Unknown')}: {e}"
                )

        print(
            f"FinAPI IPO sync completed: "
            f"{synced_count} IPOs synchronized."
        )

        return synced_count

    @classmethod
    def get_open_ipos(cls):
        ipos = cls._request()

        return [
            ipo for ipo in ipos
            if str(ipo.get("status", "")).upper() == "LIVE"
        ]

    @classmethod
    def get_active_ipos(cls):
        return cls.get_open_ipos()

    @classmethod
    def get_upcoming_ipos(cls):
        ipos = cls._request()

        return [
            ipo for ipo in ipos
            if str(ipo.get("status", "")).upper() == "UPCOMING"
        ]

    @classmethod
    def get_recent_ipos(cls):
        ipos = cls._request()

        return [
            ipo for ipo in ipos
            if str(ipo.get("status", "")).upper()
            in ["LISTED", "CLOSED"]
        ]

    @classmethod
    def get_recently_listed_ipos(cls):
        return cls.get_recent_ipos()

    @classmethod
    def get_all_visible_ipos(cls):
        return cls._request()

    @classmethod
    def get_ipo_details(cls, symbol):
        ipos = cls._request()

        for ipo in ipos:
            if str(ipo.get("symbol", "")).upper() == symbol.upper():
                return ipo

        return None