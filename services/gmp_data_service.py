import os
import re

from datetime import datetime
from decimal import Decimal, InvalidOperation

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from ipo.models import IPO


load_dotenv()


class GmpDataService:

    API_URL = (
        "https://webnodejs.investorgain.com/cloud/v2/report/"
        "data-read/331/1/{month}/{year}/0/0/all"
    )

    # Name tokens that add no matching value.
    _DROP_TOKENS = {
        "and",
        "co",
        "company",
        "corp",
        "corporation",
        "india",
        "indian",
        "ipo",
        "limited",
        "llp",
        "ltd",
        "private",
        "pvt",
        "reit",
        "the",
    }

    @classmethod
    def _headers(cls):
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.investorgain.com/",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        }

    # =========================================================
    # FETCH LIVE GMP
    # =========================================================

    @classmethod
    def fetch_live_gmp(cls):
        """Return GMP records from the InvestorGain backend API.

        Each record:
        {
            'company': str,
            'gmp': float|None,
            'gmp_percent': float,
            'price_max': float,
            'lot_size': int|None,
            'close_date': date|None,
            'category': str,
        }
        """
        now = datetime.now()
        url = cls.API_URL.format(
            month=now.month,
            year=now.year,
        )

        try:
            response = requests.get(
                url,
                headers=cls._headers(),
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print("InvestorGain GMP request error:", e)
            return []
        except ValueError as e:
            print("InvestorGain GMP JSON error:", e)
            return []

        records = []

        for item in data.get("reportTableData") or []:
            company = item.get("~ipo_name") or ""
            company = " ".join(company.split())

            if not company:
                continue

            records.append({
                "company": company,
                "gmp": cls._parse_gmp(item.get("GMP")),
                "gmp_percent": cls._to_float(
                    item.get("~gmp_percent_calc")
                ),
                "price_max": cls._to_float(
                    item.get("Price (₹)")
                ),
                "lot_size": cls._to_int(
                    item.get("Lot")
                ),
                "close_date": cls._parse_date(
                    item.get("~Str_Close")
                ),
                "category": item.get("~IPO_Category") or "",
            })

        return records

    # =========================================================
    # PARSING HELPERS
    # =========================================================

    @staticmethod
    def _parse_gmp(gmp_html):
        """Extract the GMP number from InvestorGain HTML.

        Examples:
            '&#8377;<b>228</b> (12.77%)<br>...' -> 228.0
            '&#8377;<b>-15</b> (-2.22%)<br>...' -> -15.0
            '&#8377;<b>--</b> (0.00%)<br>...'   -> None
        """
        if not gmp_html:
            return None

        soup = BeautifulSoup(gmp_html, "html.parser")
        bold = soup.find("b")
        text = (
            bold.get_text(strip=True)
            if bold else soup.get_text(" ", strip=True)
        )

        match = re.search(r"[-+]?\d+(?:\.\d+)?", text)

        if not match:
            return None

        try:
            return float(match.group())
        except ValueError:
            return None

    @staticmethod
    def _to_float(value):
        if value is None:
            return None

        try:
            return float(str(value).strip())
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _to_int(value):
        if value is None:
            return None

        try:
            return int(float(str(value).strip()))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_date(value):
        if not value:
            return None

        for fmt in (
            "%Y-%m-%d",
            "%d-%b",
            "%d-%b-%Y",
        ):
            try:
                return datetime.strptime(
                    str(value).strip(),
                    fmt,
                ).date()
            except (ValueError, TypeError):
                continue

        return None

    # =========================================================
    # NAME MATCHING
    # =========================================================

    @classmethod
    def _normalize_name(cls, name):
        if not name:
            return ""

        name = str(name).lower()
        name = re.sub(r"\(.*?\)", " ", name)
        name = re.sub(r"[^a-z0-9\s-]", " ", name)
        tokens = {
            token
            for token in name.split()
            if token not in cls._DROP_TOKENS
        }

        return " ".join(sorted(tokens))

    @classmethod
    def _names_match(cls, db_name, source_name):
        n1 = cls._normalize_name(db_name)
        n2 = cls._normalize_name(source_name)

        if not n1 or not n2:
            return False

        if n1 == n2:
            return True

        t1 = set(n1.split())
        t2 = set(n2.split())

        if not t1 or not t2:
            return False

        common = t1 & t2
        shorter = min(len(t1), len(t2))

        if len(common) >= shorter:
            return True

        if len(t1) >= 2 and len(t2) >= 2:
            return t1 < t2 or t2 < t1

        return False

    # =========================================================
    # SYNC GMP → DATABASE
    # =========================================================

    @classmethod
    def sync_gmp_to_database(cls):
        records = cls.fetch_live_gmp()

        if not records:
            return {
                "updated": 0,
                "matched": [],
                "unmatched": [],
            }

        # Bucket active IPO names once for fast matching.
        buckets = {}

        for ipo in IPO.objects.filter(is_active=True):
            key = cls._normalize_name(ipo.company_name)

            if not key:
                continue

            buckets.setdefault(key, []).append(ipo)

        updated = 0
        matched_names = []
        unmatched_names = []
        bucket_keys = list(buckets)

        for record in records:
            gmp = record["gmp"]

            # Skip rows without a numeric GMP (shows "--").
            if gmp is None:
                continue

            source_key = cls._normalize_name(record["company"])

            if not source_key:
                unmatched_names.append(record["company"])
                continue

            target = None

            if source_key in buckets:
                target = source_key
            else:
                for key in bucket_keys:
                    if cls._names_match(key, source_key):
                        target = key
                        break

            if not target:
                unmatched_names.append(record["company"])
                continue

            try:
                gmp_decimal = Decimal(str(gmp))
            except (InvalidOperation, ValueError, TypeError):
                unmatched_names.append(record["company"])
                continue

            for ipo in buckets[target]:
                ipo.gmp = gmp_decimal
                ipo.save(update_fields=["gmp", "updated_at"])
                updated += 1

            matched_names.append(record["company"])

        print(
            f"GMP sync completed: {updated} records updated "
            f"across {len(matched_names)} live IPOs."
        )

        return {
            "updated": updated,
            "matched": matched_names,
            "unmatched": unmatched_names,
        }