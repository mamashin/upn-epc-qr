# -*- coding: utf-8 -*-
__author__ = "Nikolay Mamashin (mamashin@gmail.com)"

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import UpnModel


class QrForm(forms.Form):
    decodedText = forms.CharField(label="Text", required=True)
    result = forms.JSONField(label="Result", required=True)


class QrManualForm(forms.ModelForm):
    # template_name_div = "custom_form_div.html"
    # error_css_class = "error"

    class Meta:
        model = UpnModel
        fields = ["ime_prejemnika", "iban_prejemnika", "znesek", "referenca", "data_type"]

        labels = {
            "ime_prejemnika": _("Recipient’s name"),
            "iban_prejemnika": _("Recipient’s IBAN"),
            "znesek": _("Amount"),
            "referenca": _("Recipient’s reference")
        }
        widgets = {
            "ime_prejemnika": forms.TextInput(attrs={"placeholder": _("Bank Association of Slovenia-GIZ")}),
            "iban_prejemnika": forms.TextInput(attrs={"placeholder": _("SI56 0203 6025 3863 406")}),
            "znesek": forms.NumberInput(attrs={"placeholder": "0,00"}),
            "referenca": forms.TextInput(attrs={"placeholder": _("SI08 1236-17-345679")}),
            "data_type": forms.HiddenInput(),  # Make data_type hidden
        }
