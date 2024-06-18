from django.contrib import admin
from django.utils.html import format_html

from apps.qr.models import UpnModel


# Register your models here.
@admin.register(UpnModel)
class UpnModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'ime_placnika', 'ime_prejemnika', 'znesek', 'rok_placila_format', 'created_format',
                    'qr_link', 'data_type')
    readonly_fields = ('created', 'md5', 'modified', 'rnd')
    search_fields = ('ime_placnika', 'ime_prejemnika')

    @staticmethod
    def rok_placila_format(obj):
        if obj.rok_placila:
            return obj.rok_placila.strftime('%d.%m.%y')

    @staticmethod
    def created_format(obj):
        if obj.created:
            return obj.created.strftime('%d.%m.%y %H:%M')

    @staticmethod
    @admin.display(description=format_html(f"<center>QR link</center>"))
    def qr_link(obj):
        return format_html(f"<center><a href='/qr/{obj.rnd}' target='_blank'>{obj.rnd}</a></center>")
