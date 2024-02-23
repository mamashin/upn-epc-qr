# -*- coding: utf-8 -*-
__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

from decouple import config # noqa

from conf.settings import BASE_DIR, ROOT_DIR, DEBUG

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = BASE_DIR / 'staticfiles/static'
MEDIA_ROOT = BASE_DIR / 'staticfiles/media'
LOGS_ROOT = BASE_DIR / 'logs'

if not DEBUG:
    STATIC_ROOT = ROOT_DIR / 'nginx/static'
    MEDIA_ROOT = ROOT_DIR / 'nginx/media'
    LOGS_ROOT = ROOT_DIR / 'logs'

# STATICFILES_DIRS = [('core', BASE_DIR / 'core/static')]
STATICFILES_DIRS = [BASE_DIR / 'static', ]
# STATICFILES_DIRS = ['/Users/nicko/codes/qr_epc/static', ]

STATICFILES_FINDERS = [
  # First add the two default Finders, since this will overwrite the default.
  'django.contrib.staticfiles.finders.FileSystemFinder',
  # 'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]
