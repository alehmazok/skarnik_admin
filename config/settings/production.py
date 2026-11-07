import os.path

from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    '127.0.0.1',
    'skarnik.play.of.by',
]

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Sentry error reporting: on only when secrets.json (or the environment) has SENTRY_DSN.
from config.sentry import init_sentry

init_sentry(secrets)
