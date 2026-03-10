from django.test import TestCase
from django.db import IntegrityError

from main.models import Word


class WordModelTestCase(TestCase):
    """Tests for the Word model."""

    def setUp(self):
        """Set up test data."""
        self.word_data = {
            'external_id': 123,
            'letter': 'А',
            'direction': 'be-ru',
            'text': 'Слова',
            'translation': '<p>Translation</p>',
            'redirect_to': None,
            'stress': 'Сло́ва',
        }

    def test_create_word(self):
        """Test creating a Word instance."""
        word = Word.objects.create(**self.word_data)
        self.assertEqual(word.text, 'Слова')
        self.assertEqual(word.external_id, 123)
        self.assertEqual(word.letter, 'А')
        self.assertEqual(word.direction, 'be-ru')

    def test_str_method(self):
        """Test the __str__ method."""
        word = Word.objects.create(**self.word_data)
        self.assertEqual(str(word), f'({word.pk}) Слова')

    def test_to_typesense_method(self):
        """Test the to_typesense method returns correct dict."""
        word = Word.objects.create(**self.word_data)
        typesense_data = word.to_typesense()
        
        self.assertEqual(typesense_data['id'], str(word.pk))
        self.assertEqual(typesense_data['external_id'], 123)
        self.assertEqual(typesense_data['letter'], 'А')
        self.assertEqual(typesense_data['direction'], 'be-ru')
        self.assertEqual(typesense_data['text'], 'Слова')
        self.assertEqual(typesense_data['translation'], '<p>Translation</p>')

    def test_unique_together_constraint(self):
        """Test unique_together constraint on external_id and direction."""
        Word.objects.create(**self.word_data)
        
        # Try to create duplicate - should raise IntegrityError
        with self.assertRaises(IntegrityError):
            Word.objects.create(**self.word_data)

    def test_optional_fields(self):
        """Test that redirect_to and stress are optional."""
        word_data = {
            'external_id': 456,
            'letter': 'Б',
            'direction': 'ru-be',
            'text': 'Тест',
            'translation': '<p>Test</p>',
        }
        word = Word.objects.create(**word_data)
        self.assertIsNone(word.redirect_to)
        self.assertIsNone(word.stress)

    def test_verbose_names(self):
        """Test verbose_name and verbose_name_plural."""
        self.assertEqual(Word._meta.verbose_name, 'Слова')
        self.assertEqual(Word._meta.verbose_name_plural, 'Словы')
