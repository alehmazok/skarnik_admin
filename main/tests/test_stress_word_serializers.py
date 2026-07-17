from django.test import TestCase

from main.models import StressWord
from main.serializers import StressWordDetailSerializer, StressWordListSerializer


class StressWordSerializersTestCase(TestCase):
    def setUp(self):
        self.stress_word = StressWord.objects.create(
            word="рука",
            lemma="рука́",
            table_name="Nouns",
            source_pdg_id=1000001,
            rows=[{"title": "Назоўны", "content": "рука́"}],
        )

    def test_list_serializer_excludes_rows(self):
        data = StressWordListSerializer(self.stress_word).data
        self.assertEqual(set(data.keys()), {"id", "word", "lemma", "table_name"})

    def test_detail_serializer_excludes_word_lemma_table_name(self):
        data = StressWordDetailSerializer(self.stress_word).data
        self.assertEqual(set(data.keys()), {"id", "rows"})
