# -*- coding: utf-8 -*-
__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

from datetime import datetime
from pydantic import BaseModel, Field, field_validator


def check_iso_8859_2(data: str):
    out = ''
    for char in [ord(char) for char in data]:
        if char in range(128, 159):
            char = 95
        out += chr(char)
    return out


class ListBaseModel(BaseModel):
    @classmethod
    def from_list(cls, tpl):
        return cls(**{k: v for k, v in zip(cls.__fields__.keys(), tpl)})


class UpnBaseModel(ListBaseModel):
    slog: str = Field(default='UPNQR')
    iban: str = Field(default='')
    polog: str = Field(default='')
    dvig: str = Field(default='')
    referenca_placnika: str = Field(default='')
    ime_placnika: str = Field(default='', required=True, max_length=33)
    ulica_placnika: str = Field(default='', required=True, max_length=33)
    kraj_placnika: str = Field(default='', required=True, max_length=33)
    znesek: float = Field(default=0.0)
    datum_placila: str = Field(default='')
    nujno: str = Field(default='')
    koda_namena: str = Field(default='', required=True, max_length=4)
    namen_placila: str = Field(default='', required=True, max_length=42)
    rok_placila: str = Field(default='')
    iban_prejemnika: str = Field(default='', required=True, max_length=34)
    referenca: str = Field(default='', required=True, max_length=26)
    ime_prejemnika: str = Field(default='', required=True, max_length=42)
    ulica_prejemnika: str = Field(default='', required=True, max_length=33)
    kraj_prejemnika: str = Field(default='', required=True, max_length=33)
    kontrolna_vsota: str = Field(default='', required=True, max_length=3)

    @field_validator('slog')
    @classmethod
    def parse_slog(cls, v):
        if v != 'UPNQR':
            raise ValueError('Invalid slog')
        return v

    @field_validator('znesek')
    @classmethod
    def parse_znesek(cls, v):
        amount = int(v)/100
        # If amount is 0 or empty, set minimum valid EPC amount (0.01 EUR)
        # This is common for charity payments where user chooses the amount
        if amount == 0 or not v:
            return 0.01
        return amount

    @field_validator('rok_placila')
    @classmethod
    def parse_datum_placila(cls, v: str):
        if not v:
            return ''
        try:
            ts = datetime.strptime(v, '%d.%m.%Y')
        except ValueError:
            raise ValueError('Invalid datum_placila')
        return ts

    @field_validator('referenca')
    @classmethod
    def parse_referenca(cls, v: str):
        return f'{v[:4]} {v[4:]}'

    @field_validator('ime_prejemnika', 'ulica_placnika', 'kraj_placnika', 'kraj_prejemnika',
                     'ulica_prejemnika', 'namen_placila')
    @classmethod
    def parse_ime_prejemnika(cls, v: str):
        return check_iso_8859_2(v)
