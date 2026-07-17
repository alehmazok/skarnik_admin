from django.core.management.base import BaseCommand
from django.db import connections

from main.models import StressWord
from main.supabase_sync import _client

TABLE = "stress_word"
COLUMNS = "id,word,lemma,table_name,source_pdg_id,rows"


class Command(BaseCommand):
    """
    Import StressWord rows from the Supabase `stress_word` table.
    """

    def add_arguments(self, parser):
        parser.add_argument("--page-size", type=int, default=1000)
        parser.add_argument("--limit", type=int, default=None)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        page_size = options["page_size"]
        limit = options["limit"]
        dry_run = options["dry_run"]

        client = _client()
        start = 0
        fetched = 0
        total_created_or_updated = 0

        while True:
            if limit is not None and fetched >= limit:
                break

            end = start + page_size - 1
            if limit is not None:
                end = min(end, start + (limit - fetched) - 1)

            response = (
                client.table(TABLE)
                .select(COLUMNS)
                .order("id")
                .range(start, end)
                .execute()
            )
            rows = response.data
            if not rows:
                break

            fetched += len(rows)
            self.stdout.write(f"Fetched {len(rows)} rows (total fetched: {fetched})")

            if not dry_run:
                chunk = [
                    StressWord(
                        word=row["word"].lower(),
                        lemma=row["lemma"],
                        table_name=row.get("table_name"),
                        source_pdg_id=row.get("source_pdg_id"),
                        rows=row["rows"],
                    )
                    for row in rows
                ]
                supports_target = connections[
                    StressWord.objects.db
                ].features.supports_update_conflicts_with_target
                StressWord.objects.bulk_create(
                    chunk,
                    batch_size=1000,
                    update_conflicts=True,
                    unique_fields=["source_pdg_id"] if supports_target else None,
                    update_fields=["word", "lemma", "table_name", "rows"],
                )
                total_created_or_updated += len(chunk)

            start += page_size

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"Dry run: would import {fetched} rows."))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Imported/updated {total_created_or_updated} rows.")
            )
