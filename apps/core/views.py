# -*- coding: utf-8 -*-
__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

import json
from loguru import logger
from decouple import config # noqa

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.views.generic import CreateView, TemplateView, ListView, DetailView
from django.shortcuts import render
from django_htmx.http import push_url, HttpResponseClientRefresh, trigger_client_event, HttpResponseClientRedirect, HttpResponseLocation
from result import is_err

from apps.qr.epc import generate_qr_code
from apps.qr.forms import QrManualForm, QrFullForm
from apps.qr.models import UpnModel


@require_GET
def favicon(request) -> HttpResponse:
    return HttpResponse(
        (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            + '<text y=".9em" font-size="90">🧾</text>'
            + '</svg>'
        ),
        content_type="image/svg+xml",
    )


class MainPage(TemplateView):
    template_name = "main.html"
    context_object_name = "result"
    http_method_names = ["get", ]

    def get(self, request, *args, **kwargs):
        if request.htmx:
            if mode := kwargs.get("mode", None):
                if mode == "manual":  # Fill form manually (HTMX mode)
                    form = QrManualForm()
                    form.fields["data_type"].initial = "form"
                    # render with nav.html !
                    response = render(request, "form_manual.html",
                                      {"mode": "manual", "show_form": True, "form": form, "form_type": "simple"})
                    return response

                if mode == "scan":  # Scan QR code (HTMX mode)
                    response = render(request, "form_manual.html",
                                      {"mode": "scan", "show_form": False})
                    return response

                if mode == "edit":  # Manual edit existing QR code (HTMX mode)
                    rnd = kwargs.get("rnd_id")
                    # info(f"Edit: {loggerrnd}")
                    edit_model = UpnModel.objects.filter(rnd=rnd).first()
                    edit_model.data_type = "qr_edit"
                    response = render(request, "only_form.html",
                                      {"mode": "qr", "show_form": True, 'model': edit_model,
                                       "form": QrFullForm(instance=edit_model), "form_type": "full"})

                    return push_url(response, f"/qr/{rnd}/edit/")

                if mode == "lang":
                    lang = request.GET.get("lang", "en")
                    prev_path = request.GET.get("prev_path", "/")
                    response = HttpResponseClientRedirect(f'{prev_path}')
                    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang, max_age=60 * 60 * 24 * 365)
                    return response

        if kwargs.get("mode") == "scan":  # Direct GET
            response = render(request, self.template_name,
                              {"mode": "scan", "show_form": False, "direct_get": True})
            return response

        if kwargs.get("mode") == "manual":  # Direct GET
            form = QrManualForm()
            form.fields["data_type"].initial = "form"
            response = render(request, self.template_name,
                              {"mode": "manual", "show_form": True, "form": form, "form_type": "simple", "direct_get": True})
            return response

        if kwargs.get("mode") == "edit":  # Direct GET
            rnd = kwargs.get("rnd_id")
            # logger.info(f"Edit: {rnd}")
            edit_model = UpnModel.objects.filter(rnd=rnd).first()
            # logger.info(f"Edit model: {edit_model}")
            if not edit_model:
                return render(request, "qr_open.html", {"mode": None})
            edit_model.data_type = "qr_edit"
            img = generate_qr_code(edit_model)
            if is_err(img):
                edit_model, mode, show_form = None, None, True
            else:
                img = img.value
            response = render(request, "qr_open.html",
                              {"mode": "qr", "show_form": True, 'model': edit_model, "direct_get": True,
                               "form": QrFullForm(instance=edit_model), "form_type": "full", "img": img})
            return response

        else:
            return render(request, self.template_name, self.get_context_data())
