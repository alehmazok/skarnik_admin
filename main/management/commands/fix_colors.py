import re

from django.core.management.base import BaseCommand
from main.models import Word


class Command(BaseCommand):
    def handle(self, *args, **options):
        words = Word.objects.all()
        for word in words:
            before = word.translation
            # self.stdout.write(f'Before text: {before}')
            replaced = self._replace_color_code(before)
            # self.stdout.write(f'Replaced text: {replaced}')
            word.translation = replaced
            word.save()

    @staticmethod
    def _replace_color_code(text: str) -> str:
        # Regex pattern to match color="008000"
        pattern = r'color:([0-9a-fA-F]{6})'
        # Replacement pattern with a '#' added before the color code
        replacement = r'color:#\1'  # Perform the substitution
        result = re.sub(pattern, replacement, text)
        return result
