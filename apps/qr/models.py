import hashlib
import re

from django.db import models
from loguru import logger
import random
import json

from apps.core.models import TimestampedModel
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_datetime
from django.core.serializers.json import DjangoJSONEncoder


def rnd(rnd_len: int = 6):
    return f'%0{rnd_len}x' % random.randrange(16**rnd_len)


def md5_hash(model: models.Model):
    md5_pass_fields_list = ['id', 'md5', 'rnd', 'data_type', 'created', 'modified']
    fields = [f.name for f in model._meta.get_fields() if f.name not in md5_pass_fields_list]
    data = {f: getattr(model, f) for f in fields}
    return hashlib.md5(json.dumps(data, sort_keys=True, cls=DjangoJSONEncoder).encode('utf-8')).hexdigest()


def validate_iban(value):
    pattern = r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$'
    match = re.match(pattern, value.replace(' ', ''))
    if not match:
        raise ValidationError(
            'IBAN должен начинаться с 2х букв и далее цифры',
            params={'value': value},
        )


def validate_znesek(value):
    if value < 0.01 or 999999.99 < value:
        raise ValidationError(
            ' Сумма не может быть меньше 0.01 и больше 999999,99',
            params={'value': value},
        )

# DB Model for Telegram users
class UpnModel(TimestampedModel):
    ime_placnika = models.CharField(max_length=33, blank=True)
    ulica_placnika = models.CharField(max_length=33, blank=True)
    kraj_placnika = models.CharField(max_length=33, blank=True)
    znesek = models.FloatField(blank=False, null=False, max_length=10, validators=[validate_znesek])
    koda_namena = models.CharField(max_length=4, blank=True)
    namen_placila = models.CharField(max_length=42, blank=True)
    rok_placila = models.DateTimeField(null=True, blank=True, default=None)
    iban_prejemnika = models.CharField(max_length=34, validators=[validate_iban])
    referenca = models.CharField(max_length=26)
    ime_prejemnika = models.CharField(max_length=33)
    ulica_prejemnika = models.CharField(max_length=33, blank=True)
    kraj_prejemnika = models.CharField(max_length=33, blank=True)
    kontrolna_vsota = models.CharField(max_length=3, blank=True)

    md5 = models.CharField(max_length=32, blank=False, null=False, unique=True)
    rnd = models.CharField(max_length=6, blank=False, null=False, unique=True, default=rnd)
    data_type = models.CharField(choices=[('qr', 'UPN QR'), ('qr_edit', 'UPN edit'), ('form', 'Form')],
                                 default='qr', max_length=10)

    class Meta:
        verbose_name = 'UPN QR'
        verbose_name_plural = 'UPN QR'

    def __str__(self):
        return f'{self.ime_placnika} / {self.ime_prejemnika}'

    @property
    def md5_sum(self):
        return md5_hash(self)

    @classmethod
    def create(cls, **kwargs):
        # Filter out non-existent fields
        valid_fields = {f.name for f in cls._meta.get_fields()}
        kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}
        return cls.objects.create(**kwargs)

    @classmethod
    def fill(cls, **kwargs):
        # Filter out non-existent fields
        valid_fields = {f.name for f in cls._meta.get_fields()}
        kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}
        return cls(**kwargs)

    def save(self, *args, **kwargs):
        logger.info('save!')
        created = self._state.adding
        if UpnModel.objects.filter(md5=self.md5_sum).first():
            return

        self.md5 = self.md5_sum

        if not created:
            self.rnd = UpnModel.objects.filter(rnd=self.rnd).first().rnd

        super().save(*args, **kwargs)
