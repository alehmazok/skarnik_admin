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
    A Django management command that adds stress marks to Belarusian words from the BN Korpus dictionary.

    This command identifies words that:
    1. Have more than 2 vowels
    2. Currently don't have stress marks
    3. Belong to the 'tsbm' direction (ТСБМ - Тлумачальны слоўнік беларускай мовы)

    The command fetches stress information from bnkorpus.info API and updates the database accordingly.

    Usage:
        python manage.py fill_stress_bnk

    The command processes words in batches (currently limited to 2 words per run) and:
    - Queries words matching the criteria using a custom MariaDB function to count Belarusian Cyrillic vowels
    - For each word, makes an API request to bnkorpus.info to fetch stress information
    - Updates the word's stress field in the database if stress information is found
    - Use --print-words option to only print words without making API requests

    Options:
        --dry-run     If set, do not make any API requests to the API.
        --print-words  If set, print all words from the database that match the query.
                      By default, nothing is printed.
        --direction   Required. The direction to filter words by (e.g., 'tsbm').
        --limit       Limit the number of words to process.

    Classes:
        CountBelarusianCyrillicVowels: A custom database function that counts
            Belarusian Cyrillic vowels in a text field. Supports both upper
            and lower case vowels (а, е, ё, і, о, у, ы, э, ю, я).

    Technical details:
    - Uses requests library for API calls
    - Implements custom MariaDB function for vowel counting
    - Handles HTTP errors and missing API responses gracefully

    Example:
        $ python manage.py fill_stress_bnk --direction tsbm
        Words without stress: 42
        слова => сло́ва

        $ python manage.py fill_stress_bnk --direction tsbm --dry-run
        Words without stress: 42

        $ python manage.py fill_stress_bnk --direction tsbm --print-words
        Words without stress: 42
        слова
        апытанне
        ...

        $ python manage.py fill_stress_bnk --direction tsbm --limit 10
        Words without stress: 10
        слова => сло́ва
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--direction',
            type=str,
            required=True,
            help='The direction to filter words by (e.g., tsbm).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Do not make any API requests to the API.',
        )
        parser.add_argument(
            '--print-words',
            action='store_true',
            help='Print all words from the database that match the query, without making any API requests.',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of words to process.',
        )

    def handle(self, *args, **options):
        direction = options['direction']
        dry_run = options['dry_run']
        print_words = options['print_words']
        limit = options['limit']

        qs = Word.objects.annotate(
            vowel_count=CountBelarusianCyrillicVowels('text'),
        ).filter(
            vowel_count__gt=2,  # if we leave __gt=1 condition it returns words even with one vowel
            stress__isnull=True,
            direction=direction,
        ).exclude(
            text__endswith='...'
        )

        if limit:
            qs = qs[:limit]

        self.stdout.write(f'Words without stress: {qs.count()}')

        for w in qs:
            if print_words:
                self.stdout.write(f'{w}')
            elif dry_run:
                pass  # Don't make API requests, don't print
            else:
                stress = self._fetch_stress(w.text)
                if stress:
                    self.stdout.write(f'{w} => {stress}')
                    w.stress = stress
                    w.save()
                else:
                    self.stderr.write(f'{w} => {stress}')

    def _fetch_stress(self, word) -> str | None:
        url = "https://bnkorpus.info/korpus/grammar/search"
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
        }
        data = {
            "fullDatabase": False,
            "grammar": "",
            "lang": "bel",
            "multiForm": False,
            "orderReverse": False,
            "word": word,
        }

        try:
            response = requests.post(
                url,
                json=data,
                headers=headers,
            )
            response.raise_for_status()  # Raise an error for bad HTTP status codes
            data = response.json()  # Parse JSON response

            # Extract the 'output' field value from the first element in 'output'
            if "output" in data and data["output"] and len(data["output"]):
                first_word = data["output"][0]["output"]
                if not first_word:
                    return None
                # first_word = data["output"][0]["word"]
                # print(f"First word: {first_word}")
                return first_word
            else:
                self.stderr.write('No words found in the "output".')
                return None

        except requests.exceptions.RequestException as e:
            self.stderr.write(f'An error occurred: {e}')
            return None
