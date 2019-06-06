import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from updater.update_betsapi import get_upcoming_events
from updater.process_results_betsapi import process_results

get_upcoming_events()
# process_results()
