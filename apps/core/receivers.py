# -*- coding: utf-8 -*-

__author__ = 'Nikolai Mamashin (mamashin@gmail.com)'

from django.conf import settings
from django.db.models.signals import post_save, post_delete, pre_save, m2m_changed, pre_delete
from django.dispatch import receiver

