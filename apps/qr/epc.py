# -*- coding: utf-8 -*-
__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

from loguru import logger
from segno import helpers
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from result import Result, Err, Ok

from .models import UpnModel


def get_text_dimensions(text_string, font):
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return text_width, text_height


def generate_qr_code(data: UpnModel) -> Result:
    out = io.BytesIO()
    try:
        # Ensure amount is at least 0.01 EUR (EPC standard minimum)
        # This handles charity payments where amount might be 0
        amount = data.znesek if data.znesek >= 0.01 else 0.01

        qr = helpers.make_epc_qr(name=data.ime_prejemnika, iban=data.iban_prejemnika, amount=amount,
                                 text=data.referenca, encoding='UTF-8')
        qr.save(out, scale=15, border=5, kind='png', finder_dark='#209cdf')
        out.seek(0)
        img = Image.open(out)
        img.convert('RGBA')
        draw = ImageDraw.Draw(img)
        font_cost = ImageFont.truetype('static/fonts/iosevka-term-regular.ttf', 50)
        font_descr = ImageFont.truetype('static/fonts/iosevka-term-regular.ttf', 44)

        img_width, img_height = img.size
        text_cost = f'€ {data.znesek:.2f}'
        text_referenca = data.ime_prejemnika
        text_cost_width, _ = get_text_dimensions(text_cost, font_cost)
        text_referenca_width, _ = get_text_dimensions(text_referenca, font_descr)

        draw.text(((img_width/2)-(text_cost_width/2), 10), text_cost, fill='#55a31d', font=font_cost)
        draw.text(((img_width/2)-(text_referenca_width/2), img_height-60), text_referenca, fill='#a1290e',
                  font=font_descr)
        img.resize((640, 640), Image.LANCZOS)

        final_out = io.BytesIO()
        img.save(final_out, format='png')
        final_out.seek(0)
        base64_img = base64.b64encode(final_out.getvalue()).decode("utf-8")
    except Exception as e:
        return Err(f'Error create QR - {e}')

    return Ok(base64_img)
