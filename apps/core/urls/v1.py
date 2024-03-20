# -*- coding: utf-8 -*-
__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

from django.urls import include
from django.urls import path

urlpatterns = [
    path('qr/', include("apps.qr.urls")),
]
