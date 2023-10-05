import os.path

from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    '127.0.0.1',
    'skarnik.play.of.by',
]

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
