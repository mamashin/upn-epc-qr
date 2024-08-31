# -*- coding: utf-8 -*-

__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

import json
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.generic import CreateView, TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from decouple import config  # noqa
from django.db.models.expressions import F
from loguru import logger
from result import Result, is_ok, is_err
from django import forms
from django.shortcuts import render
from django_htmx.http import retarget, push_url

from .epc import generate_qr_code
from .forms import QrForm, QrManualForm
from .services import create_upn_model
from .models import UpnModel


class PostQr(TemplateView):
    template_name = "main.html"

    def post(self, request, *args, **kwargs):
        if request.htmx:
            create_result = create_upn_model(request.POST)
            if is_ok(create_result):
                self.extra_context = {"img": create_result.value["img"],
                                      "model": create_result.value["model"],
                                      "mode": "qr"}
                return push_url(render(request, "qr_ok.html", self.get_context_data()),
                                f"/qr/{create_result.value['model'].rnd}/")
            else:
                logger.error(f'Error create_upn_model: {create_result.err}')
                return render(request, "qr_error.html", self.get_context_data())

        return render(request, self.template_name, self.get_context_data())


class PostManualForm(TemplateView):
    template_name = "main.html"

    def post(self, request, *args, **kwargs):
        if request.htmx:
            form = QrManualForm(request.POST)
            manual_qr_edit = request.POST.get("qr_edit_form", None)
            model = None
            if manual_qr_edit:
                model = UpnModel.objects.filter(rnd=manual_qr_edit).first()
                model.data_type = "qr_edit"

            if form.is_valid():
                if not model:
                    model = form.save()
                else:
                    QrManualForm(request.POST, instance=model).save()
                qr_img = generate_qr_code(model)
                if is_err(qr_img):
                    logger.error(f'Error generate_qr_code: {qr_img.err}')
                    result = render(request, "qr_error.html", {"qr_create_error": qr_img.err})
                    return retarget(result, '#main')

                result = render(request, "qr_ok.html",
                                {"mode": "qr", "show_form": False, "form": form, 'model': model,
                                 'img': qr_img.value})
                return push_url(retarget(result, '#main'), f"/qr/{model.rnd}/")
            else:  # Not valid form
                # template = "only_form.html" if manual_qr_edit else "form_manual.html"
                template = "form_manual.html"
                mode = "qr" if manual_qr_edit else "manual"
                logger.info(f'Mode: {mode}')
                return retarget(render(request, template, {"mode": mode, "show_form": True, "form": form,
                                                           "model": model}), '#main')

        return render(request, self.template_name, self.get_context_data())


class GetSaveQr(TemplateView):
    template_name = "qr_open.html"

    def get(self, request, *args, **kwargs):
        img, mode, show_form = "", "", False  # Initial values
        exist_model = UpnModel.objects.filter(rnd=kwargs.get("rnd_id")).first()
        if exist_model:
            img = generate_qr_code(exist_model)
            mode = "qr"
            if is_err(img):
                exist_model, mode, show_form = None, None, True
            else:
                img = img.value
        response = render(request,
                          self.template_name,
                          {"mode": mode, "show_form": show_form, "model": exist_model, "img": img,
                           "direct_get": True})
        return response
