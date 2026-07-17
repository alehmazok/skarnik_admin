import json
import os
from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import TestCase

from main.models import StressWord

FIXTURE_PATH = os.path.join(
    os.path.dirname(__file__), "fixtures", "stress_word_supabase_sample.json"
)


def load_fixture():
    with open(FIXTURE_PATH) as f:
        return json.load(f)


def make_mock_client(rows):
    """Build a mock Supabase client that paginates over `rows` via .range(start, end)."""
    client = MagicMock()

    def execute_side_effect():
        query = client.table.return_value.select.return_value.order.return_value
        start, end = query.range.call_args[0]
        page = rows[start:end + 1]
        response = MagicMock()
        response.data = page
        return response

    query_mock = client.table.return_value.select.return_value.order.return_value
    query_mock.range.return_value.execute.side_effect = execute_side_effect
    return client


class ImportStressWordsFromSupabaseTestCase(TestCase):
    def setUp(self):
        self.rows = load_fixture()

    def _patched_client(self):
        return patch(
            "main.management.commands.import_stress_words_from_supabase._client",
            return_value=make_mock_client(self.rows),
        )

    def test_normal_run_populates_stress_word(self):
        with self._patched_client():
            call_command("import_stress_words_from_supabase", "--page-size", "2", stdout=StringIO())

        self.assertEqual(StressWord.objects.count(), len(self.rows))
        рука = StressWord.objects.get(source_pdg_id=1000001)
        self.assertEqual(рука.word, "рука")
        self.assertEqual(рука.lemma, "рука́")

        homonyms = StressWord.objects.filter(word="пара")
        self.assertEqual(homonyms.count(), 3)
        self.assertEqual(set(homonyms.values_list("lemma", flat=True)), {"па́ра", "пара́"})

    def test_dry_run_writes_nothing(self):
        with self._patched_client():
            call_command(
                "import_stress_words_from_supabase",
                "--dry-run",
                "--page-size", "2",
                stdout=StringIO(),
            )

        self.assertEqual(StressWord.objects.count(), 0)

    def test_rerun_updates_existing_rows_via_upsert(self):
        with self._patched_client():
            call_command("import_stress_words_from_supabase", "--page-size", "2", stdout=StringIO())

        updated_rows = json.loads(json.dumps(self.rows))
        updated_rows[0]["lemma"] = "ру́ка-зменена"

        with patch(
            "main.management.commands.import_stress_words_from_supabase._client",
            return_value=make_mock_client(updated_rows),
        ):
            call_command("import_stress_words_from_supabase", "--page-size", "2", stdout=StringIO())

        self.assertEqual(StressWord.objects.count(), len(self.rows))
        рука = StressWord.objects.get(source_pdg_id=1000001)
        self.assertEqual(рука.lemma, "ру́ка-зменена")

    def test_limit_truncates(self):
        with self._patched_client():
            call_command(
                "import_stress_words_from_supabase",
                "--limit", "2",
                "--page-size", "2",
                stdout=StringIO(),
            )

        self.assertEqual(StressWord.objects.count(), 2)
