from django.test import TestCase

from main.models import Word
from main.serializers import WordSerializer


class WordSerializerTestCase(TestCase):
    """Tests for the WordSerializer."""

    def setUp(self):
        """Set up test data."""
        self.word = Word.objects.create(
            external_id=100,
            letter='А',
            direction='be-ru',
            text='Артыкул',
            translation='<p>Article</p>',
            stress='Арты́кул',
        )
        self.serializer = WordSerializer(instance=self.word)

    def test_contains_expected_fields(self):
        """Test serializer contains all expected fields."""
        data = self.serializer.data
        expected_fields = [
            'id', 'external_id', 'letter', 'direction', 
            'text', 'translation', 'redirect_to', 'stress'
        ]
        for field in expected_fields:
            self.assertIn(field, data)

    def test_field_values(self):
        """Test serializer field values match model."""
        data = self.serializer.data
        self.assertEqual(data['external_id'], 100)
        self.assertEqual(data['letter'], 'А')
        self.assertEqual(data['direction'], 'be-ru')
        self.assertEqual(data['text'], 'Артыкул')
        self.assertEqual(data['stress'], 'Арты́кул')

    def test_serializer_create(self):
        """Test serializer can create a Word instance."""
        data = {
            'external_id': 200,
            'letter': 'Б',
            'direction': 'ru-be',
            'text': 'Текст',
            'translation': '<p>Text</p>',
        }
        serializer = WordSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        word = serializer.save()
        
        self.assertEqual(word.external_id, 200)
        self.assertEqual(word.text, 'Текст')

    def test_serializer_update(self):
        """Test serializer can update a Word instance."""
        data = {
            'external_id': 100,
            'letter': 'А',
            'direction': 'be-ru',
            'text': 'Артыкул Абноўлены',
            'translation': '<p>Updated Article</p>',
            'stress': 'Арты́кул',
        }
        serializer = WordSerializer(instance=self.word, data=data)
        self.assertTrue(serializer.is_valid())
        word = serializer.save()
        
        self.assertEqual(word.text, 'Артыкул Абноўлены')
        self.assertEqual(word.translation, '<p>Updated Article</p>')
