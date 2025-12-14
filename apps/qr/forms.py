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
            "ime_prejemnika": _("Recipient's name"),
            "iban_prejemnika": _("Recipient's IBAN"),
            "znesek": _("Amount"),
            "referenca": _("Recipient's reference")
        }
        widgets = {
            "ime_prejemnika": forms.TextInput(attrs={
                "placeholder": _("Bank Association of Slovenia-GIZ"),
                "class": "active"
            }),
            "iban_prejemnika": forms.TextInput(attrs={
                "placeholder": _("SI56 0203 6025 3863 406"),
                "class": "active"
            }),
            "znesek": forms.NumberInput(attrs={"placeholder": "0,00", "class": "active", "step": "0.01", "min": "0"}),
            "referenca": forms.TextInput(attrs={"placeholder": _("SI08 1236-17-345679"), "class": "active"}),
            "data_type": forms.HiddenInput(),  # Make data_type hidden
        }


class QrFullForm(forms.ModelForm):
    """Full UPN form with all fields for creating complete UPN QR invoices"""

    rok_placila = forms.DateField(
        label=_("Payment deadline"),
        required=False,
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "active"
            },
            format='%Y-%m-%d'
        )
    )

    class Meta:
        model = UpnModel
        fields = [
            # Recipient fields (required: name, IBAN)
            "ime_prejemnika", "iban_prejemnika", "ulica_prejemnika", "kraj_prejemnika",
            # Payment fields (required: amount, purpose code, purpose)
            "znesek", "referenca", "koda_namena", "namen_placila", "rok_placila",
            # Payer fields (required: name for regular payments)
            "ime_placnika", "ulica_placnika", "kraj_placnika",
            # Service field
            "data_type"
        ]

        labels = {
            # Recipient
            "ime_prejemnika": _("Recipient's name"),
            "iban_prejemnika": _("Recipient's IBAN"),
            "ulica_prejemnika": _("Recipient's street"),
            "kraj_prejemnika": _("Recipient's city"),
            # Payment
            "znesek": _("Amount"),
            "referenca": _("Reference"),
            "koda_namena": _("Purpose code"),
            "namen_placila": _("Payment purpose"),
            # Payer
            "ime_placnika": _("Payer's name"),
            "ulica_placnika": _("Payer's street"),
            "kraj_placnika": _("Payer's city")
        }

        widgets = {
            # Recipient
            "ime_prejemnika": forms.TextInput(attrs={
                "placeholder": "Snaga d.o.o.",
                "class": "active"
            }),
            "iban_prejemnika": forms.TextInput(attrs={
                "placeholder": "SI56 0510 0801 0486 080",
                "class": "active"
            }),
            "ulica_prejemnika": forms.TextInput(attrs={
                "placeholder": "Povšetova ulica 6",
                "class": "active"
            }),
            "kraj_prejemnika": forms.TextInput(attrs={
                "placeholder": "1000 Ljubljana",
                "class": "active"
            }),
            # Payment
            "znesek": forms.NumberInput(attrs={
                "placeholder": "14.71",
                "class": "active",
                "step": "0.01",
                "min": "0.01"
            }),
            "referenca": forms.TextInput(attrs={
                "placeholder": "SI12 1033842574531",
                "class": "active"
            }),
            "koda_namena": forms.TextInput(attrs={
                "placeholder": "SCVE",
                "class": "active",
                "maxlength": "4"
            }),
            "namen_placila": forms.TextInput(attrs={
                "placeholder": "Ravn. z odpadki 04/2016 0040098579",
                "class": "active"
            }),
            # Payer
            "ime_placnika": forms.TextInput(attrs={
                "placeholder": "Janez Novak",
                "class": "active"
            }),
            "ulica_placnika": forms.TextInput(attrs={
                "placeholder": "Lepa cesta 10",
                "class": "active"
            }),
            "kraj_placnika": forms.TextInput(attrs={
                "placeholder": "2000 Maribor",
                "class": "active"
            }),
            "data_type": forms.HiddenInput(),
        }
