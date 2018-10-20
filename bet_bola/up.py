import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from updater.up import start_consuming_updates
start_consuming_updates()
