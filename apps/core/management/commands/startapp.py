# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.management.commands.startapp import Command as BaseCommand


class Command(BaseCommand):
    def handle(self, **options):
        directory = settings.BASE_DIR / "apps" / options["name"]
        directory.mkdir()

        options.update(directory=str(directory))
        print(f"⚠️ Creating {options['name']} app in {options['directory']}...\n"
              f"Don't forget to edit INSTALLED_APPS as apps.{options['name']}\n"
              f"And change in apps.py name = 'apps.{options['name']}'\n")

        super().handle(**options)
