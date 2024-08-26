# -*- coding: utf-8 -*-
__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

from django.utils.translation import gettext_lazy as _

from pathlib import Path
from decouple import config # noqa
from loguru import logger


SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)

INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
ROOT_DIR = BASE_DIR.parent
APPS_DIR = BASE_DIR / 'apps'
LOGS_ROOT = BASE_DIR / 'logs'

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "django_htmx",

    "apps.core",
    "apps.users",
    "apps.qr"
]


# Common settings
# ------------------------------------------------------------------------------

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])
AUTH_USER_MODEL = 'users.User'
WSGI_APPLICATION = 'conf.wsgi.application'
ROOT_URLCONF = 'apps.core.urls'
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

TIME_ZONE = 'Europe/Ljubljana'
LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('ru', _('Russian')),
    ('en', _('English')),
    ('sl', _('Slovenian')),
)
LOCALE_PATHS = (BASE_DIR / 'conf/locale',)

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

CSRF_TRUSTED_ORIGINS = [config('FULL_URL')]


# Middleware
# ------------------------------------------------------------------------------

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'apps.core.middleware.CustomRemoteUserMiddleware',
    'apps.core.middleware.real_ip_middleware',
    'django_htmx.middleware.HtmxMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# Database
# ------------------------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Rest Framework
# ------------------------------------------------------------------------------

DEFAULT_RENDERER_CLASSES = (
    'rest_framework.renderers.JSONRenderer',
)

if DEBUG:
    DEFAULT_RENDERER_CLASSES = DEFAULT_RENDERER_CLASSES + (
        'rest_framework.renderers.BrowsableAPIRenderer',
    )

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        # 'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': DEFAULT_RENDERER_CLASSES
}

# Templates
# ------------------------------------------------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Media
# ------------------------------------------------------------------------------

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = BASE_DIR / 'staticfiles/static'
MEDIA_ROOT = BASE_DIR / 'staticfiles/media'
LOGS_ROOT = BASE_DIR / 'logs'

if not DEBUG:
    STATIC_ROOT = ROOT_DIR / 'nginx/static'
    MEDIA_ROOT = ROOT_DIR / 'nginx/media'
    LOGS_ROOT = ROOT_DIR / 'logs'

STATICFILES_DIRS = [BASE_DIR / 'static', ]

STATICFILES_FINDERS = [
  # First add the two default Finders, since this will overwrite the default.
  'django.contrib.staticfiles.finders.FileSystemFinder',
  'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Logging
# ------------------------------------------------------------------------------
if not DEBUG:
    # Remove the default handler in production
    logger.remove()

logger.add(f"{LOGS_ROOT}/debug.log", filter=lambda record: record["level"].name == "DEBUG")
logger.add(f"{LOGS_ROOT}/info.log", filter=lambda record: record["level"].name == "INFO")
logger.add(f"{LOGS_ROOT}/error.log", filter=lambda record: record["level"].name == "ERROR")
logger.add(f"{LOGS_ROOT}/warning.log", filter=lambda record: record["level"].name == "WARNING")

# Cache
# ------------------------------------------------------------------------------

if not config("REDIS_CACHE_URL", cast=bool, default=False):
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        },
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": config("REDIS_CACHE_URL"),
            "KEY_PREFIX": "django_native_cache",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }


SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

#  Add sentry.io integration
# ------------------------------------------------------------------------------
if not DEBUG and config("SENTRY_DSN", default=None) is not None:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=config("SENTRY_DSN"),
        integrations=[DjangoIntegration()],
        send_default_pii=True,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0
    )
