# -*- coding: utf-8 -*-

__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

from rest_framework import permissions


class SuperuserAccessPermission(permissions.BasePermission):
    message = 'You dont have super power !'

    def has_permission(self, request, view):
        return request.user.is_superuser


class OnlySuperuserRW(permissions.BasePermission):
    message = 'Only superuser have super power !'

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated:
            return request.method in permissions.SAFE_METHODS
