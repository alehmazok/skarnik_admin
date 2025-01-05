import typesense
from django.conf import settings
from django.core.management.base import BaseCommand

from main.models import Word


class Command(BaseCommand):
    chunk_size = 1000

    client = typesense.Client({
        'nodes': [{
            'host': 'localhost',  # For Typesense Cloud use xxx.a1.typesense.net
            'port': '8108',  # For Typesense Cloud use 443
            'protocol': 'http'  # For Typesense Cloud use https
        }],
        'api_key': settings.TYPESENSE_KEY,
        'connection_timeout_seconds': 2
    })

    schema = {
        'name': 'words',
        'fields': [
            {
                'name': 'id',
                'type': 'string',
            },
            {
                'name': 'external_id',
                'type': 'int32',
                'index': False,
            },
            {
                'name': 'letter',
                'type': 'string',
                'index': False,
            },
            {
                'name': 'direction',
                'type': 'string',
                'index': False,
            },
            {
                'name': 'text',
                'type': 'string',
                'index': True,
                'sort': True,
                'locale': 'be',
            },
            {
                'name': 'translation',
                'type': 'string',
                'index': True,
                'locale': 'be',
            },
        ],
    }

    def handle(self, *args, **options):
        self.stdout.write('Retrieving Typesense collections.')
        collections = self.client.collections.retrieve()
        self.stdout.write('Collections exist.')
        if collections:
            self.stdout.write('Deleting collection `words`.')
            self.client.collections['words'].delete()
        self.client.collections.create(self.schema)
        self.stdout.write('New `words` collection successfully created.')

        handled = 0
        words = Word.objects.all()
        for i in range(0, len(words), self.chunk_size):
            chunk = list(map(lambda w: w.to_typesense(), words[i:i + self.chunk_size]))
            result = self.client.collections['words'].documents.import_(chunk, {'action': 'create'})
            if not all(map(lambda r: r['success'], result)):
                self.stderr.write(str(list(map(lambda r: r['error'], result))), ending='\n')
                exit(1)
            # self.stdout.write(str(result), ending='\n')
            handled += len(result)
            self.stdout.write(f'Synced {handled} words.')
        self.stdout.write('All words synced.')
