from pprint import PrettyPrinter

import typesense
from django.conf import settings
from django.core.management.base import BaseCommand
from typesense.exceptions import ObjectNotFound


class Command(BaseCommand):
    client = typesense.Client({
        'nodes': [{
            'host': 'localhost',  # For Typesense Cloud use xxx.a1.typesense.net
            'port': '8108',  # For Typesense Cloud use 443
            'protocol': 'http'  # For Typesense Cloud use https
        }],
        'api_key': settings.TYPESENSE_KEY,
        'connection_timeout_seconds': 2
    })

    def handle(self, *args, **options):
        self.stdout.write('Retrieving Typesense `words` collection.')
        try:
            words_collection = self.client.collections['words'].retrieve()
            self.stdout.write('Collections exist:')
            pp = PrettyPrinter(indent=4)
            result = pp.pformat(words_collection)
            self.stdout.write(result)
        except ObjectNotFound as e:
            self.stderr.write(str(e))
