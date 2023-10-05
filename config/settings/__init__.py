import os

from .base import *

mode = os.environ.get('MODE', 'development')

if mode == 'production':
    from .production import *
elif mode == 'testing':
    from .testing import *
else:
    from .development import *
