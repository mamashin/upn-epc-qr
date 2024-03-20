# -*- coding: utf-8 -*-
__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

from django import forms

from .models import UpnModel


class QrForm(forms.Form):
    decodedText = forms.CharField(label='Text', required=True)
    result = forms.JSONField(label='Result', required=True)


class QrManualForm(forms.ModelForm):
    # template_name_div = 'custom_form_div.html'
    # error_css_class = 'error'

    class Meta:
        model = UpnModel
        fields = ['ime_prejemnika', 'iban_prejemnika', 'znesek', 'referenca', 'data_type']

        labels = {
            'ime_prejemnika': 'Имя получателя',
            'iban_prejemnika': 'Счет получателя',
            'znesek': 'Сумма (Znesek)',
            'referenca': 'Назначение платежа'
        }
        widgets = {
            'ime_prejemnika': forms.TextInput(attrs={'placeholder': 'Ime prejemnika'}),
            'iban_prejemnika': forms.TextInput(attrs={'placeholder': 'IBAN prejemnika'}),
            'znesek': forms.NumberInput(attrs={'placeholder': '0,00'}),
            'referenca': forms.TextInput(attrs={'placeholder': 'Referenca'}),
            'data_type': forms.HiddenInput(),  # Make data_type hidden
        }

