from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from main.models import Word


class WordByIdRetrieveAPIViewTestCase(APITestCase):
    """Tests for WordByIdRetrieveAPIView."""

    def setUp(self):
        """Set up test data and client."""
        self.word = Word.objects.create(
            external_id=300,
            letter='В',
            direction='be-en',
            text='Вада',
            translation='<p>Water</p>',
        )
        self.client = APIClient()

    def test_get_word_by_id_success(self):
        """Test retrieving a word by primary key."""
        url = f'/api/words/{self.word.pk}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], 'Вада')
        self.assertEqual(response.data['external_id'], 300)

    def test_get_word_by_id_not_found(self):
        """Test retrieving non-existent word returns 404."""
        url = '/api/words/99999/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class WordByExternalIdRetrieveAPIViewTestCase(APITestCase):
    """Tests for WordByExternalIdRetrieveAPIView."""

    def setUp(self):
        """Set up test data and client."""
        self.word1 = Word.objects.create(
            external_id=400,
            letter='Г',
            direction='be-ru',
            text='Горад',
            translation='<p>City</p>',
        )
        self.word2 = Word.objects.create(
            external_id=400,
            letter='Г',
            direction='be-en',
            text='Горад',
            translation='<p>City (English)</p>',
        )
        self.client = APIClient()

    def test_get_word_by_external_id_and_direction_success(self):
        """Test retrieving a word by external_id and direction."""
        url = '/api/words/be-ru/400/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['external_id'], 400)
        self.assertEqual(response.data['direction'], 'be-ru')

    def test_get_word_by_external_id_and_direction_not_found(self):
        """Test retrieving non-existent combination returns 404."""
        url = '/api/words/be-ru/99999/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('not found', response.data['detail'])

    def test_different_directions_return_different_words(self):
        """Test that different directions return different words with same external_id."""
        url_be_ru = '/api/words/be-ru/400/'
        url_be_en = '/api/words/be-en/400/'
        
        response_be_ru = self.client.get(url_be_ru)
        response_be_en = self.client.get(url_be_en)
        
        self.assertEqual(response_be_ru.status_code, status.HTTP_200_OK)
        self.assertEqual(response_be_en.status_code, status.HTTP_200_OK)
        self.assertEqual(response_be_ru.data['direction'], 'be-ru')
        self.assertEqual(response_be_en.data['direction'], 'be-en')
