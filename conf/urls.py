# -*- coding: utf-8 -*-
__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

from django.urls import (
    include,
    path,
)

urlpatterns = [
    path("", include("apps.core.urls")),
]
