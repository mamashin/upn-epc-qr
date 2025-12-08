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
from urllib.parse import quote

from .epc import generate_qr_code
from .forms import QrForm, QrManualForm
from .services import create_upn_model
from .models import UpnModel
from .pdf_generator import UpnPdfGenerator


class PostQr(TemplateView):
    template_name = "main.html"

    def post(self, request, *args, **kwargs):
        if request.htmx:
            create_result = create_upn_model(request.POST)
            if is_ok(create_result):
                self.extra_context = {"img": create_result.value["img"],
                                      "model": create_result.value["model"],
                                      "mode": "qr",
                                      "amount_was_auto_set": create_result.value.get("amount_was_auto_set", False)}
                return push_url(render(request, "qr_ok.html", self.get_context_data()),
                                f"/qr/{create_result.value['model'].rnd}/")
            else:
                logger.error(f'Error create_upn_model: {create_result.err}')
                # self.extra_context = {"mode": "qr"}
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


class DownloadPdfView(TemplateView):
    """View for downloading UPN QR document as PDF"""

    def get(self, request, *args, **kwargs):
        rnd_id = kwargs.get("rnd_id")
        upn_model = UpnModel.objects.filter(rnd=rnd_id).first()

        if not upn_model:
            logger.error(f'PDF download: Model not found for rnd={rnd_id}')
            return HttpResponse("QR code not found", status=404)

        # Only allow PDF download for scanned QR codes (qr or qr_edit), not for manually created forms
        if upn_model.data_type == 'form':
            logger.warning(f'PDF download attempted for manually created form: rnd={rnd_id}')
            return HttpResponse("PDF download is only available for scanned invoices", status=403)

        try:
            # Get PDF settings from query parameters
            position = request.GET.get('position', 'top')  # 'top' or 'bottom'
            draw_template = request.GET.get('template', '1') == '1'  # '1' = True, '0' = False

            # Validate position parameter
            if position not in ['top', 'bottom']:
                position = 'top'

            logger.info(f'PDF download settings: position={position}, draw_template={draw_template}')

            # Generate PDF with custom settings
            generator = UpnPdfGenerator(position=position, draw_template=draw_template)
            pdf_bytes = generator.generate(upn_model)

            # Generate filename
            filename = UpnPdfGenerator.generate_filename(upn_model)

            # Create response with proper Content-Disposition header for non-ASCII filenames
            # Use RFC 2231/5987 encoding: filename (ASCII fallback) + filename* (UTF-8)
            response = HttpResponse(pdf_bytes, content_type='application/pdf')

            # ASCII fallback - remove non-ASCII characters
            ascii_filename = filename.encode('ascii', 'ignore').decode('ascii')

            # UTF-8 encoded filename
            encoded_filename = quote(filename)

            # Set both filename (ASCII fallback) and filename* (UTF-8)
            response['Content-Disposition'] = f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}'

            logger.info(f'PDF generated successfully for rnd={rnd_id}, filename={filename}')
            return response

        except Exception as e:
            logger.error(f'Error generating PDF for rnd={rnd_id}: {str(e)}')
            return HttpResponse(f"Error generating PDF: {str(e)}", status=500)
