import requests
from django.core.management.base import BaseCommand
from django.db.models import Func

from main.models import Word


# Custom function to count Belarusian Cyrillic vowels in MariaDB
class CountBelarusianCyrillicVowels(Func):
    template = """
    (
        (LENGTH(%(expressions)s) - LENGTH(REPLACE(%(expressions)s, 'а', ''))) +
        (LENGTH(%(expressions)s) - LENGTH(REPLACE(%(expressions)s, 'е', ''))) +
        (LENGTH(%(expressions)s) - LENGTH(REPLACE(%(expressions)s, 'ё', ''))) +
        (LENGTH(%(expressions)s) - LENGTH(REPLACE(%(expressions)s, 'і', ''))) +
        (LENGTH(%(expressions)s) - LENGTH(REPLACE(%(expressions)s, 'о', ''))) +
        (LENGTH(%(expressions)s) - LENGTH(REPLACE(%(expressions)s, 'у', ''))) +
        (LENGTH(%(expressions)s) - LENGTH(REPLACE(%(expressions)s, 'ы', ''))) +
        (LENGTH(%(expressions)s) - LENGTH(REPLACE(%(expressions)s, 'э', ''))) +
        (LENGTH(%(expressions)s) - LENGTH(REPLACE(%(expressions)s, 'ю', ''))) +
        (LENGTH(%(expressions)s) - LENGTH(REPLACE(%(expressions)s, 'я', ''))) +
        (LENGTH(%(expressions)s) - LENGTH(REPLACE(%(expressions)s, 'А', ''))) +
        (LENGTH(%(expressions)s) - LENGTH(REPLACE(%(expressions)s, 'Е', ''))) +
        (LENGTH(%(expressions)s) - LENGTH(REPLACE(%(expressions)s, 'Ё', ''))) +
        (LENGTH(%(expressions)s) - LENGTH(REPLACE(%(expressions)s, 'І', ''))) +
        (LENGTH(%(expressions)s) - LENGTH(REPLACE(%(expressions)s, 'О', ''))) +
        (LENGTH(%(expressions)s) - LENGTH(REPLACE(%(expressions)s, 'У', ''))) +
        (LENGTH(%(expressions)s) - LENGTH(REPLACE(%(expressions)s, 'Ы', ''))) +
        (LENGTH(%(expressions)s) - LENGTH(REPLACE(%(expressions)s, 'Э', ''))) +
        (LENGTH(%(expressions)s) - LENGTH(REPLACE(%(expressions)s, 'Ю', ''))) +
        (LENGTH(%(expressions)s) - LENGTH(REPLACE(%(expressions)s, 'Я', '')))
    )
    """


class Command(BaseCommand):
    """
    A Django management command that adds stress marks to Belarusian words from the TSBM dictionary.

    This command identifies words that:
    1. Have more than 2 vowels
    2. Currently don't have stress marks
    3. Belong to the 'tsbm' direction (ТСБМ - Тлумачальны слоўнік беларускай мовы)

    The command fetches stress information from starnik.by API and updates the database accordingly.

    Usage:
        python manage.py fill_stress

    The command processes words in batches (currently limited to 2 words per run) and:
    - Queries words matching the criteria using a custom MariaDB function to count Belarusian Cyrillic vowels
    - For each word, makes an API request to starnik.by to fetch stress information
    - Updates the word's stress field in the database if stress information is found

    Classes:
        CountBelarusianCyrillicVowels: A custom database function that counts
            Belarusian Cyrillic vowels in a text field. Supports both upper
            and lower case vowels (а, е, ё, і, о, у, ы, э, ю, я).

    Technical details:
    - Uses requests library for API calls
    - Implements custom MariaDB function for vowel counting
    - Handles HTTP errors and missing API responses gracefully

    Example:
        $ python manage.py fill_stress
        Words without stress: 42
        слова
        Stress: сло́ва
    """

    def handle(self, *args, **options):
        qs = Word.objects.annotate(
            vowel_count=CountBelarusianCyrillicVowels('text'),
        ).filter(
            vowel_count__gt=2,  # if we leave __gt=1 condition it returns words even with one vowel
            stress__isnull=True,
            direction='tsbm',
        )

        self.stdout.write(f'Words without stress: {qs.count()}')

        for w in qs:
            self.stdout.write(f'{w}')
            stress = self._fetch_stress(w.text)
            self.stdout.write(f'Stress: {stress}')
            if stress:
                w.stress = stress
                w.save()

    @staticmethod
    def _fetch_stress(lemma) -> str | None:
        url = "https://starnik.by/api/wordList"
        params = {"lemma": lemma}
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        }

        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
            )
            response.raise_for_status()  # Raise an error for bad HTTP status codes
            data = response.json()  # Parse JSON response

            # Extract the 'word' field value from the first element in 'word_list'
            if "word_list" in data and data["word_list"]:
                first_word = data["word_list"][0]["word"]
                print(f"First word: {first_word}")
                return first_word
            else:
                print("No words found in the 'word_list'.")
                return None

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None
