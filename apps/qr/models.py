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
from django.utils.translation import gettext_lazy as _


def rnd(rnd_len: int = 6) -> str:
    return f'%0{rnd_len}x' % random.randrange(16**rnd_len)  # noqa


def md5_hash(model: models.Model) -> str:
    """
    Calculate MD5 hash of the model instance
    """
    md5_pass_fields_list = ['id', 'md5', 'rnd', 'data_type', 'created', 'modified']
    fields = [f.name for f in model._meta.get_fields() if f.name not in md5_pass_fields_list]
    data = {f: getattr(model, f) for f in fields}
    return hashlib.md5(json.dumps(data, sort_keys=True, cls=DjangoJSONEncoder).encode('utf-8')).hexdigest()


def validate_iban(value) -> None:
    pattern = r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$'
    match = re.match(pattern, value.replace(' ', ''))
    if not match:
        raise ValidationError(
            _('IBAN must start with 2 letters followed by digits'),
            params={'value': value},
        )


def validate_znesek(value) -> None:
    if value < 0.01 or 999999.99 < value:
        raise ValidationError(
            _('The amount cannot be less than 0.01 and more than 999999.99'),
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
    ime_prejemnika = models.CharField(max_length=42)
    ulica_prejemnika = models.CharField(max_length=33, blank=True)
    kraj_prejemnika = models.CharField(max_length=33, blank=True)
    kontrolna_vsota = models.CharField(max_length=3, blank=True)

    md5 = models.CharField(max_length=32, blank=False, null=False, unique=True)
    rnd = models.CharField(max_length=6, blank=False, null=False, unique=True, default=rnd)
    data_type = models.CharField(choices=[('qr', 'UPN QR'), ('qr_edit', 'UPN edit'), ('form', 'Form'), ('form_full', 'Form Full')],
                                 default='qr', max_length=10, verbose_name='')

    class Meta:
        verbose_name = 'UPN QR'
        verbose_name_plural = 'UPN QR'

    def __str__(self):
        return f'{self.ime_placnika} / {self.ime_prejemnika}'

    @property
    def md5_sum(self):
        return md5_hash(self)

    def calculate_kontrolna_vsota(self) -> str:
        """
        Calculate control sum (field 20) according to UPN QR standard.
        Control sum = sum of lengths of fields 1-19 including '\n' after each field.

        Returns:
            str: 3-digit string with leading zeros (e.g., "252")
        """
        # Helper function to get field value or empty string
        def get_field_value(value) -> str:
            if value is None:
                return ""
            if isinstance(value, float):
                # Convert amount to cents (e.g., 100.50 -> "00000010050")
                return f"{int(value * 100):011d}"
            if isinstance(value, str):
                return value
            return str(value)

        # Format date field (DD.MM.YYYY or empty)
        rok_placila_str = ""
        if self.rok_placila:
            rok_placila_str = self.rok_placila.strftime("%d.%m.%Y")

        # Build array of 19 fields according to UPN QR standard
        fields = [
            "UPNQR",                              # 1. Leading style
            "",                                    # 2. Payer's IBAN (empty for form)
            "",                                    # 3. Deposit (empty)
            "",                                    # 4. Withdrawal (empty)
            "",                                    # 5. Payer's reference (empty)
            get_field_value(self.ime_placnika),   # 6. Payer's name
            get_field_value(self.ulica_placnika), # 7. Payer's street
            get_field_value(self.kraj_placnika),  # 8. Payer's city
            get_field_value(self.znesek),         # 9. Amount (in cents)
            "",                                    # 10. Payment date (empty)
            "",                                    # 11. Urgent (empty)
            get_field_value(self.koda_namena),    # 12. Purpose code
            get_field_value(self.namen_placila),  # 13. Purpose of payment
            rok_placila_str,                       # 14. Payment deadline
            get_field_value(self.iban_prejemnika).replace(" ", ""),  # 15. Recipient's IBAN
            get_field_value(self.referenca),      # 16. Recipient's reference
            get_field_value(self.ime_prejemnika), # 17. Recipient's name
            get_field_value(self.ulica_prejemnika), # 18. Recipient's street
            get_field_value(self.kraj_prejemnika),  # 19. Recipient's city
        ]

        # Calculate total length including '\n' after each field
        total_length = sum(len(field) + 1 for field in fields)  # +1 for '\n'

        # Return as 3-digit string with leading zeros
        return f"{total_length:03d}"

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
        created = self._state.adding

        # Auto-calculate kontrolna_vsota for form_full type
        if self.data_type == 'form_full':
            self.kontrolna_vsota = self.calculate_kontrolna_vsota()
            logger.debug(f"Auto-calculated kontrolna_vsota: {self.kontrolna_vsota} for {self.data_type}")

        # Check for duplicate MD5, but exclude current record when updating
        duplicate_check = UpnModel.objects.filter(md5=self.md5_sum)
        if not created and self.pk:
            duplicate_check = duplicate_check.exclude(pk=self.pk)

        if duplicate_check.first():
            return

        self.md5 = self.md5_sum

        if not created:
            self.rnd = UpnModel.objects.filter(rnd=self.rnd).first().rnd

        super().save(*args, **kwargs)
