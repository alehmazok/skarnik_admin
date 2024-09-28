from django.core.management.base import BaseCommand

from main.models import Word, Translation


class Command(BaseCommand):
    """
    Copy translations to words table.
    """

    chunk_size = 500

    def handle(self, *args, **options):
        self.stdout.write('Starting...')
        count = Translation.objects.count()
        if count  == 0:
            self.stderr.write('Table `translations` is empty. Fill the table before copying.')
            exit(1)
        if Word.objects.count() > 0:
            self.stderr.write('Table `words` is not empty. Clear the table before copying.')
            exit(1)
        self.stdout.write(f'Copying {count} translations...')
        translations = Translation.objects.all()
        for i in range(0, len(translations), self.chunk_size):
            chunk = list(map(lambda t: t.to_word(), translations[i:i + self.chunk_size]))
            Word.objects.bulk_create(chunk)

        self.stdout.write('All translations have been copied to `words`.')
