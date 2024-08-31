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
    path("qr/manual/", MainPage.as_view(), name='qr_manual', kwargs={'mode': 'manual'}),
    path("qr/scan/", MainPage.as_view(), name='qr_scan', kwargs={'mode': 'scan'}),
    path("qr/<str:rnd_id>/edit/", MainPage.as_view(), name='qr_edit', kwargs={'mode': 'edit'}),
    path("qr/<str:rnd_id>/", GetSaveQr.as_view(), name='qr_open', kwargs={'mode': 'open'}),

    path('lang/', MainPage.as_view(), name='main_page_lang', kwargs={'mode': 'lang'}),
    path('', MainPage.as_view(), name='main_page'),

    path("admin/", admin.site.urls),
    path("favicon.ico", favicon),
    path("api/", include(api)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
