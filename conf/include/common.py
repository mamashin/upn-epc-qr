# -*- coding: utf-8 -*-
__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

from decouple import config # noqa
from conf.settings import DEBUG


ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])
AUTH_USER_MODEL = 'users.User'
WSGI_APPLICATION = 'conf.wsgi.application'
ROOT_URLCONF = 'apps.core.urls'
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

TIME_ZONE = 'Europe/Moscow'
LANGUAGE_CODE = 'ru-ru'
LANGUAGES = (
    ('ru', 'Russian'),
    ('en', 'English'),
)

USE_I18N = True
USE_L10N = True
USE_TZ = True


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'apps.core.middleware.CustomRemoteUserBackend',
]

X_FRAME_OPTIONS = 'SAMEORIGIN'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

if DEBUG:
    pass

CSRF_TRUSTED_ORIGINS = ["https://open-crane-painfully.ngrok-free.app"]
