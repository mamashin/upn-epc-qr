# -*- coding: utf-8 -*-

__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

from django.contrib.auth.middleware import RemoteUserMiddleware
from django.contrib.auth.backends import RemoteUserBackend
from ipware import get_client_ip  # type: ignore


class CustomRemoteUserMiddleware(RemoteUserMiddleware):
    # header = 'HTTP_AUTHUSER'
    header = 'REMOTE_USER'


class CustomRemoteUserBackend(RemoteUserBackend):
    create_unknown_user = False


def real_ip_middleware(get_response):  # type: ignore
    """Set REMOTE_ADDR for ip guessed by django-ipware.
    We need this to make sure all apps using remote ip are usable behind any kind of
    reverse proxy.
    If this does not work as you exepcted, check out django-ipware docs to configure it
    for your local needs: https://github.com/un33k/django-ipware
    """

    def middleware(request):  # type: ignore
        request.META["REMOTE_ADDR"] = get_client_ip(request)[0]

        return get_response(request)

    return middleware
