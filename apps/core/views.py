# -*- coding: utf-8 -*-
__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

import json
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.generic import CreateView, TemplateView, ListView, DetailView
from decouple import config
from loguru import logger
from django.shortcuts import render
from django_htmx.http import HttpResponseClientRefresh, trigger_client_event

from apps.qr.forms import QrManualForm
from apps.qr.models import UpnModel

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

    def get(self, request, *args, **kwargs):
        if request.htmx:
            if mode := request.GET.get("mode"):
                if mode == "stop":
                    form = QrManualForm()
                    form.fields["data_type"].initial = "form"
                    response = render(request, "form_manual.html",
                                      {"mode": "manual", "show_form": True, "form": form})
                    return response

                if mode == "start":
                    response = render(request, "form_manual.html",
                                      {"mode": "scan", "show_form": False})
                    return response

                if mode == "edit":
                    rnd = request.GET.get("rid")
                    logger.info(f"Edit: {rnd}")
                    edit_model = UpnModel.objects.filter(rnd=rnd).first()
                    edit_model.data_type = "qr_edit"
                    response = render(request, "only_form.html",
                                      {"mode": "qr", "show_form": True, 'model': edit_model,
                                       "form": QrManualForm(instance=edit_model)})
                    return response
        else:
            return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        logger.info("MainPage POST")
        logger.debug(request.body)

        return render(request, self.template_name, self.get_context_data())
