# -*- coding: utf-8 -*-
__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from apps.core.views import MainPage, favicon
from apps.qr.views import GetSaveQr

api = [
    path("v1/", include("apps.core.urls.v1")),
]

urlpatterns = [
    path("api/", include(api)),
    path("admin/", admin.site.urls),
    path('qr/<str:rnd_id>/', GetSaveQr.as_view(), name='open_qr'),
    path('', MainPage.as_view()),
    path("favicon.ico", favicon),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
