from .settings import *
import os

DEBUG = True

ALLOWED_HOSTS = ['172.16.35.75', 'localhost', '127.0.0.1', 'sag.chiapas.gob.mx']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'salas'),
        'USER': os.environ.get('DB_USER', 'maquio'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'maquio92'),
        'HOST': os.environ.get('DB_HOST', '172.16.35.75'),
        'PORT': os.environ.get('DB_PORT', '32768'),
    }
}

STATIC_ROOT = '/app/staticfiles/'