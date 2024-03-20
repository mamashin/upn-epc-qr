# -*- coding: utf-8 -*-
__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

from django.urls import path

from .views import PostQr, PostManualForm, GetSaveQr

urlpatterns = [
    path('manual/', PostManualForm.as_view(), name='manual_form'),
    path('', PostQr.as_view()),
]
