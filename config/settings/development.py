from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    '192.168.1.104',
]

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1',
    '192.168.1.104',
]

AUTH_PASSWORD_VALIDATORS = []

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
