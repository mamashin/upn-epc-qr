# -*- coding: utf-8 -*-

__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.generic import CreateView, TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from decouple import config
from django.db.models.expressions import F


@require_GET
def favicon(request) -> HttpResponse:
    return HttpResponse(
        (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            + '<text y=".9em" font-size="90">🧾</text>'
            + "</svg>"
        ),
        content_type="image/svg+xml",
    )


class MainPage(TemplateView):
    template_name = "main.html"
    context_object_name = "result"
