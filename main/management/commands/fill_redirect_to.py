import re

from django.core.management.base import BaseCommand

from main.models import Word


class Command(BaseCommand):
    """
    Find all words containing single links like "Смотри тут" or "Глядзі тут",
    parse link and write it to the "redirect_to" field.
    """

    def handle(self, *args, **options):
        words = Word.objects.filter(translation__icontains='? <a')
        for word in words:
            href = self._get_a_href(word)
            word.redirect_to = href
            word.save()
            self.stdout.write(f'{word.id}, {word.text}, {href}')
        self.stdout.write(f'All {words.count()} words have been filled.')

    @staticmethod
    def _get_a_href(word: Word) -> list[str]:
        pattern = r'href="(.+)"'
        match = re.search(pattern, word.translation)
        count = len(match.groups())
        assert (
            count == 1,
            f'Must contain only one matched group, but Word({word.id}, {word.text}) contains {count}:\n{word.text}',
        )
        return match.group(1)
