import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from updater.update_betsapi import get_upcoming_events
get_upcoming_events()
