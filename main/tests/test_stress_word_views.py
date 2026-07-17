from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import StressWord


class StressWordListAPIViewTestCase(APITestCase):
    def setUp(self):
        self.word1 = StressWord.objects.create(
            word="рука",
            lemma="рука́",
            table_name="Nouns",
            source_pdg_id=1000001,
            rows=[{"title": "Назоўны", "content": "рука́"}],
        )
        self.homonym1 = StressWord.objects.create(
            word="пара",
            lemma="па́ра",
            table_name="Nouns",
            source_pdg_id=1021373,
            rows=[{"title": "пара", "content": "па́ра"}],
        )
        self.homonym2 = StressWord.objects.create(
            word="пара",
            lemma="пара́",
            table_name="Nouns",
            source_pdg_id=1179072,
            rows=[{"title": "пара", "content": "пара́"}],
        )
        self.client = APIClient()

    def test_list_by_word_found(self):
        response = self.client.get('/api/stress_words/?word=рука')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['lemma'], 'рука́')

    def test_list_by_word_not_found(self):
        response = self.client.get('/api/stress_words/?word=невядомае')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_list_by_word_case_insensitive(self):
        response = self.client.get('/api/stress_words/?word=РУКА')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['word'], 'рука')

    def test_list_homonyms(self):
        response = self.client.get('/api/stress_words/?word=пара')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        lemmas = {row['lemma'] for row in response.data}
        self.assertEqual(lemmas, {'па́ра', 'пара́'})


class StressWordRetrieveAPIViewTestCase(APITestCase):
    def setUp(self):
        self.stress_word = StressWord.objects.create(
            word="рука",
            lemma="рука́",
            table_name="Nouns",
            source_pdg_id=1000001,
            rows=[{"title": "Назоўны", "content": "рука́"}],
        )
        self.client = APIClient()

    def test_retrieve_found(self):
        response = self.client.get(f'/api/stress_words/{self.stress_word.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rows'], [{"title": "Назоўны", "content": "рука́"}])

    def test_retrieve_not_found(self):
        response = self.client.get('/api/stress_words/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
