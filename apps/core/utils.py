# -*- coding: utf-8 -*-

__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

from decouple import config
import requests
from pathlib import Path
import json
import math
from redis import Redis
from rq import Queue
import requests
from django_rq import job
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import datetime
from loguru import logger


def dictor(data, path=None, default=None, checknone=False, ignorecase=False):
    """"
    Usage:
    get a value from a Dictionary key
    > dictor(data, "employees.John Doe.first_name")
    parse key index and fallback on default value if None,
    > dictor(data, "employees.5.first_name", "No employee found")
    pass a parameter
    > dictor(data, "company.{}.address".format(my_company))
    if using Python 3, can use F-strings to pass parameter
    > param = 'MyCompany'
    > dictor(data, f"company.{param}.address")
    lookup a 3rd element of List, on second key, lookup index=5
    > dictor(data, "3.first.second.5")
    lookup a nested list of lists
    > dictor(data, "0.first.1.2.second.third.0.2"
    check if return value is None, if it is, raise an error
    > dictor(data, "some.key.value", checknone=True)
    > ValueError: value not found for search path: "some.key.value"
    ignore letter casing when searching
    > dictor(data, "employees.Fred Flintstone", ignorecase=True)
    """

    if path is None or path == '':
        return json.dumps(data)

    # handle keys with dots in them
    if r'\.' in path:
        path = path.replace(r'\.', '__dictor__')

    keys = path.split(".")

    if ignorecase:
        data = {k.lower(): v for k, v in data.items()}

    for i in range(len(keys)):
        key = keys[i]
        try:
            if key.isdigit():
                val = data[int(key)]
            else:
                if ignorecase:
                    key = key.lower()

                if '__dictor__' in key:
                    key = key.replace('__dictor__', '.')

                try:
                    val = data[key]
                except (KeyError, ValueError, IndexError, TypeError):
                    if checknone:
                        val = False
                        break
                    val = default
                    break

            data = val
        except (KeyError, ValueError, IndexError, TypeError):
            val = default

    if checknone:
        if not val or val == default:
            raise ValueError('value not found for search path: "%s"' % path)
    return val


def test_job():
    logger.info(f"Run cron job at {datetime.datetime.now()}")
    return "All ik OK !"
