from .settings import *

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

DATABASES['replica'] = {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': DATABASES['default']['NAME'],
    'USER': DATABASES['default']['USER'],
    'PASSWORD': DATABASES['default']['PASSWORD'],
    'HOST': DATABASES['default']['HOST'],
    'PORT': DATABASES['default']['PORT'],
    'TEST': {
        'MIRROR': 'default',
    }
}