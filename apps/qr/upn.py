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
    ime_placnika: str = Field(default='')
    ulica_placnika: str = Field(default='')
    kraj_placnika: str = Field(default='')
    znesek: float = Field(default=0.0)
    datum_placila: str = Field(default='')
    nujno: str = Field(default='')
    koda_namena: str = Field(default='')
    namen_placila: str = Field(default='')
    rok_placila: str = Field(default='')
    iban_prejemnika: str = Field(default='')
    referenca: str = Field(default='')
    ime_prejemnika: str = Field(default='')
    ulica_prejemnika: str = Field(default='')
    kraj_prejemnika: str = Field(default='')
    kontrolna_vsota: str = Field(default='')

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
        # If the amount is 0 or empty, set a minimum valid EPC amount (0.01 EUR)
        # This is common for charity payments where the user chooses the amount
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

    @field_validator('ime_placnika', 'ulica_placnika', 'kraj_placnika')
    @classmethod
    def parse_placnik_fields(cls, v: str):
        """Truncate to 45 (standard is 33!) chars and clean ISO-8859-2"""
        cleaned = check_iso_8859_2(v)
        return cleaned[:45] if len(cleaned) > 45  else cleaned

    @field_validator('ime_prejemnika')
    @classmethod
    def parse_ime_prejemnika(cls, v: str):
        """Truncate to 42 chars and clean ISO-8859-2"""
        cleaned = check_iso_8859_2(v)
        return cleaned[:42] if len(cleaned) > 42 else cleaned

    @field_validator('ulica_prejemnika', 'kraj_prejemnika')
    @classmethod
    def parse_prejemnik_address_fields(cls, v: str):
        """Truncate to 33 chars and clean ISO-8859-2"""
        cleaned = check_iso_8859_2(v)
        return cleaned[:33] if len(cleaned) > 33 else cleaned

    @field_validator('namen_placila')
    @classmethod
    def parse_namen_placila(cls, v: str):
        """Truncate to 42 chars and clean ISO-8859-2"""
        cleaned = check_iso_8859_2(v)
        return cleaned[:42] if len(cleaned) > 42 else cleaned
