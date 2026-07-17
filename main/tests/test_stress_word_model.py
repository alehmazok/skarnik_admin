from django.db import IntegrityError
from django.test import TestCase

from main.models import StressWord


class StressWordModelTestCase(TestCase):
    def setUp(self):
        self.stress_word = StressWord.objects.create(
            word="рука",
            lemma="рука́",
            table_name="Nouns",
            source_pdg_id=1000001,
            rows=[{"title": "Назоўны", "content": "рука́"}],
        )

    def test_creation(self):
        self.assertEqual(self.stress_word.word, "рука")
        self.assertEqual(self.stress_word.lemma, "рука́")
        self.assertEqual(self.stress_word.table_name, "Nouns")
        self.assertEqual(self.stress_word.source_pdg_id, 1000001)
        self.assertEqual(self.stress_word.rows, [{"title": "Назоўны", "content": "рука́"}])

    def test_str(self):
        self.assertEqual(str(self.stress_word), "рука́")

    def test_source_pdg_id_uniqueness(self):
        with self.assertRaises(IntegrityError):
            StressWord.objects.create(
                word="іншы",
                lemma="і́ншы",
                table_name="Adjectives",
                source_pdg_id=1000001,
                rows=[],
            )

    def test_verbose_name(self):
        self.assertEqual(StressWord._meta.verbose_name, "Слова з націскам")
        self.assertEqual(StressWord._meta.verbose_name_plural, "Словы з націскам")
