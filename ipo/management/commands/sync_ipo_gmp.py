from django.core.management.base import BaseCommand

from services.gmp_data_service import GmpDataService


class Command(BaseCommand):
    help = (
        "Fetch live IPO grey market premiums (GMP) from "
        "InvestorGain and update the database."
    )

    def handle(self, *args, **options):
        result = GmpDataService.sync_gmp_to_database()

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated GMP for {result['updated']} IPO records "
                f"({len(result['matched'])} live IPOs matched)."
            )
        )

        if result["matched"]:
            self.stdout.write(
                "Matched: " + ", ".join(result["matched"])
            )

        if result["unmatched"]:
            self.stdout.write(
                self.style.WARNING(
                    "Unmatched (no matching IPO in database): "
                    + ", ".join(result["unmatched"])
                )
            )