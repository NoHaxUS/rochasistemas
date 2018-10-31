from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
import datetime, os, subprocess


class UpdaterConfig(AppConfig):
    name = 'updater'
    verbose_name = 'Website Updater'


    def ready(self):
        from .up import start_update, start_consuming_updates
        scheduler = BackgroundScheduler()
        start_date = datetime.datetime.now() + datetime.timedelta(minutes=100)
        #start_date = datetime.datetime.now() + datetime.timedelta(seconds=10)
        scheduler.add_job(start_update, 'interval', minutes=100, start_date=start_date)
        scheduler.start()
        #subprocess.Popen('python up.py', shell=True)
