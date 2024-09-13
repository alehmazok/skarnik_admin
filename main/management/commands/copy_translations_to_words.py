from django.core.management.base import BaseCommand

from main.models import Word, Translation


class Command(BaseCommand):
    """
    Copy translations to words table.
    """

    n = 500

    def handle(self, *args, **options):
        words = Word.objects.all()
        translations = Translation.objects.all()
        if len(translations) == 0:
            self.stderr.write('Table `translations` is empty. Fill the table before copying.')
            exit(1)
        if len(words) > 0:
            self.stderr.write('Table `words` is not empty. Clear the table before copying.')
            exit(1)

        for i in range(0, len(translations), self.n):
            chunk = list(map(lambda t: t.to_word(), translations[i:i + self.n]))
            Word.objects.bulk_create(chunk)

        self.stdout.write('All translations have been copied to `words`.')
