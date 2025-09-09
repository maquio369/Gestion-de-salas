from .settings import *
import os

DEBUG = False

ALLOWED_HOSTS = ['172.16.35.75', 'localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'gestion_salas'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'HOST': 'db',
        'PORT': '5432',
    }
}

STATIC_ROOT = '/app/staticfiles/'