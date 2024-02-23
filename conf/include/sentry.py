# -*- coding: utf-8 -*-
__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

from decouple import config # noqa
from conf.settings import DEBUG

SENTRY_DSN = config("SENTRY_DSN", cast=str, default="")

if not DEBUG and SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.httpx import HttpxIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    def strip_transactions(event, hint):  # type: ignore
        if event["transaction"] in (
            "/admin/jsi18n/",
        ):
            return None

        return event

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration(), HttpxIntegration()],
        traces_sample_rate=0.8,
        send_default_pii=True,
        before_send_transaction=strip_transactions,
    )
