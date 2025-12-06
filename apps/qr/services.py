# -*- coding: utf-8 -*-
__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

from django.utils import timezone
from loguru import logger
from result import Result, Err, Ok, is_err
import hashlib
import json

from .epc import generate_qr_code
from .models import UpnModel
from .upn import UpnBaseModel
from .forms import QrForm, QrManualForm


def create_md5_hash(data) -> str:
    return hashlib.md5(data).hexdigest()


def create_upn_model(form_data: str) -> Result:
    """
    form_data is request.POST bytes - 'decodedText': str, 'result': { json }
    decodedText looks like  "UPNQR\n\n\n\n\nIME MARIO\nMAŠERA-SPASIĆEVA ULICA 1\n1000 LJUBLJANA\n...."
    """
    qr_form_data = QrForm(form_data)
    if qr_form_data.is_valid():
        try:
            # Convert decodedText to list (\n - separator)
            qr_form_data_list = qr_form_data.cleaned_data['decodedText'].split('\n')
        except Exception as e:
            return Err(f'Error split decodedText data - {e}')

        if len(qr_form_data_list) != 20:  # UPN has 20 fields !
            return Err('Wrong list length')

        # Check if original amount was zero (field #8 in UPN format)
        original_amount_cents = int(qr_form_data_list[8]) if qr_form_data_list[8] else 0
        amount_was_zero = original_amount_cents == 0

        try:
            # Convert list to Upn pydantic model
            upn_base_model = UpnBaseModel.from_list(qr_form_data_list)
        except Exception as e:
            return Err(f'Error convert to BaseModel model - {e}')

        try:
            # Dump BaseModel to dict, correct rok_placila to timezone aware, create md5 hash for unique model
            upn_base_model_dict = upn_base_model.model_dump(warnings=False)
            if upn_base_model_dict['rok_placila']:
                upn_base_model_dict['rok_placila'] = timezone.make_aware(upn_base_model_dict['rok_placila'])
            else:
                # If rok_placila is empty, set next day at 00:00:00 to avoid duplicates
                # All invoices scanned on the same day without deadline will have same rok_placila
                from datetime import datetime, timedelta
                tomorrow = datetime.now() + timedelta(days=1)
                tomorrow_midnight = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
                upn_base_model_dict['rok_placila'] = timezone.make_aware(tomorrow_midnight)
            # logger.warning(json.dumps(upn_base_model.model_dump_json(warnings=False),
            #                                                         sort_keys=True).encode('utf-8'))
            # logger.warning(upn_base_model.model_dump())
            # upn_base_model_dict['md5'] = create_md5_hash(json.dumps(upn_base_model.model_dump_json(warnings=False),
            #                                                         sort_keys=True).encode('utf-8'))
        except Exception as e:
            return Err(f'Error parse UpnModel BaseModel - {e}')

        upn_model = UpnModel.fill(**upn_base_model_dict)
        upn_model_exist = UpnModel.objects.filter(md5=upn_model.md5_sum).first()
        if upn_model_exist:
            upn_model = upn_model_exist
        else:
            try:
                upn_model.save()
            except Exception as e:
                return Err(f'Error create UpnModel - {e}')

        qr_img = generate_qr_code(upn_model)
        if is_err(qr_img):
            return Err(f'Error generate QR code - {qr_img.err}')

        return Ok({
            'model': upn_model,
            'img': qr_img.value,
            'amount_was_auto_set': amount_was_zero
        })
